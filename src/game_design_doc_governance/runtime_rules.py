# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime loaders for language-pack and genre-profile audit rules.

The generic genre profile owns rule *types* and references to language-pack
data.  A project profile owns executable project facts.  This module resolves
the former without allowing project facts or executable regexes back into a
shared genre profile.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - reported as a configuration issue
    yaml = None

from .profile_schema import asset_directory


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ValueError("PyYAML is required to load runtime rule assets")
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping")
    return data


def _resolve_reference(data: dict[str, Any], reference: str) -> Any:
    value: Any = data
    for part in reference.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"unknown language-pack reference: {reference}")
        value = value[part]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"language-pack reference must resolve to a string list: {reference}")
    return value


def load_runtime_boundary_checks(profile_data: dict[str, Any], profile_path: str | None) -> tuple[list[dict], list[tuple[str, str]]]:
    """Compile language-pack genre checks for a project audit.

    Returns ``(checks, errors)``.  Each error is a ``(rule, message)`` pair
    intended for a blocking configuration Finding.  No configured runtime
    rule is silently ignored.
    """
    language_pack_ref = profile_data.get("language_pack")
    if not language_pack_ref:
        return [], []
    if not isinstance(language_pack_ref, str):
        return [], [("CONFIG-LANGUAGE-PACK", "language_pack must be a string path or built-in tag")]

    errors: list[tuple[str, str]] = []
    try:
        pack_path = _resolve_language_pack(language_pack_ref, profile_path)
        pack = _load_yaml(pack_path)
        expected_language = (profile_data.get("profile") or {}).get("language")
        if pack.get("schema_version") != 1:
            raise ValueError("language pack schema_version must be 1")
        if pack.get("language") != expected_language:
            raise ValueError(
                f"language pack {pack.get('language')!r} does not match project language {expected_language!r}"
            )
    except (OSError, ValueError, FileNotFoundError) as exc:
        return [], [("CONFIG-LANGUAGE-PACK", str(exc))]

    genre_name = (profile_data.get("profile") or {}).get("genre_profile")
    if not genre_name:
        return [], [("CONFIG-GENRE-PROFILE", "language_pack requires profile.genre_profile")]
    if not isinstance(genre_name, str) or Path(genre_name).name != genre_name:
        return [], [("CONFIG-GENRE-PROFILE", "profile.genre_profile must be a built-in genre profile name")]

    try:
        genre_path = asset_directory("profiles") / "genre" / f"{genre_name.removesuffix('.yaml')}.yaml"
        if not genre_path.is_file():
            raise FileNotFoundError(f"genre profile not found: {genre_name}")
        genre = _load_yaml(genre_path)
    except (OSError, ValueError, FileNotFoundError) as exc:
        return [], [("CONFIG-GENRE-PROFILE", str(exc))]

    project_ids = {
        check.get("id") for check in profile_data.get("boundary_checks", [])
        if isinstance(check, dict) and check.get("id")
    }
    compiled: list[dict] = []
    for raw_check in genre.get("boundary_checks", []):
        if not isinstance(raw_check, dict) or raw_check.get("id") in project_ids:
            continue
        check = deepcopy(raw_check)
        try:
            if check.get("pattern_ref"):
                patterns = _resolve_reference(pack, check.pop("pattern_ref"))
                expression = "(?:" + ")|(?:".join(patterns) + ")"
                try:
                    re.compile(expression)
                except re.error as exc:
                    raise ValueError(f"invalid regular expression for {check.get('id', '(unknown)')}: {exc}") from exc
                check["forbid_regex"] = expression
            if check.get("term_ref"):
                check["forbid_any"] = _resolve_reference(pack, check.pop("term_ref"))
        except ValueError as exc:
            errors.append(("CONFIG-LANGUAGE-REF", f"{check.get('id', '(unknown)')}: {exc}"))
            continue
        if not check.get("forbid_regex") and not check.get("forbid_any"):
            errors.append(("CONFIG-LANGUAGE-REF", f"{check.get('id', '(unknown)')}: no executable language reference"))
            continue
        check.setdefault("level", "P2")
        compiled.append(check)
    return compiled, errors


def _resolve_language_pack(reference: str, profile_path: str | None) -> Path:
    """Resolve a built-in tag or a project-local YAML file safely."""
    built_in = asset_directory("rules") / "language_packs" / f"{reference.removesuffix('.yaml')}.yaml"
    if built_in.is_file():
        return built_in
    if not profile_path:
        raise FileNotFoundError(f"language pack not found: {reference}")
    relative = Path(reference)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("language_pack must be a built-in tag or a project-local path without traversal")
    candidate = Path(profile_path).resolve().parent / relative
    if candidate.suffix != ".yaml":
        candidate = candidate.with_suffix(".yaml")
    if not candidate.is_file():
        raise FileNotFoundError(f"language pack not found: {reference}")
    return candidate

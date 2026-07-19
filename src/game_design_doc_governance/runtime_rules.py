# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime loaders for language-pack and genre-profile audit rules.

The generic genre profile owns rule *types* and references to language-pack
data.  A project profile owns executable project facts.  This module resolves
the former without allowing project facts or executable regexes back into a
shared genre profile.

v2.2: Genre boundary_checks with pattern_ref/term_ref must be covered by
either a project override with the same ID or a resolvable language_pack
reference.  Uncovered rules produce P0 CONFIG-BOUNDARY-COVERAGE instead of
being silently skipped.  Project overrides are validated for executability
before being accepted as coverage.
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


def _empty_coverage() -> dict[str, int]:
    """Return a complete zero-value boundary coverage report."""
    return {
        "total": 0,
        "by_project": 0,
        "by_language_pack": 0,
        "uncovered": 0,
    }


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


def _project_rule_is_executable(rule: dict) -> tuple[bool, str]:
    """Return (True, "") if the project boundary_check has at least one
    non-empty, compilable matcher.  Otherwise (False, reason)."""
    forbid_regex = rule.get("forbid_regex")
    forbid_any = rule.get("forbid_any")

    has_regex = isinstance(forbid_regex, str) and forbid_regex.strip()
    has_terms = isinstance(forbid_any, list) and len(forbid_any) > 0 and all(isinstance(t, str) and t.strip() for t in forbid_any)

    if has_regex:
        try:
            re.compile(forbid_regex)
        except re.error as exc:
            return False, f"forbid_regex is not a valid regular expression: {exc}"

    if not has_regex and not has_terms:
        return False, "neither forbid_regex nor forbid_any is non-empty"

    return True, ""


def load_runtime_boundary_checks(profile_data: dict[str, Any], profile_path: str | None) -> tuple[list[dict], list[tuple[str, str]], dict[str, int]]:
    """Compile language-pack genre checks and verify boundary coverage.

    For each genre boundary_check that carries ``pattern_ref`` / ``term_ref``:

    1. A project ``boundary_checks`` entry with the same ``id`` overrides the
       genre rule — but only if the project rule is *executable* (non-empty
       ``forbid_regex`` or ``forbid_any``, with compilable regex).
    2. When ``language_pack`` is configured and the reference can be resolved,
       the rule is compiled from the language pack.
    3. When a language-pack reference fails to resolve a specific rule, both
       ``CONFIG-LANGUAGE-REF`` and ``CONFIG-BOUNDARY-COVERAGE`` are emitted.
    4. When **neither** a project override nor a resolvable language-pack
       reference exists, including when a same-ID project rule is not
       executable, a P0 ``CONFIG-BOUNDARY-COVERAGE`` error is emitted.

    Returns ``(checks, errors, coverage)`` where ``coverage`` is a dict with:
      * ``total`` — total genre rules with pattern_ref/term_ref
      * ``by_project`` — covered by an executable project boundary_checks override
      * ``by_language_pack`` — compiled from a language pack
      * ``uncovered`` — emitted CONFIG-BOUNDARY-COVERAGE for
    """
    errors: list[tuple[str, str]] = []
    compiled: list[dict] = []

    genre_name = (profile_data.get("profile") or {}).get("genre_profile")
    language_pack_ref = profile_data.get("language_pack")

    if not genre_name:
        if language_pack_ref:
            return [], [("CONFIG-GENRE-PROFILE", "language_pack requires profile.genre_profile")], _empty_coverage()
        return [], [], _empty_coverage()
    if not isinstance(genre_name, str) or Path(genre_name).name != genre_name:
        return [], [("CONFIG-GENRE-PROFILE", "profile.genre_profile must be a built-in genre profile name")], _empty_coverage()

    try:
        genre_path = asset_directory("profiles") / "genre" / f"{genre_name.removesuffix('.yaml')}.yaml"
        if not genre_path.is_file():
            raise FileNotFoundError(f"genre profile not found: {genre_name}")
        genre = _load_yaml(genre_path)
    except (OSError, ValueError, FileNotFoundError) as exc:
        return [], [("CONFIG-GENRE-PROFILE", str(exc))], _empty_coverage()

    genre_rules = [
        rc for rc in genre.get("boundary_checks", [])
        if isinstance(rc, dict) and (rc.get("pattern_ref") or rc.get("term_ref"))
    ]
    if not genre_rules:
        return [], [], _empty_coverage()

    project_checks_by_id: dict[str, dict] = {
        check.get("id"): check
        for check in profile_data.get("boundary_checks", [])
        if isinstance(check, dict) and check.get("id")
    }
    pack = None
    pack_loadable = False

    if language_pack_ref:
        if not isinstance(language_pack_ref, str):
            errors.append(("CONFIG-LANGUAGE-PACK", "language_pack must be a string path or built-in tag"))
        else:
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
                pack_loadable = True
            except (OSError, ValueError, FileNotFoundError) as exc:
                errors.append(("CONFIG-LANGUAGE-PACK", str(exc)))

    coverage = _empty_coverage()
    coverage["total"] = len(genre_rules)

    for raw_check in genre_rules:
        rule_id = raw_check.get("id", "(unknown)")

        refs = []
        if raw_check.get("pattern_ref"):
            refs.append(f"pattern_ref={raw_check['pattern_ref']}")
        if raw_check.get("term_ref"):
            refs.append(f"term_ref={raw_check['term_ref']}")
        ref_str = ", ".join(refs)

        if rule_id in project_checks_by_id:
            project_rule = project_checks_by_id[rule_id]
            executable, reason = _project_rule_is_executable(project_rule)
            if executable:
                coverage["by_project"] += 1
                continue
            msg = (
                f"Genre rule '{rule_id}' ({raw_check.get('type', '')}) with {ref_str} "
                f"has a project boundary_check with the same id but it is not executable: {reason}"
            )
            errors.append(("CONFIG-BOUNDARY-COVERAGE", msg))
            coverage["uncovered"] += 1
            continue

        if pack_loadable:
            check = deepcopy(raw_check)
            try:
                if check.get("pattern_ref"):
                    patterns = _resolve_reference(pack, check.pop("pattern_ref"))
                    expression = "(?:" + ")|(?:".join(patterns) + ")"
                    try:
                        re.compile(expression)
                    except re.error as exc:
                        raise ValueError(f"invalid regular expression for {rule_id}: {exc}") from exc
                    check["forbid_regex"] = expression
                if check.get("term_ref"):
                    check["forbid_any"] = _resolve_reference(pack, check.pop("term_ref"))
            except ValueError as exc:
                errors.append(("CONFIG-LANGUAGE-REF", f"{rule_id}: {exc}"))
                errors.append(("CONFIG-BOUNDARY-COVERAGE",
                    f"Genre rule '{rule_id}' ({raw_check.get('type', '')}) with {ref_str} "
                    f"could not be resolved from language_pack: {exc}"))
                coverage["uncovered"] += 1
                continue

            if not check.get("forbid_regex") and not check.get("forbid_any"):
                errors.append(("CONFIG-LANGUAGE-REF", f"{rule_id}: no executable language reference"))
                errors.append(("CONFIG-BOUNDARY-COVERAGE",
                    f"Genre rule '{rule_id}' ({raw_check.get('type', '')}) with {ref_str} "
                    f"language_pack reference resolved to an empty list."))
                coverage["uncovered"] += 1
                continue

            check.setdefault("level", "P2")
            compiled.append(check)
            coverage["by_language_pack"] += 1
        else:
            if language_pack_ref:
                msg = (
                    f"Genre rule '{rule_id}' ({raw_check.get('type', '')}) with {ref_str} "
                    f"has no executable project boundary_check override and language_pack is misconfigured."
                )
            else:
                msg = (
                    f"Genre rule '{rule_id}' ({raw_check.get('type', '')}) with {ref_str} "
                    f"has no project boundary_check override and no language_pack is configured."
                )
            errors.append(("CONFIG-BOUNDARY-COVERAGE", msg))
            coverage["uncovered"] += 1

    return compiled, errors, coverage

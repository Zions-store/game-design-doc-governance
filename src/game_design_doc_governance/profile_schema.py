# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared Profile-schema and packaged-asset helpers.

The source checkout remains the authoring location for governance assets.  A
wheel receives a build-time copy under ``game_design_doc_governance/assets``;
these helpers resolve the correct location in either environment.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional


# Supported BCP 47 core subset: language, optional Script, optional region.
# Examples: en-US, zh-Hans, zh-Hant-TW, es-419, fr-CA, ja.
LANGUAGE_TAG_PATTERN = r"^[a-z]{2,3}(?:-[A-Z][a-z]{3})?(?:-(?:[A-Z]{2}|[0-9]{3}))?$"
_LANGUAGE_TAG_RE = re.compile(LANGUAGE_TAG_PATTERN)


def validate_language_tag(language: object) -> bool:
    """Return whether *language* is a supported, safe language tag."""
    return isinstance(language, str) and bool(_LANGUAGE_TAG_RE.fullmatch(language))


def asset_directory(name: str) -> Path:
    """Locate a root-owned governance asset directory in source or a wheel."""
    source_root = Path(__file__).resolve().parents[2]
    source = source_root / name
    if source.is_dir():
        return source

    packaged = Path(__file__).resolve().parent / "assets" / name
    if packaged.is_dir():
        return packaged

    raise FileNotFoundError(f"Runtime asset directory not found: {name}")


def detect_profile_kind(data: dict[str, Any]) -> str:
    """Return the explicit profile kind; audit inputs default to project."""
    if data.get("profile_type") == "genre":
        return "genre"
    return "project"


def load_schema(kind: str) -> dict[str, Any]:
    if kind not in {"project", "genre"}:
        raise ValueError(f"Unsupported profile kind: {kind}")
    filename = "project_profile.schema.json" if kind == "project" else "genre_profile.schema.json"
    with (asset_directory("schemas") / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_profile_data(data: object, kind: Optional[str] = None) -> list[str]:
    """Validate Profile data and return deterministic, user-facing errors."""
    if not isinstance(data, dict):
        return ["(root): Profile must be a YAML mapping"]

    resolved_kind = kind or detect_profile_kind(data)
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return ["jsonschema is required for Profile validation"]

    validator = Draft7Validator(load_schema(resolved_kind))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '(root)'}: {error.message}"
        for error in errors
    ]

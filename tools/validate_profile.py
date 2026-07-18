#!/usr/bin/env python3
# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Validate a Project_Profile.yaml or genre profile against its JSON Schema.

Usage:
  python tools/validate_profile.py profiles/genre/open_world_rpg.yaml
  python tools/validate_profile.py --kind project MyProject/Project_Profile.yaml
  python tools/validate_profile.py --kind genre profiles/genre/roguelite.yaml

If --kind is omitted: auto-detected - a profile with `recommended_docs` (but not
`enabled_docs`) is treated as a genre profile; otherwise project.

Exit 0 on valid; exit 1 on one or more errors; exit 2 on missing file or schema.
"""

import sys
import os
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from game_design_doc_governance.profile_schema import (
    detect_profile_kind,
    load_schema,
    validate_profile_data,
)


def _load_schema(name):
    kind = "project" if name == "project_profile.schema.json" else "genre"
    return load_schema(kind)


def _detect_kind(data):
    return detect_profile_kind(data)


def validate(data, kind=None, schemas=None):
    """Return list of error-strings. Empty list = valid."""
    if schemas is None:
        return validate_profile_data(data, kind=kind)

    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return ["PyPI package 'jsonschema' is not installed. Install it: pip install jsonschema"]

    resolved_kind = kind or _detect_kind(data)
    schema = schemas.get(resolved_kind) or _load_schema(
        "project_profile.schema.json" if resolved_kind == "project" else "genre_profile.schema.json"
    )
    errors = sorted(Draft7Validator(schema).iter_errors(data), key=lambda error: list(error.path))
    return [f"{'.'.join(str(part) for part in error.path) or '(root)'}: {error.message}" for error in errors]


def main():
    ap = argparse.ArgumentParser(description="Validate a Game-Design-Doc-Governance profile.")
    ap.add_argument("file", help="Path to the YAML file")
    ap.add_argument("--kind", choices=["project", "genre"], default=None,
                    help="Profile kind (auto-detected if omitted)")
    ap.add_argument("--json", action="store_true", help="Print errors as JSON array")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("PyYAML is required. Install it: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    with open(args.file, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"YAML parse error: {e}", file=sys.stderr)
            sys.exit(2)

    if not isinstance(data, dict):
        print("Top-level must be a mapping", file=sys.stderr)
        sys.exit(2)

    errors = validate(data, kind=args.kind)
    if not errors:
        print(f"VALID: {args.file}")
        return 0

    if args.json:
        json.dump(errors, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for e in errors:
            print(f"  - {e}")
        print(f"{len(errors)} error(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

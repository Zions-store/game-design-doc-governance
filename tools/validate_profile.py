#!/usr/bin/env python3
# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Validate a Project_Profile.yaml or genre profile against its JSON Schema.

Usage:
  python tools/validate_profile.py profiles/open_world_rpg.yaml
  python tools/validate_profile.py --kind project MyProject/Project_Profile.yaml
  python tools/validate_profile.py --kind genre profiles/roguelite.yaml

If --kind is omitted: auto-detected - a profile with `recommended_docs` (but not
`enabled_docs`) is treated as a genre profile; otherwise project.

Exit 0 on valid; exit 1 on one or more errors; exit 2 on missing file or schema.
"""

import sys
import os
import json
import argparse

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


def _load_schema(name):
    path = os.path.join(SCHEMA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schema file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _detect_kind(data):
    if data.get("enabled_docs"):
        return "project"
    if data.get("recommended_docs"):
        return "genre"
    return "project"


def validate(data, kind=None, schemas=None):
    """Return list of error-strings. Empty list = valid."""
    if kind is None:
        kind = _detect_kind(data)

    schema_name = "project_profile.schema.json" if kind == "project" else "genre_profile.schema.json"

    if schemas is None:
        schema = _load_schema(schema_name)
    else:
        schema = schemas.get(kind)

    if schema is None:
        schema = _load_schema(schema_name)

    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return ["PyPI package 'jsonschema' is not installed. Install it: pip install jsonschema"]

    errors = []
    validator = Draft7Validator(schema)
    for e in validator.iter_errors(data):
        path = ".".join(str(p) for p in e.path) if e.path else "(root)"
        errors.append(f"{path}: {e.message}")
    return errors


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

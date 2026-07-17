Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# MANIFEST - game-design-doc-governance

What a release of this Skill contains, and what it deliberately excludes.

## Included (release payload)

```
SKILL.md            README.md   CHANGELOG.md   LICENSE   MANIFEST.md
modules/            01–09 governance modules
templates/          6 templates (PROJECT_PROFILE / STYLE_GUIDE / DESIGN_DOCUMENT /
                    AUTHORITY_MATRIX / CHANGE_CHECKLIST / AUDIT_HISTORY)
doc_modules/        16 per-document skeletons (*.md.tmpl)
profiles/           10 genre profiles (*.yaml)
schemas/            4 JSON Schemas (project_profile / genre_profile / audit_report / issue_state)
tools/              global_doc_audit.py (generic auditor) + scaffold_project.py + validate_profile.py
src/                Python package (audit / scaffold / profile_validation entry points)
docs/               10 user guides (quickstart / installation / migration / audit / schema / etc.)
tests/              fixtures/ + expected/ + README (self-contained regression)
.github/workflows/  CI configuration (ci.yml)
```

## Excluded (never part of a release)

```
__pycache__/  *.pyc  .pytest_cache/  .venv/     # Python local artifacts
<any project>/Design Document/audit/*           # generated audit output of a real project
<temp dirs>                                      # local regression / smoke run outputs
opencode skill junction                          # ~/.config/opencode/skills/... (machine-local wiring)
```

## Distribution model

Distributed as the standalone repository `Zions-store/game-design-doc-governance`.
Install from the repository root with `pip install -e .`.

## Version / tag policy

- Package version lives in `SKILL.md` frontmatter.
- Git tags use standard repository tags: `vX.Y.Z`.
- Historical monorepo skill-scoped tags remain in `project-ledger` and are not moved.
- `1.0.0` froze all interface surfaces (`schema_version: 1`, CLI, audit output, issue-state, scaffold). Breaking changes are reserved for `2.x`.

Copyright (C) 2026 ZionXiaoxiSuOGLocGo

SPDX-License-Identifier: GPL-3.0-or-later

# game-design-doc-governance

A reusable **game design documentation governance** Skill: build and maintain a

multi-document GDD system with single-source authority, cross-document boundaries,

change-safety anchors, and a data-driven Python audit.

One generic framework + a per-genre **Profile** + a data-driven **audit**. Games

enable different documents but obey the same governance principles.

## Layout

```

game-design-doc-governance/

--------- SKILL.md                 # entry point (progressive disclosure)

--------- README.md  CHANGELOG.md  LICENSE

--------- modules/                 # detailed guidance (01-09)

--------- templates/               # PROJECT_PROFILE / STYLE_GUIDE /  - skeletons

--------- doc_modules/             # per-document "applies / owns / not-owns" skeletons

--------- profiles/                # genre profiles (.yaml)

--------- tools/global_doc_audit.py# generic, data-driven auditor

--------- tests/                   # regression fixtures + baseline

```

See `docs/` for quickstart, installation, project setup, migration, and

reference guides.

## Design in two layers (language)

- **Skill payload** (this repo): English  - meant for public release.

- **Generated product** (a project's docs): any language the user picks at run

  time (default English). The agent translates but keeps `{{PLACEHOLDER}}` and

  YAML keys intact.

## The audit

`tools/global_doc_audit.py` reads two rule sources and runs generic + data-driven

checks:

- `STYLE_GUIDE.md`  - document list, anchor registry, deprecated-term registry.

- `Project_Profile.yaml`  - enabled docs, `boundary_checks`, `consistency_checks`,

  `exceptions`, thresholds.

```

python tools/global_doc_audit.py --root <md dir> --out <audit dir> \

    --profile <Project_Profile.yaml> --style <STYLE_GUIDE.md> [--baseline <json>]

```

Requires Python 3 and `PyYAML`.

## Quick Start

### Install

```bash
git clone https://github.com/Zions-store/game-design-doc-governance.git
cd game-design-doc-governance
py -m pip install -e .
```

### New project

```bash
gdd-scaffold \
  --profile profiles/open_world_narrative_tactical_shooter.yaml \
  --out "MyGame/Design Document/md file" \
  --project-name "MyGame" \
  --language en-US
```

### Existing project (migration)

```bash
# Scaffold into a clean directory first (don't overwrite existing docs)
gdd-scaffold \
  --profile profiles/open_world_narrative_tactical_shooter.yaml \
  --out "MyGame/Design Document/md file_new" \
  --project-name "MyGame"

# Migrate one content domain at a time, audit after each, drive P0/P1 to zero.
# Then replace the old directory with the new one.
```

### Audit

```bash
gdd-audit \
  --root "MyGame/Design Document/md file" \
  --style "MyGame/Design Document/md file/STYLE_GUIDE.md" \
  --profile "MyGame/Design Document/md file/Project_Profile.yaml" \
  --out "MyGame/Design Document/audit"
```

### Wire into opencode

```powershell
# Windows (PowerShell)
New-Item -ItemType Junction \
  -Path "$env:USERPROFILE\.config\opencode\skills\game-design-doc-governance" \
  -Target "C:\...\game-design-doc-governance"
```

```bash
# Linux / macOS
ln -s "/path/to/game-design-doc-governance" \
      "$HOME/.config/opencode/skills/game-design-doc-governance"
```

For detailed guides, see `docs/quickstart.md`, `docs/new_project_setup.md`, and `docs/migration_guide.md`.

## Status

**v1.1.10 -- Stable.** Ships: the generic data-driven auditor, 10 genre profiles,
16 doc-module skeletons, 9 modules, 6 templates, 4 JSON schemas, profile
validator, scaffold tool, `issue_state.jsonl` state tracking, self-contained
regression fixtures (6 projects + pytest 22/22), and complete documentation
(`docs/` 10 guides).

All interface surfaces are **frozen** in 1.x: the Profile schema (`schema_version: 1`),
CLI (`gdd-audit`, `gdd-profile-validate`, `gdd-scaffold`), audit output format,
issue-state format, and scaffold output structure. Breaking changes are reserved
for 2.x.

To install: `pip install -e .` (requires Python 3.9+, `pyyaml`, `jsonschema`).
For opencode: wire a junction `~/.config/opencode/skills/game-design-doc-governance`
- this directory.

## License

GPL-3.0-or-later. See `LICENSE`.

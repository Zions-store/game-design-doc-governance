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
├── SKILL.md                  # entry point (progressive disclosure)
├── README.md  CHANGELOG.md  LICENSE
├── modules/                  # detailed guidance (01-12)
├── templates/                # 9 templates, including PROJECT_PROFILE / STYLE_GUIDE / LANGUAGE_PACK / AUDIT_README / SEMANTIC_AUDIT_BATCH
├── doc_modules/              # per-document "applies / owns / not-owns" skeletons
├── profiles/genre/           # genre profiles (.yaml)
├── examples/                 # example project profiles
├── rules/language_packs/     # per-language audit term packs
├── tools/global_doc_audit.py # generic, data-driven auditor
└── tests/                    # regression fixtures + baseline
```

See `docs/` for quickstart, installation, project setup, migration, and

reference guides.

## Design in two layers (language)

- **Skill payload** (this repo): English — meant for public release.

- **Generated product** (a project's docs): any language the user picks at run

  time (default English). The agent translates but keeps `{{PLACEHOLDER}}` and

  YAML keys intact.

## The audit

`tools/global_doc_audit.py` reads two rule sources and runs generic + data-driven

checks:

- `STYLE_GUIDE.md` — document list, anchor registry, deprecated-term registry.

- `Project_Profile.yaml` — enabled docs, `boundary_checks`, `consistency_checks`,

  `exceptions`, thresholds.

```

python tools/global_doc_audit.py --root <md dir> --out <audit dir> \

    --profile <Project_Profile.yaml> --style <STYLE_GUIDE.md> [--baseline <json>]

```

Requires Python 3.9+ with `PyYAML` and `jsonschema` (engine 2).

## Usage Modes

1. **opencode Skill mode** — Wire via junction; `SKILL.md` guides AI-assisted documentation governance.
2. **CLI audit mode** — Use `gdd-audit`, `gdd-profile-validate`, and `gdd-scaffold` standalone (no opencode required).
3. **Template library mode** — Copy `profiles/genre/` and `doc_modules/` templates manually into your project.
4. **Human checklist mode** — Use the authority matrix and boundary rules without running Python tools.

See `docs/quickstart.md` for getting started.

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
  --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \
  --out "MyGame/Design Document/md file" \
  --project-name "MyGame" \
  --language en-US
```

### Existing project (migration)

```bash
# Scaffold into a clean directory first (don't overwrite existing docs)
gdd-scaffold \
  --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \
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

**v2.4.0 — Formal release.** Semantic audit made operational: working
template for audit rounds (batch plan / per-document output shape / both
user checkpoints / merged-list numbering), modules/11 round flow, and
SKILL.md trigger conditions (large rewrite / batch world-fact changes /
release closure). 64 tests, 10 genre profiles, 9 templates.

**v2.3.0 (previous) —** Engine bugfix round (9 confirmed bugs: `--json`
crash, UTF-8 resilience, fail-closed waivers, genre profile mis-kill, silent
rule drop, deprecated-term dedup), docs synced to v2.2 reality, modules 10-12
(workflow documents / semantic audit orchestration / decision governance),
full skeleton coverage (49 doc_modules — every profile-recommended document),
genre `level` inheritance for same-id project overrides, and zh-CN
natural-writing regexes. 64 tests, 10 genre profiles.

**v2.2.0 (previous) —** Enforces boundary coverage: genre rules with
`pattern_ref`/`term_ref` must be covered by executable project overrides or a
language pack, producing P0 `CONFIG-BOUNDARY-COVERAGE` instead of silence.
Scaffold auto-injects `language_pack` when a matching built-in pack exists
(en-US, zh-CN); other languages receive a commented `# <TODO: ...>` hint.
63 tests, 11 new coverage contract tests, 10 genre profiles,
49 doc-module skeleton files; every profile-recommended document is covered
(except Design_Document / STYLE_GUIDE, served by `templates/`), 12 modules (incl. semantic audit & decision governance), 9 templates (including `AUDIT_README_TEMPLATE.md` and `SEMANTIC_AUDIT_BATCH_TEMPLATE.md`),
4 JSON schemas, profile validator, safe scaffold v2 (--dry-run, --force, --enable-doc),
`issue_state.jsonl` state tracking, and self-contained regression fixtures (6 projects + pytest coverage),
and complete documentation (`docs/` 12 guides). The rc9 release-readiness repairs
make schema validation part of the engine-v2 audit path and make wheels
self-contained with the runtime tools and assets they need.

Interface surfaces are **frozen**: the Profile schema (`schema_version: 1`),
CLI (`gdd-audit`, `gdd-profile-validate`, `gdd-scaffold`), audit output format,
issue-state format, and scaffold output structure. Minor versions may add
behavior behind the same interfaces (v2.1 pipeline, v2.2 coverage); breaking
changes are reserved for major versions.

> **Current boundary**: Engine v2 schema-validates the project profile before
> auditing, applies file-scoped expiring waivers, persists the versioned state
> ledger, and renders Report v2. `project_fact_checks` run across all authority
> documents; a configured `language_pack` resolves the selected genre profile's
> `pattern_ref` / `term_ref` rules. Built-in tags (`en-US`, `zh-CN`)
> or safe project-local `.yaml` paths are supported; absolute paths and
> `..` traversal are rejected. The `project_fact_checks.authority` semantics and
> an explicit language-pack fact-reference contract are under evaluation for v2.3.

To install: `pip install -e .` (requires Python 3.9+, `pyyaml`, `jsonschema`).
For opencode: wire a junction `~/.config/opencode/skills/game-design-doc-governance`
- this directory.

## License

GPL-3.0-or-later. See `LICENSE`.

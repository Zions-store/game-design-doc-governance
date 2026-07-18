---
name: game-design-doc-governance
version: 1.5.1
description: "Reusable governance framework for game design documentation. Sets up document authority, genre profiles, cross-document boundaries, change-safety anchors, and data-driven audits."
---

Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later

# Game Design Documentation Governance

A reusable system for building and maintaining game design documentation that
stays consistent as it grows. It is **not** a "write my GDD for me" tool  - it
establishes a *governed document system*: single-source authority, cross-document
boundaries, change-safety anchors, and a repeatable audit.

The key idea: **one generic framework + a per-genre Profile + a data-driven audit.**
Different games enable different documents, but all obey the same principles.

## When to use

- "set up / organize game design documents", "寤虹珛璁捐鏂囨。浣撶郴", "doc governance"
- Starting a new game's GDD and unsure which documents to create
- An existing GDD has become an everything-bucket and needs splitting
- "audit my design docs" / "check design doc consistency" / "鏇存柊瀹¤"
- Migrating an old design doc set into a governed structure

## Core principles

1. **Single authority**  - each kind of content has exactly one authority document.
2. **GDD is an index**  - the GDD keeps summaries and links, never full bodies.
3. **Sub-documents carry full volume**  - light content is fine, light *structure* is not.
4. **Track facts with anchors**  - high-risk cross-document facts use stable anchor IDs.
5. **Register deprecations**  - replaced settings/terms are logged so they can't revive.
6. **Audit after change**  - run the auditor; results are tracked, not asserted.
7. **Profiles adapt to genre**  - the document set is chosen per game type, not fixed.

## Step 0  - Choose output language

The Skill itself is written in English (for publishing). **The documents it
generates for a project can be in any language.** Detect the language of the
user's request; if it is non-English, offer that as the default. Any language the
LLM can output is supported  - the agent translates section headers and labels at
generation time, but keeps `{{PLACEHOLDER}}` markers and YAML keys unchanged.

> "What language should the design documents be written in? Default: English."

The audit script prints English; report language can be configured later.

## Quick workflow  - new project setup

1. **Step 0**: choose output language.
2. **Pick a Profile** from `profiles/genre/` matching the game's genre
   (e.g. `open_world_narrative_tactical_shooter`, `multiplayer_shooter`). See
   `modules/03_genre_profiles.md`.
3. **Create the doc set**: from the selected genre Profile's `recommended_docs`
   (plus any chosen `optional_docs`), scaffold each file using `doc_modules/*.tmpl`
   (each has *applies / owns / does not own / sections*); write the final list into
   `Project_Profile.yaml` `enabled_docs`.
4. **Generate `STYLE_GUIDE.md`** from `templates/STYLE_GUIDE_TEMPLATE.md`, filling
   placeholders from the Profile (file list, authority matrix, boundaries).
5. **Generate `Project_Profile.yaml`** from `templates/PROJECT_PROFILE_TEMPLATE.yaml`.
6. **Set authority & boundaries**  - see `modules/04_authority_boundaries.md`.
7. **Add anchors & deprecations**  - see `modules/05_anchor_and_change_safety.md`.
8. **Run the audit** (below) and drive P0/P1 to zero.

## Audit flow

```
python tools/global_doc_audit.py \
  --root   "<project>/Design Document/md file" \
  --out    "<project>/Design Document/audit" \
  --profile "<...>/Project_Profile.yaml" \
  --style   "<project>/Design Document/md file/STYLE_GUIDE.md"
```

- STYLE_GUIDE.md provides the document list, anchor registry, deprecated-term registry.
- Project_Profile.yaml provides `enabled_docs`, `boundary_checks`,
  `consistency_checks`, `exceptions`, thresholds.
- Outputs `audit_report.md` + `audit_report.json` + appends `audit_history.md`;
  tracks per-issue states in `issue_state.jsonl` (suppresses false-positive /
  accepted-exception issues; `--no-state` opts out).
- `--baseline <json>` compares counts to a known-good baseline (regression gate).
- Details + issue levels/states: `modules/06_audit_workflow.md`.

## Module index

| Module | Purpose |
|---|---|
| `modules/01_document_architecture.md` | Document lifecycle, GDD-vs-subdoc, full-volume rule |
| `modules/02_project_profile.md` | Project_Profile.yaml schema and how the auditor reads it |
| `modules/03_genre_profiles.md` | Genre  - document set matrix (10 genres) |
| `modules/04_authority_boundaries.md` | Authority matrix + cross-document boundary rules |
| `modules/05_anchor_and_change_safety.md` | Anchors, REF usage, deprecated registry, 5-layer change safety |
| `modules/06_audit_workflow.md` | Audit order, issue levels (P0鈥揚3/INFO), issue states |
| `modules/07_export_and_snapshot.md` | Non-authority snapshots (.docx/.pdf) |
| `modules/08_migration_workflow.md` | Migrating an existing GDD |
| `modules/09_ai_collaboration_rules.md` | What the AI must/must not do when editing docs |

## Templates & tools

- `templates/PROJECT_PROFILE_TEMPLATE.yaml`  - per-project profile skeleton.
- `templates/STYLE_GUIDE_TEMPLATE.md`  - 15-chapter document constitution, with placeholders.
- `profiles/genre/*.yaml`  - 10 genre profiles (the current project ships as the first, and as the regression fixture).
- `doc_modules/*.md.tmpl`  - 26 per-document skeletons (applies / owns / not-owns / chapters / boundaries / audit).
- `tools/global_doc_audit.py`  - the generic, data-driven auditor.
- `tests/expected/current_project_baseline.json`  - regression baseline.

## Safety rules (what the AI must not do)

- Do not turn the GDD into a full-text repository.
- Do not maintain the same content in two authority documents.
- Do not create new documents ad hoc  - check the Profile and STYLE first.
- Do not write project-specific lore (names, factions, plot) into this Skill or
  into a shared genre Profile; those belong to a project's own docs/STYLE.
- Do not treat the audit report as design authority; it flags, humans decide.
- Do not add REF anchors just to clear P3 warnings.

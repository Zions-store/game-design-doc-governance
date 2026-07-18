Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# game-design-doc-governance Changelog

## [Unreleased]

_Next: v2.0.0 formal release after RC validation, or patch fixes._

## [2.0.0-rc.5] - 2026-07-18 — Release Candidate 5

### Fixed (since rc.4)
- **P0**: scaffold now injects `profile.language` into existing `profile:` block (no duplicate mapping).
- **P0**: CHANGELOG rc.4 literal `$rc4` replaced with actual entry.
- **P2**: coverage counts synced (24 of 48 doc names have matching skeletons).

## [2.0.0-rc.4] - 2026-07-18 — Release Candidate 4 (superseded)

### Fixed (since rc.3)
- **P0**: scaffold YAML injection no longer creates duplicate `profile:` mapping. `profile_type: project` as top-level field.
- **P0**: 9 genre profiles missing `profile_type: genre` — all 10 now have it.

## [2.0.0-rc.3] - 2026-07-18 — Release Candidate 3 (superseded)

### Fixed (since rc.2)
- **Schema enforcement**: `profile_type` now required in both genre and project profile schemas.
- **Scaffold v2 output**: generated `Project_Profile.yaml` now includes `profile_type: project` and `profile.language` fields.
- **`--dry-run` safety**: validation (non-empty dir, path traversal) now runs before preview output.
- **`_build_plan` dedup**: `Design_Document.md` and `STYLE_GUIDE.md` no longer duplicated in plan when already in enabled docs.
- **Migration checklist**: removed `project_fact_checks` and `language_pack` items (runtime consumption planned for v2.1). Kept `consistency_checks`/`boundary_checks` in project profile unchanged.
- **`--engine` help**: documented that full v2 Finding/Waiver/State/Report pipeline is v2.1; engine v2 currently provides config validation + structured waiver schema.
- **Doc counts**: README and MANIFEST updated (27 skeletons, 21 gaps, 12 docs guides).

### Release Gate (for v2.0.0 formal)
- [x] ThirdPersonTest regression EQUIVALENT
- [x] Schema enforces profile_type + v2 contract
- [x] Scaffold generates v2-compliant profiles
- [x] Migration guide accurate
- [x] --dry-run validation order fixed
- [ ] Full pytest suite + wheel install
- [ ] All 10 profiles scaffold→audit E2E

## [2.0.0-rc.2] - 2026-07-18 — Release Candidate 2 (superseded)

## [2.0.0-rc.1] - 2026-07-18 — Release Candidate 1 (superseded)

## [1.9.0] - 2026-07-18 — v2 Contract Freeze

### Added
- `docs/v2_contract.md` — complete frozen specification for v2.0.0 (11 sections).
- **Frozen contracts**: Profile Schema v2, Audit Finding v2, State Schema v2, Report Schema v2, Scaffold safety semantics, Skeleton support rules, Multi-language structure protection, Waiver v2, Audit Engine v2, v1 compatibility & deprecation table, Migration path.
- **Version gate**: v1.9.0 is feature-frozen. Only bug fixes and docs from this point.

### Changed
- No functional changes. All v2 behavior remains opt-in (`--engine 2`) until v2.0.0-rc.

## [1.8.0] - 2026-07-18 -- Any-Language Generation

### Added
- `src/game_design_doc_governance/i18n.py` — any-language generation module.
- **LanguageProvider** (ABC): abstract base for model-driven document translation.
- **FakeProvider**: offline implementation for CI/testing — wraps source with language markers, never claims false completion.
- **GenerationMetadata**: tracks target language, provider type, model ID, prompt version, profile ID, and structure validation result per generation.
- **validate_structure()**: post-generation check that placeholders, YAML keys, anchors, REFs, document links, and rule IDs survive generation intact. Returns list of issues.
- **normalize_language()**: normalizes BCP 47 tags to 20 supported languages with prefix fallback.
- **SUPPORTED_LANGUAGES**: 20 languages (en-US, zh-CN, ja, ko, fr, de, es, pt-BR, ar, ru, it, nl, pl, tr, th, vi, id, ms, hi, fr-CA).

### Changed
- Scaffold `--language` now accepts any value (not limited to en-US/zh-CN). Unknown languages return as-is; provider decides support.
- `src/__init__.py` exports i18n symbols.

## [1.7.0] - 2026-07-18 -- Skeleton Coverage Release

### Added
- `Monetization_Design.md.tmpl` — 8-section skeleton (revenue model, premium currency, battle pass, loot boxes, subscriptions, advertising, store, responsible monetization). Highest-cited missing doc across profiles.
- Full skeleton coverage audit: 27 of 48 unique doc names now have formal skeletons. 22 are documented gaps (no skeleton, listed in profiles).

### Changed
- `SKILL.md`: doc_module count updated to 27, with note about 22 known gaps.
- `README.md`: Status updated with 27 skeletons, safe scaffold features.

## [1.6.0] - 2026-07-18 -- Safe Scaffold v2

### Added
- **Dry-run** (`--dry-run`): preview all files that would be created without writing.
- **Non-empty directory protection**: refuses to write to existing non-empty dir without `--force`.
- **Path validation**: rejects directory traversal (`..`) and filesystem root targets.
- **`--enable-doc`**: explicitly select optional docs (repeatable). Optional docs are no longer created by default.
- **`--disable-doc`**: exclude a recommended doc (repeatable).
- **`--legacy`**: restore v1 behavior (all optional docs included, no safety checks).
- **Atomic writes**: all file writes use tempfile + rename to prevent partial output.
- **`_cleanup()`**: removes partially created files on failure — no half-finished projects.

### Changed
- `scaffold()`: signature extended with `dry_run`, `force`, `extra_docs`, `disabled_docs`, `legacy` parameters.
- Unsupported docs now produce a clear placeholder (not a TODO emoji fallback).

## [1.5.1] - 2026-07-18 -- Finding/Waiver/State/Report v2 Patch

### Fixed
- **P0**: `tools/scaffold_project.py` restored valid AST — unclosed string and mojibake on line 40 repaired.
- **WaiverManager**: `matches()` now compares against `finding.rule` (e.g. "GDD-SUMMARY-ONLY-ENERGY"), not the hashed `finding.id`. Fixes waiver exceptions never matching.
- **Waiver.is_expired()**: normalized timezone handling prevents `TypeError` when comparing naive/aware `datetime` objects.
- **SKILL.md**: doc_module count corrected 16→26.
- **MANIFEST.md**: doc_module count corrected 16→26.
- **README.md**: removed stale link to non-existent `docs/usage_modes.md`.

## [1.5.0] - 2026-07-18 -- Finding/Waiver/State/Report v2

### Added
- **Stable Finding ID**: fingerprint based on (rule, file) pair, not message text. Wording changes no longer create false "new issues". Non-matching `make_id()` semantics for idempotent issue tracking.
- **WaiverManager**: precise `(rule_id, file)` binding (not just global rule ID). `expires` field actually enforced — expired waivers auto-reactivate findings, reported separately.
- **StateManager**: versioned `issue_state.jsonl` schema (`_schema: 1`), atomic writes via tempfile+rename, corruption detection per-line (invalid JSON → CORRUPT status, audit continues).
- **Report v2** (`render_report_v2`): UTC ISO timestamps, Run ID, engine version, active/expired waiver counts, suppressed findings section with reasons.

### Changed
- `Finding.make_id()`: seed changed from `level|rule|file|message` → `level|rule|file`.
- `tools/global_doc_audit.py` `--engine 2` now loads WaiverManager for structured exception handling.
- Updated `__init__.py` exports: `Waiver`, `WaiverManager`, `StateManager`, `render_report_v2`.

## [1.4.0] - 2026-07-18 -- Audit Engine v2 Alpha

### Added
- `src/game_design_doc_governance/engine.py` — v2 audit engine core with `AuditContext`, `Finding`, and `validate_profile()`.
- `--engine 2` CLI flag: enables strict config validation before audit checks.
- Config validation checks: missing `enabled_docs`, malformed `deprecated_terms`, `boundary_checks`, and `exceptions` entries.
- `__init__.py` now exports `AuditContext`, `Finding`, and `validate_profile`.

### Changed
- `tools/global_doc_audit.py`: added `engine_version` parameter to `run_audit()` and `--engine` CLI arg. v2 engine validates profile structure before running checks; aborts on P0/P1 config issues.
- v1 engine remains the default (`--engine 1`); all existing behavior unchanged.

## [1.3.0] - 2026-07-18 -- Doc-Module Coverage Release

### Added
- 10 new doc_module skeletons: `Audio_Design`, `Art_Style_Guide`, `Animation_Design`, `Technical_Art`, `Accessibility`, `Localization`, `QA_Test_Plan`, `Production_Roadmap`, `Build_And_Release`, `Analytics_And_Telemetry` (16 → 26 total).
- Each skeleton follows the 6-section format: Applies / Owns / Does not own / Recommended chapters / Common boundaries / Audit notes.
- Expanded optional docs for `open_world_narrative_tactical_shooter` (+6) and `multiplayer_shooter` (+4) genre profiles.

### Changed
- README Status: doc-module count updated (16→26), version v1.2.0 → v1.3.0.

## [1.2.0] - 2026-07-18 -- Generalization Boundary Release

### Added
- `profiles/genre/` — genre profiles moved from flat `profiles/` (10 profiles).
- `examples/third_person_test/` — example project profile, baseline, README.
- `rules/language_packs/zh-CN.yaml` and `en-US.yaml` — per-language audit term packs.
- `profile_type` field added to genre and project profile JSON schemas.
- `project_fact_checks` and `language_pack` fields added to project profile schema.
- README: four usage modes (opencode / CLI / template / human checklist).
- `modules/09_ai_collaboration_rules.md` marked optional.

### Changed
- `open_world_narrative_tactical_shooter.yaml`: removed `enabled_docs`, project-specific `consistency_checks` (FACT-PROTAGONIST-NOT-CYBORG, FACT-CHAR-C-NOT-ABANDONED), Chinese regex and term lists. Now a pure genre profile with rule type references.
- All 22 path references across 13 files updated from `profiles/` to `profiles/genre/`.
- `tests/test_auditor.py`: test paths updated for new directory layout.
- README Status: v1.1.11 → v1.2.0.

## [1.1.11] - 2026-07-18 -- Baseline Integrity Patch

### Fixed
- `CHANGELOG.md` [1.1.10] date corrected from `2026-07-17` to `2026-07-18` (matched actual tag commit date).
- `docs/release_process.md` CI job count corrected from 4 to 5 (added `utf8-check`).
- `docs/issue_state.md` added current limitation note: `exceptions.expires` and `reason` are defined in schema but not yet enforced by the engine.
- `README.md` added known 1.x limitations disclosure (profile mixing, scaffold behavior, partial field enforcement).
- `MANIFEST.md` replaced outdated `0.4.0` pre-1.0 language with `1.0.0` freeze policy.

## [1.1.10] - 2026-07-18 -- Baseline Integrity Release

### Fixed
- `tools/global_doc_audit.py` `SCRIPT_VERSION` synced from `v1.1.1-generic` to `v1.1.10-generic` (was 8 versions behind).
- `CHANGELOG.md` [1.1.9] date corrected from `2026-07-11` to `2026-07-17` (matched actual tag commit date).
- `docs/issue_state.md` updated: removed stale "In the future" language for `exceptions` field (already implemented since v0.3.0).
- `MANIFEST.md` updated: added missing release payload entries (`tools/scaffold_project.py`, `tools/validate_profile.py`, `schemas/`, `docs/`, `src/`, `.github/workflows/`).
- `docs/release_process.md` updated: added `tools/global_doc_audit.py` `SCRIPT_VERSION` to the version-bump checklist.
- `templates/PROJECT_PROFILE_TEMPLATE.yaml` fixed residual `-?` mojibake on line 4.

## [1.1.9] - 2026-07-17 -- Installation UX Hotfix

### Fixed
- Default install commands in `README.md`, `docs/installation.md`, and `docs/quickstart.md` now use HTTPS (`https://github.com/...`) instead of SSH (`git@github.com:...`). SSH remains documented as an option for contributors with a configured key.
- Added `py -m pip install -e .` as the recommended Windows install command.
- Added Troubleshooting section to `docs/installation.md` covering `Permission denied (publickey)`.

## [1.1.8] - 2026-07-11 -- Release Metadata Sync

### Fixed
- Synced `SKILL.md`, `pyproject.toml`, and `README.md` versions to `1.1.8`.
- Removed remaining `-?` / `--?` mojibake remnants from public documentation.
- Updated release process wording for the standalone repository.

---
## [1.1.7] - 2026-07-10 -- Changelog Backfill and Residual Cleanup

### Fixed
- Backfilled missing `0.5.0` through `1.0.1` changelog entries.
- Continued residual mojibake cleanup after the standalone repository split.

---
## [1.1.6] - 2026-07-10 -- Mojibake CI Gate Fix

### Fixed
- Reduced mojibake CI blocker to `U+FFFD` only; removed `---` and `??` from
  patterns (false-positives on Markdown table syntax, YAML frontmatter, and code).
- Manually repaired residual `-?` em-dash damage in SKILL.md, README.md, and
  CHANGELOG.md prose.

---
## [1.1.3] - 2026-07-10 -- SKILL Description Cleanup

### Fixed
- Repaired `SKILL.md` frontmatter description encoding (rewritten as ASCII-safe).
- Inserted standalone release history into `CHANGELOG.md`.
- Repaired `open_world_narrative_tactical_shooter.yaml` as valid UTF-8 YAML.
- Added CI UTF-8 text-file check and mojibake pattern guard.

---
## [1.1.2] - 2026-07-10 -- Profile UTF-8 Repair

### Fixed
- Rewrote `profiles/open_world_narrative_tactical_shooter.yaml` as clean UTF-8.
- Added CI `utf8-check` job.
- Restored `gdd-scaffold` and profile-validation tests.

---
## [1.1.0] - 2026-07-10 -- Standalone Repository Release

### Changed
- Extracted `game-design-doc-governance` from `project-ledger` into a standalone repository.
- Updated package, CI, release, installation, and opencode wiring paths for standalone use.
- Switched release tags to standard `vX.Y.Z` format.

### Notes
- Historical monorepo skill-scoped tags remain in `project-ledger` and are not moved.

---
## [1.0.1] - 2026-07-09 -- Markdown Lint Hotfix

### Fixed
- Normalized README blank lines to satisfy markdownlint MD012.

---
## [1.0.0] - 2026-07-09 -- Stable Release

### Stable
- Profile schema v1 frozen; CLI, audit output, issue_state, scaffold frozen.
- 1.x backward-compatible; breaking changes reserved for 2.x.

### Includes
- 10 genre profiles, 16 doc-module skeletons, 9 governance modules, 6 templates,
  4 JSON schemas, self-contained regression fixtures, `docs/` 10 guides, CI 5 jobs.

---
## [0.9.0] - 2026-07-09 -- Release Candidate

### Added
- `docs/` 10 standalone guides (quickstart, installation, setup, migration,
  audit, schema, markers, issue_state, troubleshooting, release process).
- CI markdown-lint extended to docs/.
- Feature freeze: no new features before 1.0.0.

---
## [0.8.0] - 2026-07-09 -- Scaffold

### Added
- `gdd-scaffold`: initialize a new design-doc project from a genre profile.
- Console script support; en-US and zh-CN language.
- CI scaffold smoke + pytest test_scaffold_and_audit.

---
## [0.7.1] - 2026-07-09 -- CI working-directory hotfix

### Fixed
- Fixed `pip install -e .` by targeting the `game-design-doc-governance/`
  subdirectory (`working-directory`) instead of the monorepo root.

---
## [0.7.0] - 2026-07-09 -- Packaging / CLI

### Added
- `pyproject.toml` + `requirements.txt`; `src/game_design_doc_governance/` package.
- Console scripts: `gdd-audit`, `gdd-profile-validate`.
- `pip install -e .` installation; CI uses console scripts.

---
## [0.6.3] - 2026-07-09 -- Template key alignment

### Fixed
- Aligned `PROJECT_PROFILE_TEMPLATE.yaml` top-level key from `project` to `profile`.

---
## [0.6.2] - 2026-07-09 -- Schema Validation Hotfix

### Fixed
- Allowed `open_world_narrative_tactical_shooter` as a hybrid genre + project profile.
- Tightened project schema: unknown top-level fields rejected.
- Aligned project schema nested key to `profile`.

---
## [0.6.1] - 2026-07-09 -- Schema import hotfix

### Fixed
- CI pytest job runs from skill root so `tools.validate_profile` is importable.
- conftest.py adds skill root to sys.path as a fallback.

---
## [0.6.0] - 2026-07-09 -- Schema validation

### Added
- 4 JSON Schemas (`project_profile`, `genre_profile`, `audit_report`, `issue_state`).
- `tools/validate_profile.py` CLI; `jsonschema`-based.
- pytest schema tests (10 genre profiles + template pass validation).
- `schema_version: 1` backward-compatible throughout 1.x.

---
## [0.5.1] - 2026-07-09 -- Test and CI Hotfix

### Fixed
- pytest argument collision, monkeypatch leakage, fixture P3 expectations.
- CI restored to green after 0.5.0 fixture/pytest introduction.

---
## [0.5.0] - 2026-07-09 -- Self-contained test suite + pytest

### Added
- 6 self-contained fixtures, 5 expected baselines.
- pytest suite (17 tests); CI pytest job.

---
## [0.4.1] - 2026-07-09 -- CI Hotfix

### Fixed
- Fixed markdownlint-cli2-action configuration by replacing unsupported extra_args
  with config + globs; lint surface narrowed to source .md files.
- Added .markdownlint-cli2.jsonc (MD013@250ch / MD022 off / MD024 off / MD029 off /
  MD032 off / MD034 off / MD040 off / MD041 off); ignores **/tests/fixtures/** +
  node_modules + .tmp_validation + .pytest_cache.
- Replaced shell-based code-fence check with a Python checker (covers .md +
  .tmpl; roots: README/CHANGELOG/SKILL/MANIFEST/modules/templates/tests/doc_modules).
  Also resolves the latent shell backtick ( ` ) parsing bug.
- Retained game-design-doc-governance-v0.4.0; new tag game-design-doc-governance-v0.4.1.

---

## [0.4.0] - 2026-07-09 -- First public pre-1.0 release

> **Pre-1.0 / not stable.** This is the first publicly published release on the
> pre-1.0 track. The Profile schema, CLI, and scaffold workflow are **not yet
> frozen**; breaking changes may still occur before 1.0.0.

### P4 governance wiring
- Wired the Skill into opencode via a local NTFS junction
  (`~/.config/opencode/skills/game-design-doc-governance`); discovery verified in a new session.
- Verified the generic auditor against the origin project for **3 consecutive
  frozen-version runs** (`[0,0,0,1,0]`, EQUIVALENT, P3=`AUD-P3-d33cd196`), plus a
  versioned-filename smoke test (canonical / `(n)` / `_vN` / `.N`; excludes
  `_TEMPLATE`/`_BACKUP`/`_OLD`).
- Origin project switched its audit entry point to a thin wrapper (repo path first,
  junction fallback) while preserving the previous engine as
  `global_doc_audit_project_v3_legacy.py` for instant rollback.

### Tests
- Added a **self-contained sanitized fixture** `tests/fixtures/sample_open_world/`
  (+ `expected/sample_fixture_baseline.json`) as the primary regression source, so
  regression no longer depends on an external/real project path. Baseline
  `[0,0,0,1,0]`, single P3 `RULE-SAMPLE-ONLY`. The fixture uses AUDIT markers, also
  covering the language-independent STYLE-parsing path.

### CI / packaging
- CI gains a Python health job (py_compile + `--help` + fixture-baseline run) and
  excludes `tests/fixtures/**` from the markdown/copyright checks.
- Cross-platform: report path line uses `os.sep` instead of a hard-coded backslash.
- Added `MANIFEST.md` (release contents / exclusions).

### Notes
- Local milestone tag `v0.4.0-local-p4` remains; the published release tag is
  `game-design-doc-governance-v0.4.0`.

---

## [0.3.2] - 2026-07-09 -- Pre-P4 Audit Robustness

### Fixed
- **`modules/06` --2**: Pass condition now lists `--strict` / `--pedantic` /
  `--fail-on-p2` (and profile `audit.*` relaxation), matching the script.
- **`modules/06` --4**: Outputs now list `issue_state.jsonl`.
- **`SKILL.md`** quick workflow step 3: build the doc set from the genre profile's
  `recommended_docs` (+ optional), then write into `Project_Profile.yaml` `enabled_docs`
  (a genre profile has no `enabled_docs`).
- **`tests/README.md`**: baseline command adds `--no-state`, with a note to use a
  fresh out dir / `--no-state` so prior suppression can't skew the expected P3.

### Changed
- **Document-existence-ж- generalised (P2-4=B)**: new shared `match_versioned_doc()`;
  `find_latest()` globs `{base}*{ext}` then strictly filters via `version_pattern`
  (canonical / `(n)` / `_vN` / `.N`) ?rejecting `*_TEMPLATE/_BACKUP/_OLD`.
  `check_file_list()` and `check_links()` now reuse `find_latest`/`doc_exists`
  (single source of truth for existence; no more hard-coded `(n)` normalisation).
- Script  - `v1.1.1-generic`.

### Verified
- `find_latest` unit test: canonical / `(n)` / `_vN` / `.N` all resolve to the
  highest version; `_TEMPLATE`/`_BACKUP`/`_OLD` excluded.
- Origin-project regression: hard-coded vs generic both `[0,0,0,1,0]` EQUIVALENT
  (**D4 parallel-equivalence run 3/3**); baseline EQUIVALENT (`--no-state`); 12 docs found.

---

## [0.3.1] - 2026-07-09 -- Release-Consistency Fixes

### Fixed
- **README** status was stale (v0.1.0) ?updated to v0.3.1 / P3.
- **Language-independent STYLE parsing**: `load_style_rules` now reads
  `<!-- AUDIT: ENABLED_DOCS / ANCHOR_REGISTRY / DEPRECATED_TERMS _START/_END -->`
  marker blocks first (works for any generated language), falling back to the
  legacy heading heuristic so existing (e.g. Chinese) STYLE files parse unchanged.
  `STYLE_GUIDE_TEMPLATE.md` now emits those markers.
- **`--strict` now takes effect**: strict/pedantic gate P2 via the profile's
  `fail_on_p2_in_strict_mode`.
- **Profile `audit` thresholds** (`fail_on_p0` / `fail_on_p1` /
  `fail_on_p2_in_strict_mode`) now participate in pass/fail.
- **`file_versioning.version_pattern`** is passed through to `read_doc`/`find_latest`.
- **`link_checks.enabled` / `ignored_dirs`** are honoured.
- **Link check** now strips `#fragment` before the `.md` test (e.g.
  `Mission_Design.md#section` is validated instead of skipped).
- **Baseline compare** now covers P0-CP3 only (INFO is informational, not a gate).
- STYLE template --13/--14 document `audit/issue_state.jsonl`.
- Script version ?`v1.1.0-generic`.

### Verified
- Origin-project regression unchanged: hard-coded vs generic both `[0,0,0,1,0]`
  EQUIVALENT (D4 parallel-equivalence run 2); baseline EQUIVALENT.
- Marker path unit-checked on an English STYLE (docs/anchors/deprecated parsed).
- `--strict` smoke: PASS with P2=0.

---

## [0.3.0] - 2026-07-09 -- P3 Full Governance

### Added
- **modules** 07_export_and_snapshot, 08_migration_workflow, 09_ai_collaboration_rules.
- **templates** DESIGN_DOCUMENT_TEMPLATE.md, AUTHORITY_MATRIX_TEMPLATE.md,
  CHANGE_CHECKLIST_TEMPLATE.md, AUDIT_HISTORY_TEMPLATE.md.
- **Issue-state tracking** in `tools/global_doc_audit.py`: reads/writes
  `issue_state.jsonl` with states OPEN / FIXED_PENDING_VERIFY / VERIFIED /
  FALSE_POSITIVE / ACCEPTED_EXCEPTION / REOPENED. Human-marked FALSE_POSITIVE /
  ACCEPTED_EXCEPTION issues are suppressed from the counts (surfaced as
  "suppressed"); `--no-state` opts out.

### Verified
- Parallel verification on the origin project (D4 P3, run 1): hard-coded script vs
  generic script + origin `Project_Profile.yaml` both yield `[0,0,0,1,0]` ?EQUIVALENT.
- Regression vs baseline still EQUIVALENT.
- Suppression: marking the P3 as ACCEPTED_EXCEPTION drops P3 to 0 with suppressed=1.

### Note
- The origin project gains `Design Document/md file/Project_Profile.yaml` (D7). Its
  own audit script is unchanged (D4: switch to thin wrapper deferred to P4).

---

## [0.2.0] - 2026-07-09 -- P2 Genre Library

### Added
- **modules/03_genre_profiles.md** ?the two profile shapes (genre vs project
  instance) and a 10-genre matrix.
- **9 genre profiles** (`profiles/*.yaml`): open_world_rpg, linear_action_adventure,
  multiplayer_shooter, survival_crafting, roguelite, strategy_simulation,
  puzzle_adventure, horror_narrative, liveops_mobile ?each with
  `recommended_docs` / `optional_docs` / `disabled_docs`, `high_risk_boundaries`,
  `audit_focus`, `suggested_doc_modules`.
- **16 doc_module skeletons** (`doc_modules/*.md.tmpl`): Narrative_Bible / Script /
  Pipeline, Character_Sheets, Mission_Design, World_Design, Level_Design,
  Encounter_Design, Gameplay_Systems, Resource_And_Economy, Progression_Design,
  Collectibles_Design, Multiplayer_Design, LiveOps_Design, UI_UX_Design,
  Technical_Design ?each with applies / owns / does-not-own / recommended chapters /
  common boundaries / common audit rules.

### Changed
- `open_world_narrative_tactical_shooter.yaml`: added `recommended_docs` to match the
  genre-profile shape (`enabled_docs` retained for the auditor / regression fixture).

### Verified
- Regression against the origin project still EQUIVALENT (`P0=0 P1=0 P2=0 P3=1`).

---

## [0.1.0] - 2026-07-09 -- P1 MVP

### Added
- **SKILL.md** entry point (English; Step 0 output-language selection; module index;
  new-project workflow; audit flow; safety rules).
- **tools/global_doc_audit.py** ?generic, data-driven auditor:
  - Reads rules from `STYLE_GUIDE.md` (document list / anchor registry /
    deprecated-term registry) and `Project_Profile.yaml`
    (`enabled_docs` / `boundary_checks` / `consistency_checks` / `exceptions` /
    thresholds).
  - Generic checks retained in the engine (file list, tables, anchors + REF,
    deprecated terms, cross-document links).
  - Project-specific checks are **externalised** to the Profile (no hard-coded
    lore). `boundary_checks` support `forbid_regex` / `forbid_any`,
    `unless_near`, `stop_at`, and `match: first_per_term`;
    `consistency_checks` support `require_negation_near` /
    `require_all_context_near`.
  - English report `audit_report.md` + `audit_report.json`; appends
    `audit_history.md`; `--baseline` count comparison; CLI
    `--root/--out/--profile/--style/--strict/--fail-on-p2/--pedantic/`
    `--json-only/--md-only/--no-history`.
- **profiles/open_world_narrative_tactical_shooter.yaml** ?first genre profile;
  also the regression fixture. Migrates the origin project's five hard-coded
  checks into data rules.
- **templates/PROJECT_PROFILE_TEMPLATE.yaml** and **templates/STYLE_GUIDE_TEMPLATE.md**.
- **modules/** 01 (document architecture), 02 (project profile),
  04 (authority & boundaries), 05 (anchors & change safety), 06 (audit workflow).
- **tests/expected/current_project_baseline.json** ?regression baseline.

### Verified
- Regression against the origin project (`open_world_narrative_tactical_shooter`)
  reproduces `P0=0 P1=0 P2=0 P3=1 INFO=0`; `--baseline` reports EQUIVALENT.
- Does not modify the origin project's existing audit script (D4: P1/P2 leave it in place).

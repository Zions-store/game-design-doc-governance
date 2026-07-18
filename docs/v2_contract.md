# v2 Contract — Frozen Specifications

> **Freeze date**: 2026-07-18  
> **From freeze point**: no new features; only bug fixes and documentation.  
> **Effective**: v2.0.0 — when v2 becomes the default for all new projects and outputs.

---

## 1. Profile Schema v2

### 1.1 Genre Profile (`profiles/genre/*.yaml`)

| Field | Type | Required | Notes |
|-------|------|:--:|------|
| `schema_version` | int | ✅ | Must be `1` (1.x compat). v2 defaults to `2`. |
| `profile_type` | enum | ✅ | Must be `"genre"` |
| `profile.name` | string | ✅ | |
| `profile.description` | string | ✅ | |
| `profile.primary_type` | string | ✅ | |
| `profile.secondary_types` | array | | |
| `recommended_docs` | array | ✅ | Docs enabled by default for this genre |
| `optional_docs` | array | | Docs only created when `--enable-doc` is used |
| `disabled_docs` | array | | Docs explicitly excluded |
| `high_risk_boundaries` | array | | |
| `audit_focus` | array | | |
| `suggested_doc_modules` | array | | |
| `boundary_checks` | array | | Rule type references only (no project facts) |
| `consistency_checks` | array | | Must be empty `[]` or absent in genre profiles |
| `deprecated_terms` | array | | Must be empty `[]` in genre profiles |

**Forbidden in genre profiles**:
- `enabled_docs` (project-only field)
- `project_fact_checks`
- `named_characters`, `specific_factions`, `specific_lore_terms`
- `language_specific_terms` (Chinese resource words, project-specific names)
- Any project-specific lore (Shepherd, 尖兵C, 改造人, 弃子, etc.)

### 1.2 Project Profile (`examples/*/Project_Profile.yaml`)

| Field | Type | Required | Notes |
|-------|------|:--:|------|
| `schema_version` | int | ✅ | |
| `profile_type` | enum | ✅ | Must be `"project"` |
| `profile.name` | string | ✅ | |
| `profile.language` | string | ✅ | BCP 47 tag |
| `profile.genre_profile` | string | | References a `profiles/genre/` entry |
| `enabled_docs` | array | ✅ | |
| `language_pack` | string | | Path to `rules/language_packs/*.yaml` |
| `project_fact_checks` | array | | Project-specific facts with `forbid_terms`, `require_negation_near` |
| `boundary_checks` | array | | With concrete `forbid_regex` / `forbid_any` |
| `non_authority_files` | array | | |
| `exceptions` | array | | Waivers with `id`, `file`, `reason`, `expires` |
| `audit` | object | | `fail_on_p0`, `fail_on_p1`, `fail_on_p2_in_strict_mode` |
| `file_versioning` | object | | `version_pattern`, `latest_strategy` |
| `link_checks` | object | | `enabled`, `ignored_dirs` |

---

## 2. Audit Finding v2 (→ v2.1 full pipeline)

> **v2.0**: schema + config validation + `--engine 2` default.
> **v2.1**: full Finding/Waiver/State/Report pipeline wired into audit chain.

### 2.1 Finding Identity

- **Stable ID**: `AUD-{LEVEL}-{md5(level|rule|file)[:8]}`
- Identity is based on (rule, file) pair, **not** message text.
- Wording improvements do NOT create "new issues".
- Baseline comparison uses Finding ID, not full message text.

### 2.2 Finding Structure

```json
{
  "id": "AUD-P2-abcd1234",
  "level": "P2",
  "rule": "GDD-SUMMARY-ONLY-ENERGY",
  "message": "Possible energy rate in GDD without Gameplay_Systems link.",
  "file": "Design_Document.md",
  "location": "",
  "suppressed": false,
  "suppression_reason": ""
}
```

### 2.3 Levels

| Level | Meaning | Gate |
|-------|---------|------|
| P0 | Blocking: fact/authority conflict, missing doc, config invalid | Must fix |
| P1 | High: deprecated setting, broken link, boundary leak | Must fix |
| P2 | Medium: format issues, rule suspicions | Blocks in `--strict` |
| P3 | Advisory: traceability, naming suggestions | Non-blocking |
| INFO | Informational: non-authority files present | Non-blocking |

---

## 3. State Schema v2 (→ v2.1)

> **v2.1**: StateManager wired into audit chain.

- **Schema marker**: `"_schema": 1` on every entry.
- **Atomic writes**: tempfile + rename. No partial writes.
- **Corruption detection**: per-line JSON parse errors produce `CORRUPT` entries; audit continues.
- **File-scoped state**: state entries keyed by `issue_id` (Finding ID).

### 3.2 States

| State | Meaning |
|-------|---------|
| `OPEN` | Detected in current run |
| `FIXED_PENDING_VERIFY` | Changed, awaiting next audit |
| `VERIFIED` | Confirmed gone on next audit |
| `FALSE_POSITIVE` | Human-confirmed false alarm |
| `ACCEPTED_EXCEPTION` | Registered waiver (suppressed) |
| `REOPENED` | Was fixed, appeared again |
| `CORRUPT` | Line unreadable (audit continues) |

---

## 4. Report Schema v2 (→ v2.1)

> **v2.1**: Report v2 rendered by audit engine.

```markdown
# Audit Report v2
- Run ID: AUDIT-YYYYMMDD-HHMM (UTC)
- Started: RFC3339 UTC timestamp
- Engine: vN
- Script: vX.Y.Z-generic
- Root / Profile / Style paths

## Summary
| Level | Count |
| P0-P3, INFO, _suppressed_

Active waivers: N
Expired waivers: N

## P0 / P1 / P2 / P3 / INFO
- [ID] **file**: message

## Suppressed
- [ID] **file**: message (reason: ...)

## Expired Waivers
- id [file]: expired YYYY-MM-DD

## Verdict
- PASS/FAIL (P0=N P1=N P2=N P3=N)
```

### 4.2 JSON Report

```json
{
  "audit_id": "AUDIT-20260718-HHMM",
  "time": "RFC3339 UTC",
  "script_version": "vX.Y.Z-generic",
  "engine_version": 2,
  "p0": 0, "p1": 0, "p2": 0, "p3": 0, "info": 0,
  "suppressed": 0,
  "waivers_active": 0,
  "waivers_expired": 0,
  "issues": [...],
  "loaded_rules": {
    "docs": 12, "anchors": 15, "deprecated": 6,
    "boundary_checks": 4, "consistency_checks": 2
  }
}
```

---

## 5. Scaffold Safety Semantics v2

### 5.1 Default Behavior (v2)

| Rule | v1 Legacy | v2 Default |
|------|-----------|------------|
| Non-empty directory | Silently overwrites | **Refused** (needs `--force`) |
| Optional docs | All created | **Only when** `--enable-doc` used |
| Path traversal | Unchecked | **Rejected** |
| File writes | Direct | **Atomic** (tempfile + rename) |
| Failure cleanup | Leaves partial output | **`_cleanup()`** removes all |
| Unsupported docs | TODO emoji fallback | **Clear placeholder** |

### 5.2 CLI

```
gdd-scaffold --profile ... --out ... [--project-name ...] [--language ...]
             [--dry-run] [--force] [--enable-doc X] [--disable-doc X]
             [--legacy]
```

---

## 6. Skeleton Support Rules v2

- **24 of 48 unique game-design doc names** have formal skeletons.
- **22 doc names** are known gaps (referenced by profiles, no skeleton).
- A profile **may** reference docs without skeletons; scaffold will produce a clear placeholder.
- Scaffold **must not** silently generate TODO fallback emoji shells.
- Each skeleton **must** have 6 sections: Applies / Owns / Does Not Own / Recommended Chapters / Common Boundaries / Audit Notes.

---

## 7. Multi-Language Structure Protection

- **LanguageProvider** (ABC): model-driven translation. Implementations must not store keys in repo.
- **FakeProvider**: CI-compatible offline provider. Returns source wrapped with language markers.
- **validate_structure()**: checks PLACEHOLDER, YAML_KEY, ANCHOR_ID, REF_MARKER, DOC_LINK survival.
- **Degradation**: without a configured Provider, scaffold MUST clearly state translation was not performed.
- **Structure must not be broken** by generation. Broken output is rejected.

---

## 8. Waiver v2 (→ v2.1)

> **v2.1**: WaiverManager wired into audit chain.

- Waivers are loaded from `profile.exceptions[]`.
- Matching is by **rule name** (e.g. `"GDD-SUMMARY-ONLY-ENERGY"`) + **file scope**.
- `expires` (ISO 8601 date) enforcement: expired waivers auto-reactivate findings.
- Report distinguishes: active waivers, expired waivers, suppressed findings.

---

## 9. Audit Engine v2

- `--engine 1`: v1 legacy path (global mutable state, no config pre-validation).
- `--engine 2` (default in v2.0): Pre-validates profile structure. The full Finding/Waiver/State/Report pipeline is **v2.1**.
  - v2.0: config validation + structured waiver schema + `--engine 2` default.
  - v2.1: WaiverManager.apply(), StateManager, render_report_v2 wired into the actual audit chain.

## 10. v1 Compatibility & Deprecation

| v1 Feature | Status in v2 |
|------------|-------------|
| Flat `profiles/*.yaml` paths | **Removed** as primary path; `profiles/genre/` only |
| `enabled_docs` in genre profiles | **Forbidden** (project profiles only) |
| Project facts in genre profiles | **Forbidden** |
| Chinese regex/terms in genre profiles | **Forbidden** (language packs only) |
| `SCRIPT_VERSION = "v1.1.1-generic"` | **Fixed** — always synced with release tag |
| `--engine 1` | **Still available** (v1 reader) |
| `gdd-audit` v1 output | **Still generated** when `--engine 1` |
| v1→v2 migration | `gdd-profile-validate` + manual review |

### Support Period

- v1 reader and migrator will be maintained through v2.x.
- Earliest possible removal of v1 support: **v3.0.0**.
- v2.x will NOT drop v1 compatibility.

---

## 11. Migration Path (v1 → v2)

1. Run `gdd-profile-validate --kind project Project_Profile.yaml`
2. Add `profile_type: project` to your project profile
3. Add `profile.language` to your project profile's `profile:` block
4. Move any `enabled_docs` from genre profile to project profile
5. Keep existing `consistency_checks` and `boundary_checks` in project profile (v2.1 will add `project_fact_checks`/`language_pack` runtime consumption)
6. Re-run `gdd-audit` with `--engine 2` (default since v2.0)
7. Verify EQUIVALENT with v1 baseline

---

## Version Gate

- **v1.9.0**: Contract freeze. No new features.
- **v2.0.0-rc**: Default switch. `--engine 2` default, scaffold v2 safety, profile_type required.
- **v2.0.0**: Formal release. v1 reader retained. Full engine pipeline (Finding/Waiver/State/Report) → v2.1.
- **v2.1**: Engine v2 complete — WaiverManager, StateManager, Report v2 wired into audit chain.

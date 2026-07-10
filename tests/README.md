Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Tests

## Quick run

```
cd game-design-doc-governance/tests
pip install pyyaml pytest
python -m pytest -v
```

CI runs the same command (`pip install pyyaml pytest && python -m pytest -v`).

## Fixtures (self-contained, 6 projects)

| Fixture | Path | What it tests |
|---|---|---|
| `sample_open_world` | `fixtures/sample_open_world/` | Marker-based STYLE parsing + anchor/no-REF P3 regression |
| `minimal_zh_fallback` | `fixtures/minimal_zh_fallback/` | Chinese heading fallback path (no AUDIT markers) |
| `broken_boundary` | `fixtures/broken_boundary/` | boundary_checks catch event-body / weapon-stat leaks |
| `versioned_filename` | `fixtures/versioned_filename/` | `find_latest` / `check_file_list` with `(n)` naming; excludes `_TEMPLATE`/`_BACKUP`/`_OLD` |
| `issue_state` | `fixtures/issue_state/` | `issue_state.jsonl` suppression (ACCEPTED_EXCEPTION / FALSE_POSITIVE) |
| `strict_mode` | `fixtures/strict_mode/` | `--strict` / `--pedantic` / `--fail-on-p2` gate behaviour |

## Expected baselines

Located in `expected/`. Each `.json` file mirrors the known-good counts for one
fixture. The pytest integration tests assert against these baselines.

## Primary regression

The self-contained `sample_open_world` fixture is the primary regression source
(no external project dependency). Run with `--no-state`:

```
python ../tools/global_doc_audit.py \
  --root     "fixtures/sample_open_world/md file" \
  --style     "fixtures/sample_open_world/md file/STYLE_GUIDE.md" \
  --profile  "fixtures/sample_open_world/md file/Project_Profile.yaml" \
  --out      "<temp audit dir>" \
  --baseline "expected/sample_fixture_baseline.json" \
  --no-state
```

## Secondary regression (optional, real-world)

The origin `open_world_narrative_tactical_shooter` project baseline
(`expected/current_project_baseline.json`) is kept as an optional secondary
regression. It depends on an external real-project path and is not required for
CI.

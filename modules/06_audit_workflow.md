Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 06 - Audit Workflow

The auditor (`tools/global_doc_audit.py`) verifies structure and consistency. It
flags; humans decide. It is never a design authority.

## 1. Audit order

```
1. file-list check (expected authority docs present; note non-authority files)
2. table structure (column counts; HTML comment between table rows)
3. anchors (authority presence; FACT/RULE missing REF)
4. deprecated terms (with negation-context exemption)
5. cross-document links (broken links to non-existent docs)
6. boundary_checks   (from Profile)
7. consistency_checks (from Profile)
8. apply exceptions  (registered waivers)
9. write report.md + report.json; append history.md
10. optional: compare against --baseline
```

## 2. Issue levels

| Level | Meaning | Gate |
|---|---|---|
| P0 | Blocking: fact/authority conflict, missing authority doc, audit can't run | Must fix; cannot pass |
| P1 | High: deprecated setting remains, wrong-authority link, boundary confusion, anchor with no authority | Must fix; cannot pass |
| P2 | Medium: format/table/REF-position issues; blocks only in strict mode | Human judgement (strict = fix) |
| P3 | Advisory: traceability, naming candidates, low-risk REF suggestions | Non-blocking |
| INFO | Informational: non-authority file present, skipped items | None |

Pass = `P0 == 0 and P1 == 0`. With `--strict` / `--pedantic` / `--fail-on-p2`,
also require `P2 == 0` (the profile's `audit.fail_on_p2_in_strict_mode` can relax
this; `audit.fail_on_p0` / `fail_on_p1` can relax P0/P1 gating).

## 3. Issue IDs and states

- Stable ID: `AUD-{LEVEL}-{md5(file|rule|message)[:8]}` - same issue keeps the same ID.
- States (P1 predefines the `status` field; full flow implemented in P3 via
  `issue_state.jsonl`):

```
OPEN                  detected this run
FIXED_PENDING_VERIFY  changed, awaiting next audit
VERIFIED              confirmed gone on next audit
FALSE_POSITIVE        human-confirmed false alarm
ACCEPTED_EXCEPTION    registered waiver (see Profile exceptions)
REOPENED              was fixed, appeared again
```

## 4. Outputs

- `audit_report.md` - latest snapshot (overwritten).
- `audit_report.json` - machine result: counts, issues, loaded-rule counts.
- `audit_history.md` - appended each run (trend over time).
- `issue_state.jsonl` - per-issue lifecycle ledger; suppresses FALSE_POSITIVE /
  ACCEPTED_EXCEPTION issues from the counts on later runs (`--no-state` opts out).

## 5. Regression baseline

When changing the engine or a profile, run against a known-good project with
`--baseline <expected.json>`. The auditor prints `EQUIVALENT` / `DIVERGED` and
fails the run on divergence. See `tests/`.

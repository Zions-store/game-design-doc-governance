# Audit Reference

The generic auditor (`gdd-audit`) verifies structure and cross-document
consistency. It flags; humans decide.

## Command

```bash
gdd-audit --root <md dir> --style <STYLE_GUIDE.md> \
          --profile <Project_Profile.yaml> --out <audit dir> \
          [--strict] [--pedantic] [--fail-on-p2] [--no-state] [--baseline <json>]
```

## Rule sources

| Source | Provides |
|---|---|
| `STYLE_GUIDE.md` | Document list, anchor registry, deprecated-term registry |
| `Project_Profile.yaml` | `enabled_docs`, `boundary_checks`, `consistency_checks`, `exceptions`, thresholds |

## Audit order

1. File-list check - are all expected authority docs present?
2. Table structure - column counts, HTML comments between rows.
3. Anchors - authority present? FACT/RULE missing `REF:`?
4. Deprecated terms - with negation-context exemption.
5. Cross-document links - broken links to non-existent docs.
6. `boundary_checks` (from profile) - content leaking into the wrong doc.
7. `consistency_checks` (from profile) - core facts wrongly stated.
8. Apply `exceptions` (registered waivers).
9. Write `audit_report.md` + `audit_report.json`; append `audit_history.md`;
   update `issue_state.jsonl`.
10. Optional: compare against `--baseline`.

## Issue levels

| Level | Blocks pass? | Typical cause |
|---|---|---|
| **P0** | Always | Fact/authority conflict, missing authority doc |
| **P1** | Always | Deprecated setting, broken link, boundary confusion, anchor without authority |
| **P2** | Only in `--strict`/`--pedantic`/`--fail-on-p2` | Format, table, REF position issues |
| **P3** | Never | Traceability, naming suggestions |
| **INFO** | Never | Non-authority file present |

Pass = P0==0 and P1==0 (plus P2==0 for strict modes).

## Output files

- `audit_report.md` - latest snapshot (overwritten).
- `audit_report.json` - machine result: counts, issues, loaded-rule counts.
- `audit_history.md` - appended each run.
- `issue_state.jsonl` - per-issue lifecycle: `OPEN / FIXED_PENDING_VERIFY /
  VERIFIED / FALSE_POSITIVE / ACCEPTED_EXCEPTION / REOPENED`. Issues marked
  FALSE_POSITIVE / ACCEPTED_EXCEPTION are suppressed from counts.

## Useful options

- `--no-state` - skip reading/writing `issue_state.jsonl` (use for baseline
  regression).
- `--baseline <json>` - compare P0-P3 counts against a known-good baseline;
  prints EQUIVALENT / DIVERGED.
- `--strict` / `--pedantic` / `--fail-on-p2` - gate P2 to block pass.

For the full audit workflow see `modules/06_audit_workflow.md`.

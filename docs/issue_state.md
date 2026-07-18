# Issue State Tracking

Every issue reported by `gdd-audit` carries a stable ID:
`AUD-{level}-{md5(file|rule|msg)[:8]}`. The same issue keeps the same ID across
runs.

## `issue_state.jsonl`

A JSON-lines file in the audit directory. Each line is one issue:

```json
{"issue_id": "AUD-P3-d33cd196", "status": "OPEN", "level": "P3",
 "file": "RULE-NAMING-FACT-BOUNDARY", "msg": "RULE anchor has no REF",
 "reason": "", "updated_at": "2026-07-09 12:00"}
```

## States

| State | Meaning |
|---|---|
| `OPEN` | Detected this run |
| `FIXED_PENDING_VERIFY` | Changed, awaiting next audit |
| `VERIFIED` | Confirmed gone on next audit |
| `FALSE_POSITIVE` | Human-confirmed false alarm |
| `ACCEPTED_EXCEPTION` | Registered waiver (will not re-alarm) |
| `REOPENED` | Was fixed, appeared again |

## Suppression

Issues marked `FALSE_POSITIVE` or `ACCEPTED_EXCEPTION` are **suppressed from the
counts** on subsequent runs (they appear as "suppressed" in the report but do not
affect P0-P3 totals). Use `--no-state` to skip state tracking entirely (useful
for baseline regression, where you want the raw counts).

## Manual workflow

1. Run `gdd-audit` normally (with state tracking on by default).
2. Review the report. For issues you accept as exceptions, edit
   `issue_state.jsonl` and change `status` to `ACCEPTED_EXCEPTION`, adding a
   `reason`.
3. Re-run `gdd-audit`. The accepted issue will be suppressed.

In addition, a profile-level `exceptions` field allows registering waivers
declaratively in `Project_Profile.yaml`. See `docs/profile_schema.md`.

> **v2.1 behavior**: `--engine 2` applies structured file-scoped waivers before
> counting findings, reports active and expired waivers, and uses stable Finding
> IDs for state suppression. `--engine 1` retains the legacy exception path for
> compatibility.

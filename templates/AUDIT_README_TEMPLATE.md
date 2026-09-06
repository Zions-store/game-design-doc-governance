<!-- Copyright (C) 2026 ZionXiaoxiSuOGLocGo -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Audit Directory

This directory holds the **audit products** of `gdd-audit`. They are governance
records, not design authority — never edit design documents based on a report
without going through the project's change process.

## Files

| File | Nature | Purpose |
|---|---|---|
| `audit_report.md` | Snapshot | Latest run only (overwritten). Human-readable summary + issue list. |
| `audit_report.json` | Snapshot | Machine result: counts, issues, loaded-rule counts, boundary coverage. |
| `audit_history.md` | Append-only | One block per run (run ID, engine, script, counts). Never edited. |
| `issue_state.jsonl` | Ledger | Per-issue lifecycle (`OPEN` → `FIXED_PENDING_VERIFY` → `VERIFIED`, `FALSE_POSITIVE`, `ACCEPTED_EXCEPTION`, `REOPENED`). |

## Conventions

- `audit_history.md` and `issue_state.jsonl` are append-only; corrections are
  made by re-running the audit, never by rewriting history.
- `FALSE_POSITIVE` / `ACCEPTED_EXCEPTION` entries suppress their issue from
  future counts (`--no-state` opts out; use it for baseline regression).
- Prefer profile-level `exceptions` (with `reason` / `expires`) over manual
  `issue_state.jsonl` edits.

Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 10 - Workflow & Session Documents

Design documents are not the only files a governed project produces. Around
them lives a **workflow layer** — agent instructions, state snapshots, logs,
session records, handoff files and long-lived ledgers. This module defines
their lifecycle so the audit and the AI can reason about them.

## 1. The seven workflow shapes

| Shape | Examples | Lifecycle | Authority |
|---|---|---|---|
| Agent instructions | `AGENTS.md` | Living; edited when rules change | Rules for agents, not design facts |
| State snapshot | `PROJECT_STATE.md`-style | Refreshed per session; "now" tense | Progress/parameters only; never design truth |
| Append-only log | `DEVLOG.md`-style | Append; **recorded entries are never edited** | Evidence (commits, audit results), not plans |
| Execution list | `TODO.md`-style | Items checked off; AI-proposed items need explicit user confirmation | What to do next, sourced from decisions |
| Session record | `prompts.md`-style | Append; user wording verbatim, assistant replies compressed | Process history; never a design source |
| Handoff file | per-session, archived after consumption | Create only when a new session must continue unfinished work | Navigation index, not a copy of content |
| Long-lived ledger | nested decision registries | Permanent; every entry dated; IDs never reused | Where each problem came from and how it nests |

## 2. Rules

1. **Append-only discipline**: before appending to an append-only file, verify
   the tail anchor of the previous entry; prefer true end-append over
   insert-in-place. Corrections to history are made by appending a correction
   note, never by rewriting the original entry.
2. **Never cite line numbers** in append-only files (they drift). Cite
   document name, date + title, or section number.
3. Workflow files are **non-authority**: they never serve as a design source.
   Register them (or their directory) in `non_authority_files` /
   `link_checks.ignored_dirs` so they do not pollute audits.
4. **State snapshots** are updated at session end; logs at task end; handoff
   files only at session interruption (context limits) — and are archived once
   consumed, with stale conclusions marked or removed.
5. **Sync contract**: when a governance-relevant change happens (release,
   rule change, audit closure), define an explicit sync list (which workflow
   files must be touched) and complete it in the same batch — partial syncs
   are how contradictions are born.

## 3. Why this is a module and not engine code

These files are human/agent process artifacts; structural audits cannot
verify their semantics. The engine's role is limited to *not tripping over
them* (rule 3). Consistency of the workflow layer itself is maintained by the
sync contract and by semantic review (module 11).

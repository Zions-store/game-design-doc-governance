Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 12 - Decision Governance

Audits govern *documents*; this module governs *decisions* — the moments
where a design fact is settled. Origin-project incidents (a proposal mistaken
for a settled fact survived three sessions) are why these rules exist.

## 1. Proposal vs. decision

- A **recommendation** (⭐ or "suggested") is never a decision. Only the
  project owner **confirms**; the marker for a confirmed decision is ✔️
  (or an explicit equivalent).
- Before any decision point, present **decision material**: options,
  consequences, a recommendation, numbered decision points (D1, D2, ...).
  Decide item by item; record the ruling with each item.
- AI-proposed TODO items enter the execution list **only after per-item user
  confirmation**; rejected items are removed, not parked as comments.

## 2. Three-tier completion marks

| Mark | Meaning |
|---|---|
| ✔️ decided | The user has ruled (decision layer terminal state) |
| ✅ written | The change has been written into the authority document |
| 📦 complete | Decided + written + verified (audit/chain check) |

Process states: 🔴 discussing, ⭐ recommended (not decided), 🔲 not started,
⚠️ parked. "Settled" wording is avoided in status names — one word, one
meaning.

## 3. Change-side discipline (chain impact)

Confirming a fact is never a one-file edit. Before writing:

1. list every document that references, summarizes or depends on the fact
   (impact list — grouped into: must write / must update old wording /
   confirmed-unaffected);
2. same-batch execution — no single-file "quick fixes" of confirmed facts;
3. search old wording **including word-order variants** (a deprecated phrase
   reworded by one character escapes a literal match);
4. re-run the audit immediately after the batch;
5. after each work segment, re-walk the impact list and repair gaps.

## 4. Deferral (backlog) — not a waiver

Some fixes wait for a future decision or workflow stage. A **backlog entry**
records: what, why deferred, which future stage consumes it, date. This is
deliberately different from the engine's `exceptions` waiver (an accepted,
possibly expiring suppression of a *known finding*): a backlog item is *work
not yet done*, tracked in the workflow layer, and it never silences an audit
finding on its own.

## 5. Provenance (where did this problem come from)

Long projects forget why a rule exists. Keep a decision registry (can be a
section of a workflow ledger, module 10): each problem nests under the
discussion that spawned it; IDs are never reused; merged items keep their ID
with a "merged into" note. Query path: *why does this exist* → registry;
*what is the current status* → state snapshot; *what runs next* → execution
list.

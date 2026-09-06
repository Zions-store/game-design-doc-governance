<!-- Copyright (C) 2026 ZionXiaoxiSuOGLocGo -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Semantic Audit Batch — Working Template

Companion to `modules/11_semantic_audit.md`. Copy the tables below into the
project's workflow log (never into authority documents) when running a
semantic audit round. The engine audit (`gdd-audit`) verifies structure;
this template organizes what only reading agents can judge.

## 1. Batch plan

Derive batches from the project's own document set — do not copy another
project's batch table. Group by theme domain (2-3 documents per batch),
highest-risk documents first, collectibles and other low-risk documents last.

| Batch | Documents | Reading agent | Status |
|---|---|---|---|
| 1 | Narrative_Bible.md, Design_Document.md | agent A | pending |
| 2 | World_Design.md, Mission_Design.md | agent B | pending |

## 2. Per-document output shape (every reading agent uses this)

- _Reading status_: fully read, positioned at the document's final section,
  N lines in M passes (the main session spot-checks; a batch with skipped
  sections is returned for re-reading).
- _Core-settings summary_: setting → what it establishes.
- _Dimension A (internal semantics)_ table: # / section / issue type /
  description / quoted evidence / P-level / suggestion.
- _Dimension B (vs. settled conclusions)_: drift against the rewritten
  baseline (rewritten chapters, registered facts, anchors).
- _Dimension C (cross-document, collected not judged locally)_: the same
  fact as stated in other documents.
- _Statistics_: A/B/C counts by P-level.

## 3. User checkpoint 1 — after reading, before comparison

For each document: 1-2 lines of core findings + A/B/C counts. Confirm the
reading directions are right before they propagate into Stage 2 comparison.

## 4. Stage 2 — cross-document comparison (main session only)

Compare collected C-items, anchor chains, deprecated-term sweeps (including
word-order variants) and timeline consistency. For every conflict decide who
is authoritative. Output per conflict: document A section vs. document B
section / difference / authority / P-level / suggestion.

## 5. User checkpoint 2 — ruling on the merged list

Every item gets exactly one ruling: fix now / fix after a pending decision
is settled / defer to a named later workflow stage (backlog, module 12) /
accept as-is. The main session registers all findings in one global
numbering sequence; reading agents never assign global IDs.

## 6. Closure

After fixes land, rerun `gdd-audit` — the round is done when P0/P1 are zero
and every deferred item is registered in the backlog. Engine-clean is not
semantically clean; semantic-clean is not engine-clean: you need both.

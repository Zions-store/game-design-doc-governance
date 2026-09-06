Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 11 - Semantic Audit Orchestration

The engine audit (module 06) verifies **structure**: file lists, anchors,
deprecated keywords, regex boundaries, links. It cannot read meaning. Three
failure classes survive it — and they are the most expensive ones:

- internal contradictions inside one authority document (e.g. a timeline that
  disagrees with itself ten chapters apart);
- drift between a rewritten authority and documents that were not rewritten;
- semantic direction errors (right words, wrong meaning).

Origin-project case: an authority "Bible" had two chapters assigning mutually
exclusive dates to the same event; every structural audit passed; only a
cross-document semantic comparison caught it. Treat this module as mandatory
for any large rewrite or pre-release closure.

## 1. Two-stage model

1. **Stage 1 — per-document reading** (parallel sub-agents): every target
   document read **line by line** (no sampling) against three dimensions:
   - **A — internal semantics**: undefined references, self-contradiction,
     sections marked "pending" whose content already exists, broken reasoning.
   - **B — vs. settled conclusions**: drift against the current authority
     baseline (rewritten chapters, registered facts, anchors).
   - **C — cross-document consistency**: the same fact stated differently in
     two documents (collected for Stage 2, not judged locally).
2. **Stage 2 — cross-document comparison** (main session): only the main
   session holds every document's context. Compare collected C-items plus
   anchor chains, deprecated-term sweeps (including word-order variants!) and
   timeline consistency; resolve who is authoritative per conflict.

## 2. Orchestration rules

- Batch documents by theme domain (2-3 documents per sub-agent batch); collectibles and other low-risk docs last.
- Each reading agent must prove completeness: state "fully read, positioned at
  the document's final section, N lines in M passes" — main session
  spot-checks and **returns any batch with skipped sections**.
- Uniform output per document: findings table (#/section/type/quote evidence/
  P-level/suggestion), suspicious-points table, A/B/C counts.
- **Numbering discipline**: sub-agents never assign global IDs; the main
  session registers findings in one global sequence.
- Two user checkpoints: (1) after Stage 1 — confirm reading directions before
  they propagate into comparison; (2) after the merged list — user rules on
  every item (fix / defer / accept as-is).
- Resolve every finding into buckets: **fix now / fix after a pending decision
  is settled / defer to a named later workflow stage** (the deferral bucket is
  a backlog, not a waiver — see module 12).

## 3. Closure

The engine audit is the objective gate: after semantic fixes land, rerun
`gdd-audit` — semantic work is done when P0/P1 are zero **and** the deferred
bucket is registered. Engine-clean ≠ semantically clean; semantic-clean ≠
engine-clean. You need both.

Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 05 — Anchors & Change Safety

Prevents the classic failure: change a setting in one document, forget to update
the copies elsewhere. Five layers, all recorded in `STYLE_GUIDE.md`.

## 1. Five-layer change-safety mechanism

1. **Authority matrix** — who is the single owner of each fact (Module 04).
2. **Change-type classification** — is this a fact / term / rule / parameter change?
3. **Anchors** — stable IDs for high-risk cross-document facts.
4. **Deprecated registry** — replaced settings/terms that must not revive.
5. **Change checklist** — the procedure to run before/after a cross-doc edit.

## 2. Anchor types

Stable IDs for facts that recur across documents. Supported prefixes:

```
FACT- TERM- RULE- PARAM- FLOW- RESOURCE- COLLECTIBLE-
PROGRESSION- ECONOMY- MULTIPLAYER- LIVEOPS- UI- TECH-
```

## 3. Usage

- **Authority location** uses the raw anchor as an HTML comment:
  `<!-- FACT-PROTAGONIST-ORIGIN -->`
- **Reference locations** (summaries, script, missions, delivery) use `REF:`:
  `<!-- REF: FACT-PROTAGONIST-ORIGIN -->`
- High-risk facts that recur **must** have an anchor; low-risk local content need not.
- Anchors do not replace prose; they exist for search, sync and audit.
- To change an anchored fact: full-text search the anchor ID, update every hit.

The auditor loads the anchor registry from STYLE_GUIDE §"anchor registry" and flags
anchors with no authority occurrence (P1), FACT with no REF (P2), RULE with no REF (P3).

## 4. Deprecated registry

```md
| Deprecated | Correct now | Type | Keyword | Search scope |
|---|---|---|---|---|
```

Rules: keywords must be specific; broad keywords need a context condition;
deprecated wording must not appear in authority prose except explicitly marked as
"old/incorrect/deprecated". A remaining deprecated setting is at least P1; a fact
conflict is P0. The auditor skips hits near negation words (`不是/并非/deprecated/…`).

## 5. Change checklist (before editing a cross-document setting)

1. Classify the change (fact / term / rule / parameter).
2. Find the authority document.
3. List impacted documents (summaries, script, missions, delivery, naming).
4. Search for the old wording (deprecated keywords).
5. Search for the anchor ID and update every reference.
6. Run the audit; drive P0/P1 to zero before claiming done.

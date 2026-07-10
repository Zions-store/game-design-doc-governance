Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 04 - Authority & Boundaries

## 1. Authority matrix

Every project maintains a table mapping content types to their single owner:

```md
| Content type | Authority doc | May reference | Must NOT store |
|---|---|---|---|
| Gameplay numbers | Gameplay_Systems.md | GDD summary / Character narrative meaning | Character must not store numbers |
| Mission/event body | Mission_Design.md | World mounts it / Script performs it | World must not write mission body |
| World map structure | World_Design.md | Mission references regions | Mission must not define map layout |
| World truth / faction logic | Narrative_Bible.md | Script/Mission reference | Script must not be the truth library |
| Concrete performance/dialogue | Narrative_Script.md | Bible provides the facts | Script must not own world truth |
| Resource / economy | Resource_And_Economy.md | Mission uses as cost | Collectibles must not hold ordinary resources |
| Narrative collectibles | Collectibles_Design.md | Pipeline delivers, Mission triggers | Must not hold economy resources |
| Names / terminology | Naming.md | All docs use | Others do not invent names |
```

Adapt rows to the enabled documents of the chosen Profile.

## 2. High-risk boundaries (audit focus)

These pairs are where content tends to leak; declare them in the Profile's
`high_risk_boundaries` and enforce with `boundary_checks`:

- **GDD vs sub-document** - GDD summarises; body lives in sub-docs.
- **Mission vs World** - Mission = what happens / choices / consequences;
  World = where it is placed / density.
- **Narrative Bible vs Script** - Bible = objective truth; Script = how it is
  discovered, misread, performed.
- **Character vs Gameplay** - Character may state a mechanic's narrative meaning;
  Gameplay owns the numbers.
- **Resource vs Collectibles** - resources/materials/economy vs narrative relics.
- **Naming vs Fact** - Naming owns "what it is called and why"; Bible owns
  "what it is in the world".

## 3. Cross-reference rules

- Every cross-document reference points to the **authority** document.
- When content is moved, its old references must be updated.
- Non-authority records (history/snapshots) are never cited as a design source.
- Prefer `[Doc.md](Doc.md)` links; the auditor flags links to non-existent docs.

## 4. Character-vs-numbers rule (common trap)

Character sheets may say "this weapon defines the character"; they must not carry
`22 damage / 150% HP`. Numbers link back to `Gameplay_Systems.md`. The
`CHAR-NO-WEAPON-STATS` boundary check enforces this.

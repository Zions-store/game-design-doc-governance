<!-- Copyright (C) 2026 ZionXiaoxiSuOGLocGo -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# {{PROJECT_NAME}} - Content Authority Matrix

> Single source of truth per content type. Lives in STYLE_GUIDE §4; this template is
> the fill-in shape. Each content type has exactly one authority document.

| Content type | Authority document | May reference | Must NOT store |
|---|---|---|---|
| {{CONTENT_TYPE}} | {{AUTHORITY_DOC}} | {{MAY_REFERENCE}} | {{FORBIDDEN_LOCATION}} |

Example rows (adapt to the Profile's `enabled_docs`):

| Content type | Authority document | May reference | Must NOT store |
|---|---|---|---|
| Gameplay numbers | Gameplay_Systems.md | GDD summary; Character narrative meaning | Character must not store numbers |
| Mission/event body | Mission_Design.md | World mounts; Script performs | World must not write mission body |
| World map structure | World_Design.md | Mission references regions | Mission must not define map layout |
| World truth / faction logic | Narrative_Bible.md | Script/Mission reference | Script must not be the truth library |
| Concrete performance/dialogue | Narrative_Script.md | Bible provides facts | Script must not own world truth |
| Resource / economy | Resource_And_Economy.md | Mission uses as cost | Collectibles must not hold ordinary resources |
| Narrative collectibles | Collectibles_Design.md | Pipeline delivers; Mission triggers | Must not hold economy resources |
| Names / terminology | Naming.md | All docs use | Others do not invent names |

## High-risk boundaries
List the pairs where content tends to leak (from the Profile's
`high_risk_boundaries`) and enforce each with a `boundary_check` in the Profile.

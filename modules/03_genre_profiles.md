Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 03 — Genre Profiles

Different game types need different documents. A **genre profile** (`profiles/*.yaml`)
declares a recommended document set, high-risk boundaries and audit focus for one
game type. Pick one to start a project; enable the recommended docs plus any needed
optional docs.

## 1. Two profile shapes

| Shape | Fields | Used by |
|---|---|---|
| **Genre profile** (type library) | `recommended_docs` / `optional_docs` / `disabled_docs` / `high_risk_boundaries` / `audit_focus` / `suggested_doc_modules` | Choosing a document set for a new project |
| **Project profile** (instance) | `enabled_docs` + `boundary_checks` / `consistency_checks` / `exceptions` / thresholds | The auditor at run time |

To instantiate: take a genre profile's `recommended_docs` (+ chosen `optional_docs`),
write them into a project's `Project_Profile.yaml` `enabled_docs`, then add that
project's data rules. `open_world_narrative_tactical_shooter.yaml` ships as both — a
genre entry **and** the instantiated regression fixture (it carries `enabled_docs`
and data rules in addition to `recommended_docs`).

## 2. Genre matrix

| Genre | Core recommended | Notable optional | Disabled | Top boundary |
|---|---|---|---|---|
| open_world_narrative_tactical_shooter | Bible / Script / Pipeline / Mission / World / Character / Gameplay / Resource / Collectibles | Level / Encounter / Progression | Multiplayer / LiveOps / Monetization | Mission vs World |
| open_world_rpg | Bible / Quest / World / Character / Faction / Gameplay / Progression / Resource / Item / Dialogue | Encounter / Collectibles | Multiplayer / LiveOps | Quest vs Dialogue |
| linear_action_adventure | Bible / Script / Level / Encounter / Gameplay / Character / UI_UX | Collectibles / Pacing | Multiplayer / LiveOps / Resource | Script vs Level |
| multiplayer_shooter | Gameplay / Weapon_Balance / Map / Multiplayer / Progression / UI_UX / Technical | LiveOps / Monetization | Narrative_Script / Pipeline / Collectibles | Weapon Balance vs Gameplay |
| survival_crafting | Gameplay / Resource / Crafting / World / Progression / Base_Building / AI_Creature / UI_UX | Narrative_Bible | LiveOps / Monetization | Resource vs Crafting |
| roguelite | Gameplay / Run_Structure / Progression / Item / Enemy / Level_Generation / Meta_Progression / UI_UX | Narrative | Multiplayer | Run vs Meta |
| strategy_simulation | Gameplay / Economy_Simulation / AI_Systems / Faction / Unit / Tech_Tree / Map / UI_UX / Technical | Narrative | LiveOps | Unit vs Tech Tree |
| puzzle_adventure | Puzzle / Level / Narrative_Script / Interaction / UI_UX | Collectibles | Multiplayer / Resource | Puzzle Logic vs Level Layout |
| horror_narrative | Bible / Script / Level / Encounter / Audio / Pacing / Collectibles / UI_UX | — | Multiplayer / LiveOps | Script vs Level |
| liveops_mobile | Gameplay / Resource / Progression / LiveOps / Monetization / Event / UI_UX / Technical | — | Narrative_Script / Collectibles | Economy vs Monetization |

All genres also enable the universal layer: `Design_Document.md`, `STYLE_GUIDE.md`,
`Naming.md`, and a `Project_Profile.yaml`.

## 3. Choosing and extending

- Match the game's primary type; add secondary types for hybrids.
- Enable `optional_docs` only when the game actually needs them (avoid over-design).
- A genre-specific doc without a `doc_modules/` skeleton yet (e.g. `Weapon_Balance.md`)
  is still listed in `recommended_docs`; its skeleton can be added later.
- `suggested_doc_modules` points at the `doc_modules/*.tmpl` skeletons to scaffold.

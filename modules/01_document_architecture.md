Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 01 — Document Architecture

How to decide *which* documents exist and *what each one owns*.

## 1. Lifecycle types

| Type | Example | Role |
|---|---|---|
| Index authority | `Design_Document.md` (GDD) | Overview + summaries + links only |
| Full-volume authority | `Gameplay_Systems.md`, `Mission_Design.md`, … | The single owner of one content domain |
| Rule authority | `STYLE_GUIDE.md` | The constitution: structure, boundaries, audit rules |
| Snapshot | `*.docx` / `*.pdf` exports | Human-readable render; never a design source |
| History | prompt logs / discussion records | Non-authority record |
| Scratch | temporary notes | Must migrate into an authority doc once resolved |

## 2. Four principles

1. **Single authority** — one kind of content, one authority document.
2. **Content ownership beats appearance** — a thing appearing in doc X does not
   make X its owner (an event on the map is owned by Mission, not World).
3. **Summaries may repeat, bodies may not** — a one-line summary + link is fine;
   maintaining the same full table/section in two docs is forbidden.
4. **Full-volume first** — *light content is OK; light structure is not.* Every
   authority doc is built to its final shape from day one; unfinished sections use
   a `🔲 TODO` placeholder. No `misc / other / global rules` catch-all buckets.

## 3. GDD vs sub-documents

The GDD answers "what parts does this game have"; it holds project positioning,
pillars, and *summaries* of each system with links. It never holds full parameter
tables, full mission bodies, full event libraries, full character sheets, full
world-truth libraries, or full scripts. Those live in the corresponding authority
sub-document.

## 4. Before adding a new document — ask five questions

1. Is this an independent authority domain, or a chapter of an existing doc?
2. Would it cause over-fragmentation?
3. Does it have long-term maintenance value?
4. Does it need a full-volume skeleton?
5. Is it registered in STYLE_GUIDE?

If in doubt, prefer a new chapter in an existing authority doc over a new file.

## 5. Document header

Each authority doc's header states its **final** responsibility (what it owns and
what it does not own), not merely its current content. This keeps the boundary
stable while the content grows.

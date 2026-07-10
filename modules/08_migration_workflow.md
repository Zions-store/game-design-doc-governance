Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 08 - Migration Workflow

When a project already has an old GDD or scattered documents, migrate it into the
governed structure instead of rewriting from scratch.

## 1. Steps

```
1.  Read the existing files.
2.  Identify content types (world / mission / world-map / gameplay / economy / ...).
3.  Build the target document list from the chosen genre Profile.
4.  Build the authority matrix (who owns what).
5.  Mark old / pending settings (deprecated registry candidates).
6.  Create anchors for high-risk recurring facts.
7.  Migrate body text into its authority document.
8.  Replace the GDD's full bodies with summaries + links.
9.  Fix cross-document links to point at the new authorities.
10. Run the audit.
11. Register remaining legacy issues (deprecated terms, TODOs).
```

## 2. Forbidden during migration

- Copying full text verbatim into a new document (without classification).
- Splitting before content is classified.
- Maintaining the old body and the new body at the same time.
- Not updating STYLE_GUIDE when a document's responsibility changes.
- Not registering deprecated wording.

## 3. Order matters

Migrate one content domain at a time, run the audit, drive P0/P1 to zero, then move
to the next. This is exactly how the origin project was migrated (world truth →
Bible, events → Mission, resources → Resource, mounts → World), and it kept each
step verifiable.

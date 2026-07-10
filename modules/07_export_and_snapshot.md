Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 07 - Export & Snapshot

`.docx` / `.pdf` / any export are **human-readable renders, never design sources**.
The `.md` authority documents are the only source of truth.

## 1. Rules

- Always edit the `.md` first; regenerate exports from it.
- Exports are read-only; never edit an export and hope it flows back.
- An export must not be referenced as an authority by any design document.
- Record the export time / source; export only after structure is stable.

## 2. Recommended layout

```
Design Document/
  md file/        # authority sources
  export/         # non-authority snapshots
    Design_Document_YYYYMMDD.docx
    Design_Document_YYYYMMDD.pdf
```

## 3. Snapshot record

Keep a small table so a snapshot can be traced to its source state:

```md
| Snapshot file | Source commit / audit ID | Time | Passed audit? |
|---|---|---|---|
```

## 4. Tooling

A one-to-one `.md → .docx` converter (with per-file table-count parity and orphan
deletion) is a good snapshot tool. Generate the whole set after a review round, not
mid-edit. The audit's `ignored_dirs` should list `export/` so snapshots are never
scanned as authority.

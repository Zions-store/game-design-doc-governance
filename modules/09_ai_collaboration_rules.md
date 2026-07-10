Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 09 - AI Collaboration Rules

Rules for an AI agent editing a governed document set, so it does not create new
inconsistencies while "helping".

## 1. Before editing - confirm

- Which change type is this (fact / term / rule / parameter)?
- Which document is the authority?
- Which documents are impacted (summaries, script, missions, delivery, naming)?
- Which old keywords must be searched (deprecated registry)?
- Which anchors must be synced?
- Does STYLE_GUIDE need updating (a responsibility change)?
- Does the Project Profile need updating (a new rule / doc)?

## 2. Must NOT

- Turn the GDD into a full-text repository.
- Write a full body into a non-authority document.
- Create new documents ad hoc (check Profile + STYLE first).
- Bypass STYLE to change a boundary.
- Rewrite a deprecated setting back into authority prose.
- Treat the audit report as design authority.
- Add REF anchors just to clear a P3 warning.

## 3. After editing - do

- State the scope of the change.
- List impacted documents.
- Note whether anchors are involved.
- Note whether deprecated terms are involved.
- Suggest running the audit.
- Judge pass/fail from the report (P0/P1 must be zero), not from intent.

## 4. Golden rule

Instructions say *what*, not *how*. "Add X" does not mean "skip the boundary
checks". A change is done only when the audit confirms it, not when the text is
written.

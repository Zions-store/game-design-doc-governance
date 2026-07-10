<!-- Copyright (C) 2026 ZionXiaoxiSuOGLocGo -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Cross-Document Change Checklist

> Run this before and after modifying any setting that appears in more than one
> document. Copy one block per change.

## Change: {{CHANGE_TITLE}}

- [ ] **1. Classify** — type: fact / term / rule / parameter → `{{CHANGE_TYPE}}`
- [ ] **2. Authority** — owning document: `{{AUTHORITY_DOC}}`
- [ ] **3. Impact list** — documents that reference this:
      `{{IMPACTED_DOCS}}`
- [ ] **4. Old wording** — search deprecated keywords: `{{OLD_KEYWORDS}}`
- [ ] **5. Anchor** — anchor ID to search & sync: `{{ANCHOR_ID}}`
      (authority uses `<!-- ANCHOR-ID -->`; references use `<!-- REF: ANCHOR-ID -->`)
- [ ] **6. Edit** — update the authority body; update every reference / summary
- [ ] **7. Deprecate** — register any replaced wording in STYLE §6.3
- [ ] **8. Audit** — run `global_doc_audit.py`; drive P0/P1 to zero
- [ ] **9. Done only when the audit confirms** — not when the text is written

### Notes
{{NOTES}}

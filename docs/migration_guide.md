# Migration Guide

Moving an existing GDD (or a scattered set of design documents) into the governed
structure.

## Principle

**Migrate one content domain at a time, audit after each, drive P0/P1 to zero,**
then move to the next. This keeps every step verifiable and prevents a single
overwhelming pile of unverified changes.

## Steps

### 1. Take inventory

List all existing documents and their effective content:
- GDD (the everything-bucket)
- Scattered notes, spreadsheets, wiki pages
- Chat logs / prompt logs (non-authority - do not migrate verbatim)

### 2. Choose a genre profile

Pick the closest profile from `profiles/genre/` and note the `recommended_docs` list.
Scaffold it into a clean directory (`gdd-scaffold`), NOT into the existing
directory (keep the old files for reference during migration).

### 3. Classify content

For each piece of existing content, decide:
- **Authority domain** - what does this body of text *own*? (world truth, mission
  body, gameplay numbers, character identity, naming, etc.)
- **Target document** - map to one of the `enabled_docs`.

### 4. Migrate one domain

Pick the smallest content domain. Copy the text into the target authority
document. Replace any full bodies in the GDD with a one-line summary + link.
Register any old/replaced wording in the deprecated-term registry of
`STYLE_GUIDE.md`.

### 5. Audit

```bash
gdd-audit --root "md file" --style "md file/STYLE_GUIDE.md" \
          --profile "md file/Project_Profile.yaml" --out "audit"
```

Drive P0/P1 to zero before moving to the next domain.

### 6. Add anchors as you go

When a fact appears in more than one document, register it in the anchor registry
and add `<!-- FACT-... -->` / `<!-- REF: ... -->` comments. See
`modules/05_anchor_and_change_safety.md`.

## Forbidden during migration

- Full-text copy-paste into new docs without classification.
- Maintaining the old body and the new body at the same time.
- Skipping the audit step ("I'll audit later" → debt accumulates).

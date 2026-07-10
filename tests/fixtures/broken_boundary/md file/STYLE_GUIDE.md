<!-- Fixture: STYLE with English headings. Boundary rules in profile. -->
# Sample STYLE (broken-boundary fixture)

## 2. Authoritative File List

<!-- AUDIT: ENABLED_DOCS_START -->
| File | Role |
|---|---|
| Design_Document.md | GDD |
| World_Design.md | map |
| Character_Sheets.md | sheets |
| Naming.md | naming |
| STYLE_GUIDE.md | rules |
<!-- AUDIT: ENABLED_DOCS_END -->

## 6. Change-Safety Mechanism

### 6.2 Anchor registry

<!-- AUDIT: ANCHOR_REGISTRY_START -->
| Anchor ID | Setting | Authority | Ref |
|---|---|---|---|
| FACT-BROKEN | dummy | Design_Document.md | World_Design.md |
<!-- AUDIT: ANCHOR_REGISTRY_END -->

### 6.3 Deprecated-term registry

<!-- AUDIT: DEPRECATED_TERMS_START -->
| Deprecated | Correct | Type | Keyword | Scope |
|---|---|---|---|---|
| broken_old | broken_new | term | broken_old | * |
<!-- AUDIT: DEPRECATED_TERMS_END -->

<!-- Sanitized fixture STYLE_GUIDE — uses AUDIT markers (language-independent path). -->
# Sample STYLE_GUIDE (fixture)

Documentation constitution for the self-contained regression fixture.

## 2. Authoritative File List

<!-- AUDIT: ENABLED_DOCS_START -->
| File | Role |
|---|---|
| Design_Document.md | GDD |
| Gameplay_Systems.md | systems |
| Naming.md | naming |
| STYLE_GUIDE.md | rules |
<!-- AUDIT: ENABLED_DOCS_END -->

## 6. Change-Safety Mechanism

### 6.2 Anchor registry

<!-- AUDIT: ANCHOR_REGISTRY_START -->
| Anchor ID | Setting | Authority | Ref |
|---|---|---|---|
| FACT-SAMPLE-ORIGIN | protagonist origin | Design_Document.md | Gameplay_Systems.md |
<!-- AUDIT: ANCHOR_REGISTRY_END -->

### 6.3 Deprecated-term registry

<!-- AUDIT: DEPRECATED_TERMS_START -->
| Deprecated | Correct now | Type | Keyword | Search scope |
|---|---|---|---|---|
| obsolete_sample_term | current_sample_term | term | obsolete_sample_term | * |
<!-- AUDIT: DEPRECATED_TERMS_END -->

## 14. Audit

Run via the generic auditor with this STYLE + the fixture Project_Profile.yaml.
Expected: a single P3 (RULE-SAMPLE-ONLY has no REF), everything else zero.

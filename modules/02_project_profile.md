Copyright (C) 2026 ZionXiaoxiSuOGLocGo
SPDX-License-Identifier: GPL-3.0-or-later
# Module 02 — Project Profile

Every project has one `Project_Profile.yaml`. It declares the document set and the
project's data-driven audit rules. The auditor reads it together with
`STYLE_GUIDE.md`. Full skeleton: `templates/PROJECT_PROFILE_TEMPLATE.yaml`.

## 1. Top-level schema

```yaml
schema_version: 1
profile: {name, description, primary_type, secondary_types[]}
enabled_docs: []          # the authority documents this project maintains
optional_docs: []         # allowed if the game needs them
disabled_docs: []         # explicitly not used
non_authority_files: []   # files that are OK to exist but are not authority
authority: {high_risk_boundaries[], audit_focus[]}
deprecated_terms: []      # optional; project-specific terms usually live in STYLE
audit: {fail_on_p0, fail_on_p1, fail_on_p2_in_strict_mode, require_history, require_json, require_markdown}
file_versioning: {mode, version_pattern, latest_strategy}
boundary_checks: []
consistency_checks: []
link_checks: {enabled, ignored_dirs[]}
exceptions: []
```

## 2. Data-driven rule formats

**boundary_checks** — content that must not appear in the wrong document:

```yaml
- id: CHAR-NO-WEAPON-STATS
  files: [Character_Sheets.md]        # or ["*"] for all (STYLE excluded)
  forbid_regex: '\d+/\s*发'           # OR forbid_any: [word1, word2]
  unless_near: [Gameplay_Systems.md, 数值权威]
  near_window: 200
  stop_at: "[已迁移]"                 # optional: only scan text before this marker
  match: all                          # or first_per_term
  level: P2
  message: "..."
```

**consistency_checks** — a core fact must not be stated wrongly:

```yaml
- id: FACT-PROTAGONIST-NOT-CYBORG
  files: ["*"]
  term: '改造人'
  require_negation_near: [不是, 并非]      # nearby negation = safe
  # require_all_context_near: [尖兵, C]    # only trigger when ALL present
  near_window: 40
  level: P0
  message: "..."
```

**deprecated_terms / exceptions** — replaced terms; and registered waivers
(`{id, file, reason, expires}`) that suppress a known issue.

## 3. How the auditor reads it

```
1. load Project_Profile.yaml
2. load STYLE_GUIDE.md (doc list / anchors / deprecated)
3. enabled_docs = profile.enabled_docs or STYLE list
4. read docs -> generic checks -> profile data rules -> apply exceptions
5. write report/json, append history, optional --baseline compare
```

## 4. What stays out of a shared profile

A **shared genre profile** declares structure and rule *types* only. Project-specific
anchors, deprecated terms and lore live in that project's `STYLE_GUIDE.md`, not in the
shared profile (keeps the Skill genre-general and publishable).

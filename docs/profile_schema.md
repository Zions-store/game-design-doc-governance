# Profile Schema

## Two profile shapes

| Shape | File | Purpose |
|---|---|---|
| **Genre profile** | `profiles/*.yaml` | Recommends a document set for one game type |
| **Project profile** | `Design Document/md file/Project_Profile.yaml` | Carries enabled docs + audit rules for one project |

A genre profile is turned into a project profile by `gdd-scaffold`, or by hand.

## Genre profile fields

```yaml
schema_version: 1          # required
profile:
  name: ""                 # required
  description: ""          # required
  primary_type: ""         # required
  secondary_types: []

recommended_docs: []       # required
optional_docs: []
disabled_docs: []
high_risk_boundaries: []
audit_focus: []
suggested_doc_modules: []
```

## Project profile fields

```yaml
schema_version: 1
enabled_docs: []           # required
optional_docs: []
non_authority_files: []
audit:
  fail_on_p0: true
  fail_on_p1: true
  fail_on_p2_in_strict_mode: true
file_versioning:
  mode: canonical
  version_pattern: "\\((\\d+)\\)"
  latest_strategy: highest_version_suffix
boundary_checks: []
consistency_checks: []
link_checks:
  enabled: true
  ignored_dirs: []
exceptions: []
```

## Data-driven rule formats

**boundary_checks**: catch content that belongs in a different document.

```yaml
- id: CHAR-NO-STATS              # unique
  files: [Character_Sheets.md]   # or ["*"]
  forbid_regex: '\d+/\s*发'      # regex to catch
  # forbid_any: [电池, 药品]     # OR list of literal words
  unless_near: [Gameplay_Systems.md]  # nearby mention = safe
  near_window: 200
  stop_at: "[已迁移]"            # optional: scan only before this marker
  match: all                     # "all" | "first_per_term"
  level: P2
  message: "Weapon stat in character doc without gameplay ref."
```

**consistency_checks**: catch core facts stated incorrectly.

```yaml
- id: FACT-NOT-CYBORG
  files: ["*"]
  term: '改造人'
  require_negation_near: [不是, 并非]
  # require_all_context_near: [尖兵, C]  # only when ALL present
  near_window: 40
  level: P0
  message: "Protagonist described as cyborg without negation."
```

Both rule types support `exceptions` (registered waivers with `id`, `file`,
`reason`, `expires`).

## Schema validation

```bash
gdd-profile-validate Project_Profile.yaml
gdd-profile-validate --kind genre profiles/roguelite.yaml
```

Validates against the JSON Schemas in `schemas/`. `schema_version: 1` is
backward-compatible throughout 1.x.

For full details see `modules/02_project_profile.md`.

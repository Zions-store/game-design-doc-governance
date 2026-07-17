# New Project Setup

The one-time steps to bring a new game under the governance framework.

## 1. Choose a genre profile

Look inside `profiles/genre/` and pick the genre closest to your game. Each `.yaml`
file declares which documents are recommended, optional, and disabled for that
type. For a custom hybrid, copy the nearest profile and adjust.

Open the profile and note the `recommended_docs` and `optional_docs` lists.

## 2. Scaffold

```bash
gdd-scaffold \
  --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \
  --out "<my-game>/Design Document/md file" \
  --project-name "My Game" \
  --language en-US
```

This writes:

```
Design Document/md file/
  Design_Document.md       # index + summaries (never full bodies)
  STYLE_GUIDE.md           # the document constitution
  Project_Profile.yaml     # enabled docs, audit rules
  Naming.md                # names, terms, replacements
  ... (enabled doc skeletons)
  audit/                   # output directory (initially empty except README)
```

## 3. Fill the Project_Profile.yaml

Open `Project_Profile.yaml` and verify:

- `enabled_docs` - match the genre profile's `recommended_docs` + any chosen
  `optional_docs`.
- `audit` thresholds - defaults are `fail_on_p0: true, fail_on_p1: true,
  fail_on_p2_in_strict_mode: true`.
- `file_versioning.version_pattern` - default is `\((\d+)\)` (for `(n)`
  suffixes).

## 4. Populate the STYLE_GUIDE.md

The placeholder `STYLE_GUIDE.md` has the structure but **no project-specific
content**. Fill in:
- The authority matrix (搂4) - one row per content type.
- The anchor registry (搂6.2) - register high-risk cross-document facts.
- The deprecated-term registry (搂6.3) - register replaced settings/terms.

See `modules/04_authority_boundaries.md` and `modules/05_anchor_and_change_safety.md`.

## 5. First audit

```bash
gdd-audit --root "md file" --style "md file/STYLE_GUIDE.md" \
          --profile "md file/Project_Profile.yaml" --out "audit"
```

## 6. Iterate

Populate the doc skeletons with real content. After each batch of changes, run
`gdd-audit` and drive P0/P1 back to zero. Add boundary_checks and
consistency_checks to the profile as you discover content-leak patterns.

For migrating an existing GDD, follow `migration_guide.md`.

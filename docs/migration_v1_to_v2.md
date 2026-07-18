# Migration Guide — v1.x 🭆 v2.0

This guide covers migrating an existing project from v1.x governance to v2.0.

## Quick Summary

| Change | Action |
|--------|--------|
| `profiles/*.yaml` → `profiles/genre/*.yaml` | Update `--profile` paths in your scripts |
| Genre profile cleanup | Move `enabled_docs` and project facts to your `Project_Profile.yaml` |
| Language rules separated | Move Chinese/English terms to `rules/language_packs/` |
| Engine v2 default | `--engine 2` is now default; `--engine 1` for rollback |
| Scaffold safety | Non-empty dirs refused without `--force`; optional docs only with `--enable-doc` |

---

## Step-by-Step Migration

### 1. Check current state

```bash
gdd-audit --root "<project>/Design Document/md file" \
  --style "<project>/Design Document/md file/STYLE_GUIDE.md" \
  --profile "<project>/Design Document/md file/Project_Profile.yaml" \
  --out "<project>/Design Document/audit" --no-state
```

Record the baseline: `P0=N P1=N P2=N P3=N INFO=N`.

### 2. Add `profile_type` to your Project_Profile.yaml

```yaml
schema_version: 1
profile_type: project   # ← add this line
profile:
  name: My Project
  ...
```

Validate:

```bash
gdd-profile-validate --kind project "<path>/Project_Profile.yaml"
```

Expected: `VALID`.

### 3. Move `enabled_docs` out of genre profile (if you had a custom one)

If your genre profile (in `profiles/genre/`) contains `enabled_docs`, move it to your project profile. Genre profiles must NOT contain `enabled_docs` in v2.

### 4. Move project facts out of genre profile

If your genre profile contains `consistency_checks` with project-specific facts (character names, faction names, lore terms), move them to `project_fact_checks` in your project profile.

**Before** (genre profile — WRONG in v2):
```yaml
consistency_checks:
  - id: FACT-SHEPHERD-HUMAN
    term: 改造人
    require_negation_near: [不是, 并非]
    level: P0
```

**After** (project profile — CORRECT):
```yaml
project_fact_checks:
  - id: FACT-SHEPHERD-HUMAN
    authority: Character_Sheets.md
    forbid_terms: [改造人]
    require_negation_near: [不是, 并非, 非]
    level: P0
    message: "Protagonist may be described as cyborg (改造人) without negation."
```

### 5. Move Chinese regex/terms to language pack

If your genre profile contains language-specific regex patterns or resource terms, move them to a language pack.

**Before** (in genre profile):
```yaml
boundary_checks:
  - id: COLLECTIBLES-NO-RESOURCE
    forbid_any: [电池, 药品, 食物, 零件, 净水, 碎片]
```

**After** (in `rules/language_packs/zh-CN.yaml`):
```yaml
resource_terms:
  - 电池
  - 药品
  - 食物
  - 零件
  - 净水
  - 碎片
```

Reference in project profile:
```yaml
language: zh-CN
language_pack: rules/language_packs/zh-CN.yaml
```

### 6. Update profile paths in scripts

```bash
# Old
--profile profiles/open_world_narrative_tactical_shooter.yaml

# New
--profile profiles/genre/open_world_narrative_tactical_shooter.yaml
```

### 7. Re-run audit with engine v2 (now default)

```bash
gdd-audit --root "<project>/Design Document/md file" \
  --style "<project>/Design Document/md file/STYLE_GUIDE.md" \
  --profile "<project>/Design Document/md file/Project_Profile.yaml" \
  --out "<project>/Design Document/audit" --no-state
```

If you need the old behavior temporarily:
```bash
gdd-audit ... --engine 1
```

### 8. Verify EQUIVALENT

Compare P0/P1/P2/P3 counts with the v1 baseline recorded in step 1. They should be identical (EQUIVALENT).

If DIVERGED:
- Check step 2-5 for missed migrations
- Run with `--engine 1` to confirm v1 still matches
- Report the issue

---

## Scaffold Migration

### Old (v1 legacy)
```bash
gdd-scaffold --profile ... --out ... --project-name "My Game"
# Creates ALL optional docs in the target directory (even if not empty)
```

### New (v2 default)
```bash
gdd-scaffold --profile ... --out ... --project-name "My Game"
# Refuses non-empty dirs, only creates recommended docs

# To include optional docs:
gdd-scaffold ... --enable-doc Audio_Design.md --enable-doc Accessibility.md

# To force-overwrite a non-empty dir:
gdd-scaffold ... --force

# To restore legacy behavior:
gdd-scaffold ... --legacy
```

---

## Rollback

If v2 causes issues in your project:

1. Use `--engine 1` to keep the v1 audit behavior
2. Use `--legacy` to keep the v1 scaffold behavior
3. All v1 paths will be maintained through v2.x

---

## v1 Support Timeline

- **v2.0.x**: Full v1 compatibility maintained
- **v2.x**: v1 reader and migration entry points preserved
- **v3.0.0** (earliest): v1 support may be removed
- v2.x will NOT drop v1 support without a migration window

---

## Checklist

- [ ] `profile_type: project` added to Project_Profile.yaml
- [ ] `enabled_docs` moved from genre profile to project profile
- [ ] Project facts moved from `consistency_checks` to `project_fact_checks`
- [ ] Language-specific terms moved to `rules/language_packs/`
- [ ] Profile paths updated in scripts and CI
- [ ] `gdd-profile-validate` passes
- [ ] `gdd-audit` v2 baseline EQUIVALENT with v1
- [ ] Scaffold scripts updated (`--enable-doc`, `--force`, or `--legacy`)

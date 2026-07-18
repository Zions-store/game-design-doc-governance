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

> **Note**: `project_fact_checks` and `language_pack` are declared schema fields in v2.0.0-rc.
> The audit engine currently runs `consistency_checks` and `boundary_checks` from the project profile.
> Full runtime consumption of `project_fact_checks` and `language_pack` is planned for v2.1.
> For now, keep your existing `consistency_checks` in your project profile unchanged.

If your genre profile contains `consistency_checks` with project-specific facts, ensure they are in your
project profile (not the genre profile). Genre profiles must NOT contain project-specific fact checks.

### 5. Language rules: future path

> **Note**: `language_pack` field is declared but not yet consumed by the audit engine at runtime.
> Boundary checks with `forbid_regex`/`forbid_any` in your project profile continue to work
> as before. The `rules/language_packs/` directory and v1.8 `i18n.py` are infrastructure
> for future language-independent checks planned for v2.1.

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
- [ ] Profile paths updated in scripts and CI (`profiles/` → `profiles/genre/`)
- [ ] `gdd-profile-validate` passes
- [ ] `gdd-audit` v2 baseline EQUIVALENT with v1
- [ ] Scaffold scripts updated (`--enable-doc`, `--force`, or `--legacy`)

> **v2.1 planned**: `project_fact_checks` and `language_pack` runtime consumption.
> For now, keep `consistency_checks` and `boundary_checks` in your project profile unchanged.

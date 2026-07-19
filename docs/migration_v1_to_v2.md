# Migration Guide: v1.x to v2.0

This guide covers migrating an existing project from v1.x governance to v2.0.

## Quick Summary

| Change | Action |
|--------|--------|
| `profiles/*.yaml` -> `profiles/genre/*.yaml` | Update `--profile` paths in your scripts |
| Genre profile cleanup | Move `enabled_docs` to your `Project_Profile.yaml` |
| `profile_type: project` required | Add to your Project_Profile.yaml |
| Engine v2 default | `--engine 2` is now default; `--engine 1` for rollback |
| Scaffold safety | Non-empty dirs refused without `--force`; optional docs only with `--enable-doc` |

> **v2.1 available**: `project_fact_checks`, an explicitly selected maintained `language_pack`, and the full Engine v2 Finding/Waiver/State/Report pipeline run at audit time.
>
> **v2.2 available**: boundary coverage enforcement. When your project profile
> declares a `genre_profile`, every genre `boundary_check` with
> `pattern_ref`/`term_ref` must be covered by either (a) an executable project
> `boundary_checks` entry with the same `id`, or (b) a `language_pack` that
> resolves the reference. Uncovered rules produce P0 `CONFIG-BOUNDARY-COVERAGE`.

---

## Step-by-Step Migration

### 1. Check current state


`ash
gdd-audit --root "<project>/Design Document/md file" \
  --style "<project>/Design Document/md file/STYLE_GUIDE.md" \
  --profile "<project>/Design Document/md file/Project_Profile.yaml" \
  --out "<project>/Design Document/audit" --no-state
```

Record the baseline: `P0=N P1=N P2=N P3=N INFO=N`.

### 2. Add `profile_type` and `profile.language` to your Project_Profile.yaml


`yaml
schema_version: 1
profile_type: project   # <- add this line
profile:
  language: en-US        # <- add this line (BCP 47 tag)
  name: My Project
  ...
```

Validate:


`ash
gdd-profile-validate --kind project "<path>/Project_Profile.yaml"
```

Expected: `VALID`.

### 3. Move `enabled_docs` out of genre profile (if you had a custom one)

If your genre profile (in `profiles/genre/`) contains `enabled_docs`, move it to your project profile. Genre profiles must NOT contain `enabled_docs` in v2.

### 4. Move project facts out of genre profile

> **v2.1 behavior**: `project_fact_checks` run across every authority document.
> Keep existing `consistency_checks` in your project profile unchanged; they remain independently supported.

If your genre profile contains `consistency_checks` with project-specific facts, ensure they are in your
project profile (not the genre profile). Genre profiles must NOT contain project-specific fact checks.

### 5. Language rules

> **v2.1 behavior**: setting `language_pack` to a built-in tag (currently
> `en-US` or `zh-CN`) or a safe project-local `.yaml` path resolves the selected
> `profile.genre_profile`'s `pattern_ref` / `term_ref` checks. A project boundary
> rule with the same ID overrides the generic rule. For languages without a
> maintained built-in pack, supply your own local `.yaml` (see
> `templates/LANGUAGE_PACK_TEMPLATE.yaml`). Built-in tags and project-local
> paths are both supported; absolute paths and `..` traversal are rejected.
>
> **v2.2 behavior**: genre rules with `pattern_ref`/`term_ref` that are neither
> overridden by a same-ID project `boundary_checks` nor resolved via `language_pack`
> produce P0 `CONFIG-BOUNDARY-COVERAGE`. Each project override must be executable
> (non-empty `forbid_regex` or `forbid_any` with compilable regex). If you use a
> genre profile with such rules, either add project overrides or configure
> `language_pack` to a matching built-in tag.

### 6. Update profile paths in scripts


`ash
# Old
--profile profiles/open_world_narrative_tactical_shooter.yaml

# New
--profile profiles/genre/open_world_narrative_tactical_shooter.yaml
```

### 7. Re-run audit with engine v2 (now default)


`ash
gdd-audit --root "<project>/Design Document/md file" \
  --style "<project>/Design Document/md file/STYLE_GUIDE.md" \
  --profile "<project>/Design Document/md file/Project_Profile.yaml" \
  --out "<project>/Design Document/audit" --no-state
```

If you need the old behavior temporarily:

`ash
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

`ash
gdd-scaffold --profile ... --out ... --project-name "My Game"
# Creates ALL optional docs in the target directory (even if not empty)
```

### New (v2 default)

`ash
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
- [ ] Profile paths updated in scripts and CI (`profiles/` -> `profiles/genre/`)
- [ ] `gdd-profile-validate` passes
- [ ] `gdd-audit` v2 baseline EQUIVALENT with v1
- [ ] All genre boundary_checks covered by project rules or language_pack (no CONFIG-BOUNDARY-COVERAGE)
- [ ] Scaffold scripts updated (`--enable-doc`, `--force`, or `--legacy`)

> **v2.1 available**: project facts and an explicitly selected maintained language
> pack run in addition to existing `consistency_checks` and `boundary_checks`.
>
> **v2.2 available**: boundary coverage enforcement. If your project selects a
> `genre_profile` with `boundary_checks` using `pattern_ref`/`term_ref`, every
> such rule must be covered. Uncovered rules produce P0 errors.

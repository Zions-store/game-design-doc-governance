# Release Process

How to cut and publish a release of the `game-design-doc-governance` Skill.

## Versioning

- **Package version** lives in `SKILL.md` frontmatter (`version:`), `pyproject.toml`
  (`version`), `README.md` Status, and `CHANGELOG.md`.
- **Git tags** use standard repository tags: `vX.Y.Z`.
  Historical monorepo skill-scoped tags remain in `project-ledger` and are not moved.
- `schema_version: 1` in the JSON Schemas and Profile YAML files is
  backward-compatible throughout 1.x. Breaking schema changes are reserved for
  2.x.

## Pre-release checklist

1. CI all green: `markdown-lint` + `code-block-check` + `python-health` + `utf8-check` + `pytest`.
2. `pytest` passes locally (if pip proxy allows; otherwise verified in CI).
3. Fixture baseline regression: `gdd-audit --no-state --baseline …` → EQUIVALENT.
4. Origin project regression (if available): `gdd-audit --no-state --baseline …`.
5. All genre profiles pass `gdd-profile-validate`.
6. `MANIFEST.md` is up to date.
7. `CHANGELOG.md` has a `[VERSION]` entry.
8. `SKILL.md version:` matches the version being released.
9. No `.pyc` / `__pycache__` / temporary files in the repo.

## Cutting a release

```bash
# 1. Bump versions
#    - SKILL.md:  version: X.Y.Z
#    - README.md:  Status vX.Y.Z
#    - pyproject.toml:  version = "X.Y.Z"
#    - CHANGELOG.md:  ## [X.Y.Z] - YYYY-MM-DD - title
#    - tools/global_doc_audit.py:  SCRIPT_VERSION = "vX.Y.Z-generic"

# 2. Commit
git add .
git commit -m "release: X.Y.Z - summary"

# 3. Tag
git tag vX.Y.Z

# 4. Push
git push origin master
git push origin vX.Y.Z
```

## Tag policy

- Tags are **never force-moved** after being pushed.
- If CI is red on the tagged commit, the tag is left as-is (historical record)
  and a **patch version** (X.Y.Z+1) is released on the green fix.
- Pre-1.0 releases (0.x) may contain breaking changes. `0.9.0` is the RC freeze
  point; after RC, only bug fixes are backported.

## Branch strategy

- `master` is the single release branch.
- Feature work lands directly on `master` in small, CI-verified commits.
- Each release is a single commit on `master` + a tag.

## Stale planned / known-issue notes

Before tagging, check that `CHANGELOG.md` does not contain stale "P4 planned" or
"later phases add" notes that contradict the release content. Replace them with a
forward-looking `_Next:` line in `[Unreleased]`.

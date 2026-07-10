# Troubleshooting

## `gdd-audit` reports P0 "Missing expected authority doc"

The document is either not present in the `--root` directory or has a versioned
filename that the auditor cannot match. Check:

1. The filename matches the entry in `STYLE_GUIDE.md` (canonical) or uses the
   configured `version_pattern` in `Project_Profile.yaml`.
2. The file is actually in the `--root` directory.
3. Run `gdd-profile-validate` on your `Project_Profile.yaml` to ensure the
   `enabled_docs` list matches your actual files.

## STYLE parsing returns zero documents / anchors

If the auditor loads zero documents or anchors from your STYLE file, it is likely
that neither AUDIT markers nor the heading-heuristic keywords were found. Check:

- Your `STYLE_GUIDE.md` includes `<!-- AUDIT: ENABLED_DOCS_START/END -->`
  markers, OR uses the fallback heading names (e.g. `文件清单` or
  `Authoritative File List`).
- The tables are well-formed GFM pipe tables.
- Run `gdd-profile-validate` to confirm the STYLE file is a valid Markdown
  structure.

## `pip install -e .` fails with "not a Python project"

You ran `pip install -e .` from the monorepo root (`project-ledger/`), not from
the skill sub-directory. Do:

```bash
cd game-design-doc-governance
pip install -e .
```

## Markdown lint errors in CI

CI runs `markdownlint-cli2` with a project-specific config
(`.markdownlint-cli2.jsonc`). If you see new lint errors:

1. Check that your file is within the lint scope (`globs` in `ci.yml`).
2. If the rule is a false alarm for document prose (e.g. MD013 for long table
   rows), add it to the config's disabled rules.
3. Fixture files under `tests/fixtures/` are excluded from lint - intentional.

## Baseline regression diverged

1. Use a fresh output directory and `--no-state` to avoid state-file interference.
2. Check that no documents were added/removed from the root directory.
3. Check that both executions use the same profile and STYLE.
4. Run `gdd-profile-validate` to confirm the profile has not gained unexpected
   fields.

## `jsonschema` not installed

```bash
pip install jsonschema
```

Or re-run `pip install -e .` which declares `jsonschema` as a dependency.

# Quickstart

The fastest path from zero to a governed, auditable game design document set.

## 1. Install

```bash
git clone https://github.com/Zions-store/game-design-doc-governance.git
cd game-design-doc-governance
py -m pip install -e .
```

Three console commands are now available: `gdd-audit`, `gdd-profile-validate`,
`gdd-scaffold`.

## 2. Scaffold a new project

Pick a genre profile from `profiles/genre/` (e.g. `open_world_narrative_tactical_shooter`):

```bash
gdd-scaffold \
  --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \
  --out "<my-game>/Design Document/md file" \
  --project-name "My Game" \
  --language en-US
```

This creates ~15 doc skeletons, a `STYLE_GUIDE.md` (the document constitution),
a `Project_Profile.yaml`, and an `audit/` directory - all ready to fill in.

## 3. Run the first audit

```bash
cd "<my-game>/Design Document"
gdd-audit \
  --root "md file" \
  --style "md file/STYLE_GUIDE.md" \
  --profile "md file/Project_Profile.yaml" \
  --out "audit"
```

A freshly scaffolded project should show **P0=0 P1=0** (the templates produce no
blocking issues). Populate the doc bodies, re-audit, and drive P0/P1 back to zero
after each batch of changes.

## 4. Understand the report

- **P0** - blocking: fact or authority conflict; must fix.
- **P1** - high: deprecated setting, broken link, boundary leak; must fix.
- **P2** - medium: format/table issues; blocks in `--strict` mode.
- **P3** - advisory: traceability / naming suggestions.

Issue IDs are stable (`AUD-{level}-{hash}`). State is tracked in
`audit/issue_state.jsonl`.

## 5. Next steps

- Add anchors (`<!-- FACT-... -->`) for cross-document facts.
- Register deprecated terms in `STYLE_GUIDE.md`.
- Add `boundary_checks` and `consistency_checks` to `Project_Profile.yaml`.
- See the other docs/ guides for deeper dives.

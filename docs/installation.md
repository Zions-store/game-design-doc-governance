# Installation

## Requirements

- Python 3.9 or later
- Git

The only runtime dependencies are `pyyaml` and `jsonschema` (declared in
`pyproject.toml` and `requirements.txt`).

## From source (recommended for local use)

```bash
git clone git@github.com:Zions-store/game-design-doc-governance.git
cd game-design-doc-governance
pip install -e .
```

Three console scripts are registered:

| Command | Purpose |
|---|---|
| `gdd-audit` | Run the generic documentation auditor |
| `gdd-profile-validate` | Validate a Project_Profile.yaml or genre profile against its JSON Schema |
| `gdd-scaffold` | Initialize a new design-doc project from a genre profile |

## Installing into opencode

The Skill lives as a sub-directory of the `project-ledger` monorepo. Wire it
into opencode via an NTFS junction (Windows) or symlink (Linux/macOS):

```
# Windows (PowerShell)
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.config\opencode\skills\game-design-doc-governance" `
  -Target "<path to game-design-doc-governance>"

# Linux / macOS
ln -s "<path to project-ledger>/game-design-doc-governance" \
      "$HOME/.config/opencode/skills/game-design-doc-governance"
```

After wiring, the Skill's `SKILL.md` is automatically discovered by opencode in
the next session.

## Developer install (for contributing to the Skill itself)

```bash
cd game-design-doc-governance
pip install -e ".[test]"   # if a [test] extra is defined
pip install pytest          # otherwise
python -m pytest tests -v
```

## Checking everything works

```bash
gdd-audit --help
gdd-profile-validate --help
gdd-scaffold --help
```

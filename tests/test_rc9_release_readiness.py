# -*- coding: utf-8 -*-
"""Regression coverage for rc9 release-readiness repairs."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from conftest import run_auditor
from game_design_doc_governance.engine import validate_profile
from game_design_doc_governance.profile_schema import validate_profile_data
from tools.scaffold_project import scaffold


ROOT = Path(__file__).resolve().parents[1]


def _project_profile(language: str = "en-US") -> dict:
    return {
        "schema_version": 1,
        "profile_type": "project",
        "profile": {"name": "Test Project", "language": language},
        "enabled_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
    }


def test_engine_v2_rejects_project_profile_that_fails_schema():
    findings = validate_profile({"schema_version": 1, "enabled_docs": []}, strict=True)
    assert any(f.rule == "CONFIG-SCHEMA" and f.level == "P0" for f in findings)


def test_direct_source_audit_uses_engine_v2_schema_validation(tmp_path):
    profile = tmp_path / "invalid_project.yaml"
    profile.write_text("schema_version: 1\nenabled_docs: []\n", encoding="utf-8")
    tool = ROOT / "tools" / "global_doc_audit.py"
    source = ROOT / "src"
    runner = f"""
import runpy
import sys
from pathlib import Path
root = Path({str(ROOT)!r})
source = Path({str(source)!r}).resolve()
sys.path[:] = [item for item in sys.path if Path(item or '.').resolve() != source]
sys.argv = [{str(tool)!r}, '--root', {str(tmp_path)!r}, '--profile', {str(profile)!r}, '--out', {str(tmp_path / 'audit')!r}, '--no-state', '--no-history', '--engine', '2']
runpy.run_path({str(tool)!r}, run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", runner],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "P0 CONFIG-SCHEMA:" in result.stderr
    assert "falling back to v1 validation" not in result.stdout


@pytest.mark.parametrize("language", ["en-US", "zh-Hans", "zh-Hant-TW", "es-419", "fr-CA"])
def test_project_schema_accepts_supported_language_tags(language):
    assert validate_profile_data(_project_profile(language), kind="project") == []


@pytest.mark.parametrize("language", ["", "{{LANGUAGE}}", "en-\\ninjected: true", "EN-us"])
def test_project_schema_rejects_invalid_or_unsafe_language_tags(language):
    assert validate_profile_data(_project_profile(language), kind="project")


def test_project_schema_rejects_malformed_runtime_audit_rule():
    profile = _project_profile()
    profile["boundary_checks"] = [{"id": "INCOMPLETE"}]
    assert validate_profile_data(profile, kind="project")


@pytest.mark.parametrize(
    "mutation",
    [
        {"consistency_checks": []},
        {"deprecated_terms": []},
        {"link_checks": {"enabled": True}},
        {"exceptions": []},
    ],
)
def test_genre_schema_rejects_project_only_fields(mutation):
    profile = {
        "schema_version": 1,
        "profile_type": "genre",
        "profile": {
            "name": "Generic Genre",
            "description": "A reusable genre profile.",
            "primary_type": "Action",
        },
        "recommended_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
    }
    profile.update(mutation)
    assert validate_profile_data(profile, kind="genre")


def test_genre_schema_rejects_nested_project_facts_and_executable_patterns():
    profile = {
        "schema_version": 1,
        "profile_type": "genre",
        "profile": {
            "name": "Generic Genre",
            "description": "A reusable genre profile.",
            "primary_type": "Action",
            "named_characters": ["Not allowed"],
        },
        "recommended_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
        "boundary_checks": [{
            "id": "GENERIC-RULE",
            "type": "generic_rule",
            "pattern_ref": "stat_patterns.value",
            "files": ["Design_Document.md"],
            "message": "Generic boundary warning.",
            "forbid_regex": "project-only implementation",
        }],
    }
    assert validate_profile_data(profile, kind="genre")


def test_scaffold_escapes_project_name_before_writing_yaml(tmp_path):
    profile = ROOT / "profiles" / "genre" / "open_world_rpg.yaml"
    out = tmp_path / "injected" / "md file"
    name = 'Quoted " name\nwith a second line'

    assert scaffold(str(profile), str(out), name, "en-US")
    rendered = yaml.safe_load((out / "Project_Profile.yaml").read_text(encoding="utf-8"))

    assert rendered["profile"]["name"] == name
    assert "injected" not in rendered
    assert validate_profile_data(rendered, kind="project") == []


def test_scaffold_validates_document_names_before_dry_run(tmp_path):
    profile = tmp_path / "malicious_genre.yaml"
    profile.write_text(
        """schema_version: 1
profile_type: genre
profile:
  name: Malicious test
  description: Test profile
  primary_type: Test
recommended_docs: [../escaped.md]
""",
        encoding="utf-8",
    )
    out = tmp_path / "generated" / "md file"

    assert not scaffold(str(profile), str(out), "Test", "en-US", dry_run=True)
    assert not out.exists()


def test_all_genre_profiles_scaffold_validate_and_audit(tmp_path):
    for profile in sorted((ROOT / "profiles" / "genre").glob("*.yaml")):
        out = tmp_path / profile.stem / "md file"
        audit = tmp_path / profile.stem / "audit"

        assert scaffold(str(profile), str(out), profile.stem, "en-US"), profile.name
        data = yaml.safe_load((out / "Project_Profile.yaml").read_text(encoding="utf-8"))
        assert validate_profile_data(data, kind="project") == [], profile.name

        passed, counts, _ = run_auditor(
            str(out),
            str(out / "Project_Profile.yaml"),
            str(out / "STYLE_GUIDE.md"),
            out=str(audit),
            write_history=False,
            write_state=False,
        )
        assert passed, f"{profile.name}: {counts}"
        assert counts["p0"] == 0, profile.name
        assert counts["p1"] == 0, profile.name


def test_skeleton_coverage_counts_are_release_metadata_source_of_truth():
    skeletons = {
        path.name.removesuffix(".md.tmpl") + ".md"
        for path in (ROOT / "doc_modules").glob("*.md.tmpl")
    }
    profile_docs = set()
    for profile_path in (ROOT / "profiles" / "genre").glob("*.yaml"):
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        for key in ("recommended_docs", "optional_docs"):
            profile_docs.update(data.get(key, []))

    assert len(skeletons) == 27
    assert len(profile_docs) == 48
    assert len(skeletons & profile_docs) == 24
    assert len(profile_docs - skeletons) == 24


def test_release_version_surfaces_are_consistent():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r"(?m)^version: (.+)$", skill).group(1)
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert f'version = "{version}"' in pyproject
    assert f"**v{version} " in readme
    assert f"## [{version}]" in changelog
    for path in (ROOT / "tools" / "global_doc_audit.py", ROOT / "src" / "game_design_doc_governance" / "engine.py"):
        assert f'SCRIPT_VERSION = "v{version}-generic"' in path.read_text(encoding="utf-8")

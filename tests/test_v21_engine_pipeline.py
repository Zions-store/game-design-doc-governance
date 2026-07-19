"""Regression coverage for the v2.1 runtime audit pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator

from conftest import run_auditor
from game_design_doc_governance.engine import Finding


def _profile(**overrides: object) -> dict:
    profile = {
        "schema_version": 1,
        "profile_type": "project",
        "profile": {"name": "Pipeline Test", "language": "en-US"},
        "enabled_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
        "boundary_checks": [
            {
                "id": "TEST-FORBIDDEN",
                "files": ["Design_Document.md"],
                "forbid_any": ["forbidden"],
                "level": "P2",
                "message": "Forbidden test content.",
            }
        ],
        "link_checks": {"enabled": False},
    }
    profile.update(overrides)
    return profile


def _write_project(tmp_path: Path, profile: dict, document: str = "forbidden") -> tuple[Path, Path]:
    root = tmp_path / "md file"
    root.mkdir()
    (root / "Design_Document.md").write_text(document, encoding="utf-8")
    (root / "STYLE_GUIDE.md").write_text("# Style\n", encoding="utf-8")
    profile_path = root / "Project_Profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8")
    return root, profile_path


def _report(out: Path) -> dict:
    return json.loads((out / "audit_report.json").read_text(encoding="utf-8"))


def test_engine_v2_uses_precise_waivers_and_report_v2(tmp_path):
    profile = _profile(exceptions=[{
        "id": "TEST-FORBIDDEN",
        "file": "Design_Document.md",
        "reason": "Intentional test fixture.",
        "expires": "2999-01-01",
    }])
    root, profile_path = _write_project(tmp_path, profile)
    out = tmp_path / "audit"

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=True, engine_version=2,
    )

    assert passed
    assert counts["p2"] == 0
    assert len(issues) == 1
    assert issues[0]["suppressed"] is True
    assert issues[0]["suppression_reason"] == "waiver: Intentional test fixture."
    data = _report(out)
    assert data["engine_version"] == 2
    assert data["waivers_active"] == 1
    assert data["waivers_expired"] == 0
    assert data["suppressed"] == 1
    assert data["boundary_rule_coverage"] == {
        "total": 0,
        "by_project": 0,
        "by_language_pack": 0,
        "uncovered": 0,
    }
    report_schema = json.loads((Path(__file__).resolve().parents[1] / "schemas" / "audit_report.schema.json").read_text(encoding="utf-8"))
    assert list(Draft7Validator(report_schema).iter_errors(data)) == []
    missing_coverage = dict(data)
    missing_coverage.pop("boundary_rule_coverage")
    assert list(Draft7Validator(report_schema).iter_errors(missing_coverage))
    invalid_coverage = json.loads(json.dumps(data))
    invalid_coverage["boundary_rule_coverage"]["total"] = "0"
    assert list(Draft7Validator(report_schema).iter_errors(invalid_coverage))
    assert (out / "audit_report.md").read_text(encoding="utf-8").startswith("# Audit Report v2")


def test_engine_v1_preserves_invalid_regex_exception(tmp_path):
    profile = _profile(boundary_checks=[{
        "id": "INVALID-REGEX",
        "files": ["Design_Document.md"],
        "forbid_regex": "[",
        "level": "P0",
        "message": "Invalid regex fixture.",
    }])
    root, profile_path = _write_project(tmp_path, profile, document="test")

    with pytest.raises(re.error):
        run_auditor(
            str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
            out=str(tmp_path / "audit"), write_history=False,
            write_state=False, engine_version=1,
        )


def test_engine_v2_expired_waiver_reactivates_finding(tmp_path):
    profile = _profile(exceptions=[{
        "id": "TEST-FORBIDDEN",
        "file": "Design_Document.md",
        "reason": "Expired test fixture.",
        "expires": "2000-01-01",
    }])
    root, profile_path = _write_project(tmp_path, profile)
    out = tmp_path / "audit"

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p2"] == 1
    assert issues[0].get("suppressed") is None
    data = _report(out)
    assert data["waivers_active"] == 0
    assert data["waivers_expired"] == 1
    assert "## Expired Waivers" in (out / "audit_report.md").read_text(encoding="utf-8")


def test_engine_v2_state_transitions_are_stable_and_file_scoped(tmp_path):
    profile = _profile()
    root, profile_path = _write_project(tmp_path, profile)
    out = tmp_path / "audit"

    run_auditor(str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
                 write_history=False, write_state=True, engine_version=2)
    finding_id = Finding.make_id("P2", "TEST-FORBIDDEN", "Forbidden test content.", "Design_Document.md")
    state_path = out / "issue_state.jsonl"
    state = {entry["issue_id"]: entry for entry in map(json.loads, state_path.read_text(encoding="utf-8").splitlines())}
    assert state[finding_id]["status"] == "OPEN"
    issue_state_schema = json.loads((Path(__file__).resolve().parents[1] / "schemas" / "issue_state.schema.json").read_text(encoding="utf-8"))
    assert list(Draft7Validator(issue_state_schema).iter_errors(state[finding_id])) == []

    (root / "Design_Document.md").write_text("clean", encoding="utf-8")
    run_auditor(str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
                 write_history=False, write_state=True, engine_version=2)
    state = {entry["issue_id"]: entry for entry in map(json.loads, state_path.read_text(encoding="utf-8").splitlines())}
    assert state[finding_id]["status"] == "FIXED_PENDING_VERIFY"

    run_auditor(str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
                 write_history=False, write_state=True, engine_version=2)
    state = {entry["issue_id"]: entry for entry in map(json.loads, state_path.read_text(encoding="utf-8").splitlines())}
    assert state[finding_id]["status"] == "VERIFIED"

    (root / "Design_Document.md").write_text("forbidden", encoding="utf-8")
    run_auditor(str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
                 write_history=False, write_state=True, engine_version=2)
    state = {entry["issue_id"]: entry for entry in map(json.loads, state_path.read_text(encoding="utf-8").splitlines())}
    assert state[finding_id]["status"] == "REOPENED"


def test_engine_v2_consumes_project_facts_and_language_pack_genre_patterns(tmp_path):
    profile = _profile(
        profile={
            "name": "Runtime Fields Test",
            "language": "en-US",
            "genre_profile": "open_world_narrative_tactical_shooter",
        },
        language_pack="en-US",
        project_fact_checks=[{
            "id": "FACT-NOT-CYBORG",
            "authority": "Design_Document.md",
            "forbid_terms": ["cyborg"],
            "require_negation_near": ["not"],
            "level": "P0",
            "message": "Protagonist must not be described as a cyborg.",
        }],
    )
    root, profile_path = _write_project(tmp_path, profile, "cyborg has a 10%/s drain")
    out = tmp_path / "audit"

    _, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=False, engine_version=2,
    )

    assert counts["p0"] == 1
    assert counts["p2"] == 1
    assert {issue["rule"] for issue in issues} == {
        "FACT-NOT-CYBORG", "GDD-SUMMARY-ONLY-ENERGY"
    }


def test_engine_v2_rejects_language_pack_without_a_genre_profile(tmp_path):
    profile = _profile(language_pack="en-US")
    root, profile_path = _write_project(tmp_path, profile, "clean")
    out = tmp_path / "audit"

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] == 1
    assert issues[0]["rule"] == "CONFIG-GENRE-PROFILE"


def test_engine_v2_reports_invalid_language_pack_yaml_as_configuration_error(tmp_path):
    profile = _profile(
        profile={"name": "Bad Pack", "language": "en-US", "genre_profile": "open_world_narrative_tactical_shooter"},
        language_pack="bad-pack.yaml",
    )
    root, profile_path = _write_project(tmp_path, profile, "clean")
    (root / "bad-pack.yaml").write_text("language: [unterminated", encoding="utf-8")
    out = tmp_path / "audit"

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    # v2.2: 1 CONFIG-LANGUAGE-PACK + 4 CONFIG-BOUNDARY-COVERAGE (one per uncovered genre rule)
    assert counts["p0"] >= 1
    error_rules = {issue["rule"] for issue in issues if issue["level"] == "P0"}
    assert "CONFIG-LANGUAGE-PACK" in error_rules
    coverage_count = sum(1 for issue in issues if issue["rule"] == "CONFIG-BOUNDARY-COVERAGE")
    assert coverage_count == 4


def test_engine_v2_reports_invalid_language_pack_regex_as_configuration_error(tmp_path):
    profile = _profile(
        profile={"name": "Bad Regex", "language": "en-US", "genre_profile": "open_world_narrative_tactical_shooter"},
        language_pack="bad-regex.yaml",
    )
    root, profile_path = _write_project(tmp_path, profile, "clean")
    (root / "bad-regex.yaml").write_text(
        "schema_version: 1\nlanguage: en-US\nstat_patterns:\n  percentage_per_second: ['[']\n",
        encoding="utf-8",
    )
    out = tmp_path / "audit"

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"), out=str(out),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] >= 1
    assert "CONFIG-LANGUAGE-REF" in {issue["rule"] for issue in issues}

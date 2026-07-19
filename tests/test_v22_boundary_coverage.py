# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""v2.2.0 boundary-coverage contract tests.

Verifies that genre boundary_checks with pattern_ref/term_ref are never
silently skipped.  The coverage algorithm is:

  1. Project boundary_checks with the same ID overrides the genre rule
     — but only if the project rule is executable (non-empty forbid_regex
     or forbid_any, with compilable regex).
  2. A configured language_pack with a resolvable reference covers the rule.
  3. When a language-pack reference fails to resolve, both CONFIG-LANGUAGE-REF
     and CONFIG-BOUNDARY-COVERAGE are emitted.
  4. Neither executable project override nor resolvable language pack →
     P0 CONFIG-BOUNDARY-COVERAGE.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from conftest import run_auditor


# -- helpers --


def _genre_profile() -> dict:
    """Genre profile with boundary_checks that all use pattern_ref or term_ref."""
    return {
        "schema_version": 1,
        "profile_type": "genre",
        "profile": {
            "name": "test_coverage_genre",
            "description": "Test genre for v2.2 coverage validation.",
            "primary_type": "Action",
        },
        "recommended_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
        "boundary_checks": [
            {
                "id": "GENRE-RULE-A",
                "type": "test_rule_a",
                "pattern_ref": "stat_patterns.value_a",
                "files": ["Design_Document.md"],
                "message": "Genre rule A triggered.",
            },
            {
                "id": "GENRE-RULE-B",
                "type": "test_rule_b",
                "term_ref": "resource_terms",
                "files": ["Design_Document.md"],
                "message": "Genre rule B triggered.",
            },
            {
                "id": "GENRE-RULE-C",
                "type": "test_rule_c",
                "pattern_ref": "stat_patterns.value_c",
                "files": ["Design_Document.md"],
                "message": "Genre rule C triggered.",
            },
        ],
    }


def _language_pack(language: str = "en-US") -> dict:
    return {
        "schema_version": 1,
        "language": language,
        "stat_patterns": {
            "value_a": [r"\d+ units? per minute"],
            "value_c": [r"\d+ items? each"],
        },
        "resource_terms": ["battery", "clean water", "parts"],
    }


def _project_profile(
    *,
    genre_name: str = "test_coverage_genre",
    language: str = "en-US",
    language_pack_ref: str | None = None,
    boundary_checks: list[dict] | None = None,
) -> dict:
    profile: dict = {
        "schema_version": 1,
        "profile_type": "project",
        "profile": {
            "name": "Coverage Test Project",
            "language": language,
            "genre_profile": genre_name,
        },
        "enabled_docs": ["Design_Document.md", "STYLE_GUIDE.md"],
        "link_checks": {"enabled": False},
    }
    if language_pack_ref is not None:
        profile["language_pack"] = language_pack_ref
    if boundary_checks is not None:
        profile["boundary_checks"] = boundary_checks
    return profile


def _write_project(
    tmp_path: Path,
    profile: dict,
    genre: dict | None = None,
    language_pack: dict | None = None,
    document: str = "clean text with no triggers",
) -> tuple[Path, Path]:
    """Write a complete project fixture into tmp_path and return (root, profile_path)."""
    root = tmp_path / "md file"
    root.mkdir()
    (root / "Design_Document.md").write_text(document, encoding="utf-8")
    (root / "STYLE_GUIDE.md").write_text("# Style\n", encoding="utf-8")
    profile_path = root / "Project_Profile.yaml"
    profile_path.write_text(
        yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8"
    )

    if genre is not None:
        genre_dir = tmp_path / "profiles" / "genre"
        genre_dir.mkdir(parents=True, exist_ok=True)
        (genre_dir / f"{genre['profile']['name']}.yaml").write_text(
            yaml.safe_dump(genre, allow_unicode=True), encoding="utf-8"
        )

    if language_pack is not None:
        rules_dir = tmp_path / "rules" / "language_packs"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / f"{language_pack['language']}.yaml").write_text(
            yaml.safe_dump(language_pack, allow_unicode=True), encoding="utf-8"
        )

    return root, profile_path


# -- tests --


def test_uncovered_genre_rules_produce_p0(tmp_path, monkeypatch):
    """Genre rules with pattern_ref/term_ref, no language_pack, no project
    overrides → P0 CONFIG-BOUNDARY-COVERAGE for each rule."""
    profile = _project_profile(language_pack_ref=None, boundary_checks=None)
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(), document="clean"
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] == 3
    coverage_issues = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert len(coverage_issues) == 3
    rule_ids = {re.search(r"'([^']+)'", i["message"]).group(1) for i in coverage_issues}
    assert rule_ids == {"GENRE-RULE-A", "GENRE-RULE-B", "GENRE-RULE-C"}


def test_all_genre_rules_covered_by_project_overrides_pass(tmp_path, monkeypatch):
    """All genre rules covered by project boundary_checks with same IDs → no P0."""
    profile = _project_profile(
        language_pack_ref=None,
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+ units? per minute", "level": "P2",
                "message": "Overridden A.",
            },
            {
                "id": "GENRE-RULE-B", "files": ["Design_Document.md"],
                "forbid_any": ["battery"], "level": "P2",
                "message": "Overridden B.",
            },
            {
                "id": "GENRE-RULE-C", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+ items? each", "level": "P2",
                "message": "Overridden C.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(), document="clean"
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p0"] == 0
    coverage = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert coverage == []


def test_genre_rules_resolved_via_language_pack_pass(tmp_path, monkeypatch):
    """When language_pack is configured and references are resolvable →
    compiled checks run, no P0 coverage errors."""
    profile = _project_profile(language_pack_ref="en-US", boundary_checks=None)
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(),
        language_pack=_language_pack(), document="clean",
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p0"] == 0


def test_missing_language_pack_reference_produces_error(tmp_path, monkeypatch):
    """Language pack is configured but a genre rule's reference is missing
    from the pack → both CONFIG-LANGUAGE-REF and CONFIG-BOUNDARY-COVERAGE."""
    incomplete_pack = {
        "schema_version": 1,
        "language": "en-US",
        "stat_patterns": {"value_a": [r"\d+ units? per minute"]},
    }
    profile = _project_profile(
        language_pack_ref="en-US",
        boundary_checks=[
            {
                "id": "GENRE-RULE-C", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+ items? each", "level": "P2",
                "message": "Overridden C.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(),
        language_pack=incomplete_pack, document="clean",
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] >= 1
    error_rules = {i["rule"] for i in issues if i["level"] == "P0"}
    assert "CONFIG-LANGUAGE-REF" in error_rules
    assert "CONFIG-BOUNDARY-COVERAGE" in error_rules


def test_mixed_coverage_assembly(tmp_path, monkeypatch):
    """GENRE-RULE-A overridden by project, GENRE-RULE-B from language pack,
    GENRE-RULE-C from language pack → all covered, no P0."""
    profile = _project_profile(
        language_pack_ref="en-US",
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+ units? per minute", "level": "P2",
                "message": "Overridden A.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(),
        language_pack=_language_pack(), document="clean",
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p0"] == 0


def test_project_override_ignores_language_pack_for_same_id(tmp_path, monkeypatch):
    """Project boundary_checks with same ID take priority over language_pack."""
    profile = _project_profile(
        language_pack_ref="en-US",
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "forbid_regex": r"PROJECT-SPECIFIC-PATTERN", "level": "P2",
                "message": "Project-specific override A.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(),
        language_pack=_language_pack(), document="5 units per minute",
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p0"] == 0
    ga_issues = [i for i in issues if i["rule"] == "GENRE-RULE-A"]
    assert ga_issues == []


def test_partial_project_coverage_still_reports_uncovered(tmp_path, monkeypatch):
    """When the project overrides only SOME genre rules, the uncovered ones
    still produce P0 CONFIG-BOUNDARY-COVERAGE."""
    profile = _project_profile(
        language_pack_ref=None,
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+ units? per minute", "level": "P2",
                "message": "Overridden A.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(), document="clean"
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] == 2
    coverage = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert len(coverage) == 2
    rule_ids = {re.search(r"'([^']+)'", i["message"]).group(1) for i in coverage}
    assert rule_ids == {"GENRE-RULE-B", "GENRE-RULE-C"}


def test_third_person_test_equivalent_full_coverage(tmp_path, monkeypatch):
    """Simulate ThirdPersonTest: all 4 genre rules overridden by project
    boundary_checks + language_pack configured → 0 P0."""
    import shutil

    real_genre_path = (
        Path(__file__).resolve().parents[1] / "profiles" / "genre"
        / "open_world_narrative_tactical_shooter.yaml"
    )
    real_pack = (
        Path(__file__).resolve().parents[1] / "rules" / "language_packs" / "en-US.yaml"
    )

    genre_dir = tmp_path / "profiles" / "genre"
    genre_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(real_genre_path, genre_dir / "open_world_narrative_tactical_shooter.yaml")

    pack_dir = tmp_path / "rules" / "language_packs"
    pack_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(real_pack, pack_dir / "en-US.yaml")

    profile = _project_profile(
        genre_name="open_world_narrative_tactical_shooter",
        language_pack_ref="en-US",
        boundary_checks=[
            {
                "id": "GDD-SUMMARY-ONLY-ENERGY", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+%/s",
                "unless_near": ["Gameplay_Systems.md"], "near_window": 200,
                "stop_at": "[已迁移]", "level": "P2",
                "message": "Possible energy rate in GDD.",
            },
            {
                "id": "CHAR-NO-WEAPON-STATS", "files": ["Design_Document.md"],
                "forbid_regex": r"\d+/发", "level": "P2",
                "message": "Weapon stat in character doc.",
            },
            {
                "id": "WORLD-NO-EVENT-BODY", "files": ["Design_Document.md"],
                "forbid_regex": r"选择.*后果", "level": "P2",
                "message": "Event body in world doc.",
            },
            {
                "id": "COLLECTIBLES-NO-RESOURCE", "files": ["Design_Document.md"],
                "forbid_any": ["电池"], "level": "P3",
                "message": "Resource in collectibles.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=None, document="clean",
    )

    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert passed
    assert counts["p0"] == 0
    coverage = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert coverage == []


def test_non_executable_project_override_triggers_coverage_p0(tmp_path, monkeypatch):
    """Project override with empty forbid_regex and forbid_any is NOT
    accepted as coverage → CONFIG-BOUNDARY-COVERAGE."""
    profile = _project_profile(
        language_pack_ref=None,
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "level": "P2", "message": "Empty matchers rule.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(), document="clean"
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] == 3
    coverage = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert len(coverage) == 3
    messages = " ".join(i["message"] for i in coverage)
    assert "not executable" in messages


def test_invalid_regex_in_project_override_triggers_coverage_p0(tmp_path, monkeypatch):
    """Project override with invalid forbid_regex '[' → CONFIG-BOUNDARY-COVERAGE."""
    profile = _project_profile(
        language_pack_ref=None,
        boundary_checks=[
            {
                "id": "GENRE-RULE-A", "files": ["Design_Document.md"],
                "forbid_regex": "[", "level": "P2",
                "message": "Invalid regex rule.",
            },
        ],
    )
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(), document="clean"
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    assert counts["p0"] == 4
    coverage = [i for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE"]
    assert len(coverage) == 3
    messages = " ".join(i["message"] for i in coverage)
    assert "regular expression" in messages
    # +1 from CONFIG-BOUNDARY-REGEX crash defense when bad regex runs at audit time


def test_missing_language_pack_ref_emits_both_errors(tmp_path, monkeypatch):
    """Missing lang-pack ref → both CONFIG-LANGUAGE-REF and CONFIG-BOUNDARY-COVERAGE."""
    incomplete_pack = {
        "schema_version": 1, "language": "en-US",
        "stat_patterns": {"value_a": [r"\d+ units? per minute"]},
    }
    profile = _project_profile(language_pack_ref="en-US", boundary_checks=None)
    root, profile_path = _write_project(
        tmp_path, profile, genre=_genre_profile(),
        language_pack=incomplete_pack, document="clean",
    )
    monkeypatch.setattr(
        "game_design_doc_governance.runtime_rules.asset_directory",
        lambda sub: tmp_path / sub,
    )

    passed, counts, issues = run_auditor(
        str(root), str(profile_path), str(root / "STYLE_GUIDE.md"),
        out=str(tmp_path / "audit"),
        write_history=False, write_state=False, engine_version=2,
    )

    assert not passed
    error_rules = {i["rule"] for i in issues if i["level"] == "P0"}
    assert "CONFIG-LANGUAGE-REF" in error_rules
    assert "CONFIG-BOUNDARY-COVERAGE" in error_rules
    assert sum(1 for i in issues if i["rule"] == "CONFIG-LANGUAGE-REF") == 2
    assert sum(1 for i in issues if i["rule"] == "CONFIG-BOUNDARY-COVERAGE") == 2

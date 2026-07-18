# -*- coding: utf-8 -*-
import os
import json
import hashlib
import tempfile
import pytest

from conftest import _auditor, run_auditor, fixture_md, fixture_profile, expected_json

# ────────────────────────────────────────────────────────
# 1  STYLE parsing paths
# ────────────────────────────────────────────────────────
def test_marker_parsing():
    gda = _auditor()
    style = """## 2. Authoritative File List
<!-- AUDIT: ENABLED_DOCS_START -->
| File | Role |
|---|---|
| Design_Document.md | GDD |
| Gameplay_Systems.md | sys |
<!-- AUDIT: ENABLED_DOCS_END -->
### 6.2 Anchor registry
<!-- AUDIT: ANCHOR_REGISTRY_START -->
| Anchor ID | Setting | Authority | Ref |
|---|---|---|---|
| FACT-TEST | test | D | G |
<!-- AUDIT: ANCHOR_REGISTRY_END -->
### 6.3 Deprecated-term registry
<!-- AUDIT: DEPRECATED_TERMS_START -->
| Deprecated | Correct | Type | Keyword | Scope |
|---|---|---|---|---|
| old | new | term | old | * |
<!-- AUDIT: DEPRECATED_TERMS_END -->
"""
    gda.load_style_rules(style)
    assert "Design_Document.md" in gda.EXPECTED_DOCS
    assert "Gameplay_Systems.md" in gda.EXPECTED_DOCS
    assert "FACT-TEST" in gda.ANCHOR_LIST
    assert any(d[0] == "old" for d in gda.DEPRECATED_LIST)

def test_chinese_fallback_parsing():
    gda = _auditor()
    style = """## 2. 文件清单
| 文件 | 角色 |
|---|---|
| Design_Document.md | GDD |
| Gameplay_Systems.md | 系统 |
### 6.2 已建立锚点清单
| 锚点 ID | 设定内容 | 权威文档 | 引用文档 |
|---|---|---|---|
| FACT-ZH | zh test | D | G |
### 6.3 废弃说法
| 废弃说法 | 当前正确说法 | 类型 | 关键词 | 搜索范围 |
|---|---|---|---|---|
| old_zh | new_zh | 术语 | old_zh | 全部正式权威文档 |
登记原则：废弃关键词尽量具体。
"""
    gda.load_style_rules(style)
    assert "Design_Document.md" in gda.EXPECTED_DOCS
    assert "FACT-ZH" in gda.ANCHOR_LIST
    assert any(d[0] == "old_zh" for d in gda.DEPRECATED_LIST)

# ────────────────────────────────────────────────────────
# 2  file versioning
# ────────────────────────────────────────────────────────
def test_find_latest_canonical():
    gda = _auditor()
    d = tempfile.mkdtemp()
    for n in ["STYLE_GUIDE.md", "STYLE_GUIDE_TEMPLATE.md"]:
        open(os.path.join(d, n), "w").close()
    p, v = gda.find_latest(d, "STYLE_GUIDE.md")
    assert os.path.basename(p) == "STYLE_GUIDE.md"
    assert v == 0

def test_find_latest_n_suffix():
    gda = _auditor()
    d = tempfile.mkdtemp()
    for n in ["STYLE_GUIDE.md", "STYLE_GUIDE(29).md"]:
        open(os.path.join(d, n), "w").close()
    p, v = gda.find_latest(d, "STYLE_GUIDE.md")
    assert "STYLE_GUIDE(29).md" in p
    assert v == 29

def test_find_latest_excludes_template_backup_old():
    gda = _auditor()
    d = tempfile.mkdtemp()
    for n in ["STYLE_GUIDE_TEMPLATE.md", "STYLE_GUIDE_BACKUP.md", "STYLE_GUIDE_OLD.md"]:
        open(os.path.join(d, n), "w").close()
    p, _ = gda.find_latest(d, "STYLE_GUIDE.md")
    assert p is None

# ────────────────────────────────────────────────────────
# 3  check_links fragment support (no monkeypatch pollution)
# ────────────────────────────────────────────────────────
def test_links_fragment_accepted():
    gda = _auditor()
    d = tempfile.mkdtemp()
    open(os.path.join(d, "Target.md"), "w").close()
    text = "see [Target](Target.md#section)"
    gda.issues = []
    gda.check_links([("Test.md", text)], d)
    assert not any(i.p == "P1" for i in gda.issues)
    gda.issues = []  # clean up after ourselves

# ────────────────────────────────────────────────────────
# 4  Full fixture integrations
# ────────────────────────────────────────────────────────
def test_fixture_sample_open_world():
    passed, c, _ = run_auditor(
        fixture_md("sample_open_world"), fixture_profile("sample_open_world"),
    )
    assert passed
    assert c == {"p0": 0, "p1": 0, "p2": 0, "p3": 0, "info": 0}

def test_fixture_minimal_zh_fallback():
    passed, c, _ = run_auditor(
        fixture_md("minimal_zh_fallback"), fixture_profile("minimal_zh_fallback"),
    )
    assert c == {"p0": 0, "p1": 0, "p2": 0, "p3": 0, "info": 0}

def test_fixture_broken_boundary():
    passed, c, _ = run_auditor(
        fixture_md("broken_boundary"), fixture_profile("broken_boundary"),
    )
    assert c == {"p0": 0, "p1": 0, "p2": 2, "p3": 0, "info": 0}

def test_fixture_versioned_filename():
    passed, c, _ = run_auditor(
        fixture_md("versioned_filename"), fixture_profile("versioned_filename"),
    )
    assert c == {"p0": 0, "p1": 0, "p2": 0, "p3": 0, "info": 0}

# ────────────────────────────────────────────────────────
# 5  issue_state suppression
# ────────────────────────────────────────────────────────
def _issue_state_seed_id():
    # P3 issue for the RULE anchor without REF: file=anchor_id, msg fixed
    raw = "RULE-SAMPLE-ONLY|ANCHOR-RULE-NO-REF|RULE anchor has no REF"
    return "AUD-P3-" + hashlib.md5(raw.encode()).hexdigest()[:8]

def _seed_state(out_dir, status, reason=""):
    with open(os.path.join(out_dir, "issue_state.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "issue_id": _issue_state_seed_id(),
            "status": status,
            "level": "P3",
            "file": "RULE-SAMPLE-ONLY",
            "msg": "RULE anchor has no REF",
            "reason": reason,
        }, ensure_ascii=False) + "\n")

def test_issue_state_suppression():
    root = fixture_md("issue_state")
    out = tempfile.mkdtemp(prefix="gdd_is_")
    _seed_state(out, "ACCEPTED_EXCEPTION", "test-accepted")
    passed, c, issues = run_auditor(
        root, fixture_profile("issue_state"),
        out=out, write_state=True, write_history=False,
        engine_version=1,
    )
    assert c["p3"] == 0
    assert c["p0"] == 0

def test_issue_state_no_state_opt_out():
    root = fixture_md("issue_state")
    out = tempfile.mkdtemp(prefix="gdd_is2_")
    _seed_state(out, "ACCEPTED_EXCEPTION", "test")
    # write_state=False → suppression is skipped
    passed, c, _ = run_auditor(
        root, fixture_profile("issue_state"),
        out=out, write_state=False, write_history=False,
        engine_version=1,
    )
    assert c["p3"] == 1

# ────────────────────────────────────────────────────────
# 6  strict / pedantic / fail-on-p2
# ────────────────────────────────────────────────────────
def test_strict_mode_p2_blocks():
    root = fixture_md("strict_mode")
    passed, _, _ = run_auditor(root, fixture_profile("strict_mode"), strict=False)
    assert passed
    passed, _, _ = run_auditor(root, fixture_profile("strict_mode"), strict=True)
    assert not passed

def test_pedantic_mode_p2_blocks():
    root = fixture_md("strict_mode")
    passed, _, _ = run_auditor(root, fixture_profile("strict_mode"), pedantic=True)
    assert not passed

# ────────────────────────────────────────────────────────
# 7  baseline compare (P0-P3 only, INFO excluded per decision D)
# ────────────────────────────────────────────────────────
def test_baseline_compare_ignores_info():
    root = fixture_md("versioned_filename")
    _, c, _ = run_auditor(
        root, fixture_profile("versioned_filename"),
        baseline_path=expected_json("versioned_filename_baseline.json"),
    )
    assert c == {"p0": 0, "p1": 0, "p2": 0, "p3": 0, "info": 0}

# ────────────────────────────────────────────────────────
# 8  Project_Profile loading
# ────────────────────────────────────────────────────────
def test_profile_loads_enabled_docs():
    gda = _auditor()
    prof = gda.load_profile(fixture_profile("sample_open_world"))
    assert "Design_Document.md" in prof["enabled_docs"]

# ────────────────────────────────────────────────────────
# 9  exceptions
# ────────────────────────────────────────────────────────
def test_exception_suppresses_issue():
    gda = _auditor()
    gda.issues[:] = []
    gda.add("P2", "Test.md", "boundary hit", rule="EX-TEST")
    gda.apply_exceptions([{"id": "EX-TEST", "file": "Test.md", "reason": "waived"}])
    assert len(gda.issues) == 0


# ────────────────────────────────────────────────────────
# 10  profile schema validation
# ────────────────────────────────────────────────────────
import glob as _glob
try:
    import yaml as _yaml
except ImportError:
    _yaml = None


def _validate_file(path, kind):
    """Call the validate tool programmatically. Returns list of error strings."""
    with open(path, encoding="utf-8") as f:
        data = _yaml.safe_load(f) if _yaml else {}
    from tools.validate_profile import validate
    return validate(data, kind=kind)


def test_all_genre_profiles_valid():
    if _yaml is None:
        pytest.skip("yaml not available")
    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in _glob.glob(os.path.join(skill, "profiles", "genre", "*.yaml")):
        errors = _validate_file(p, "genre")
        assert errors == [], f"{os.path.basename(p)}: {errors}"


def test_project_profile_template_valid(tmp_path):
    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template = os.path.join(skill, "templates", "PROJECT_PROFILE_TEMPLATE.yaml")
    p = tmp_path / "Project_Profile.yaml"
    p.write_text(
        open(template, encoding="utf-8").read().replace("{{LANGUAGE}}", "en-US"),
        encoding="utf-8",
    )
    errors = _validate_file(str(p), "project")
    assert errors == [], f"template: {errors}"


def test_invalid_profile_detected(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("schema_version: 1\nenabled_docs: [Design_Document.md]\nunknown_field: oops\n", encoding="utf-8")
    errors = _validate_file(str(p), "project")
    assert errors  # should NOT be empty


def test_missing_required_detected(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("schema_version: 1\n", encoding="utf-8")
    errors = _validate_file(str(p), "project")
    assert any("enabled_docs" in e.lower() for e in errors)


# ────────────────────────────────────────────────────────
# 11  scaffold
# ────────────────────────────────────────────────────────
def test_scaffold_and_audit(tmp_path):
    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile = os.path.join(skill, "profiles", "genre", "open_world_narrative_tactical_shooter.yaml")
    out = tmp_path / "md file"
    audit = tmp_path / "audit"
    # Import the scaffold engine and run it programmatically
    from tools.scaffold_project import scaffold
    assert scaffold(profile, str(out), "test-project", "en-US")
    # Audit the scaffolded project
    passed, c, _ = run_auditor(
        str(out),
        os.path.join(str(out), "Project_Profile.yaml"),
        os.path.join(str(out), "STYLE_GUIDE.md"),
        out=str(audit),
    )
    assert c["p0"] == 0
    assert c["p1"] == 0

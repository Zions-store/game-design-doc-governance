# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import pytest

# The auditor lives one level up from tests/, inside tools/
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "tools"))
# Also add the skill root itself - lets tests import tools.validate_profile etc.
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

FIXTURES_DIR = os.path.join(SKILL_ROOT, "tests", "fixtures")
EXPECTED_DIR = os.path.join(SKILL_ROOT, "tests", "expected")


def _auditor():
    import global_doc_audit as gda
    return gda


def run_auditor(root, profile, style=None, out=None, **kw):
    """Run the auditor against a fixture and return (passed, counts_dict, issues_list)."""
    gda = _auditor()
    if out is None:
        out = tempfile.mkdtemp(prefix="gdd_test_")
    if style is None:
        style = os.path.join(root, "STYLE_GUIDE.md")
    write_history = kw.pop("write_history", False)
    write_state = kw.pop("write_state", False)
    passed = gda.run_audit(
        root, out, profile, style,
        write_history=write_history, write_state=write_state,
        **kw
    )
    report = os.path.join(out, "audit_report.json")
    if os.path.exists(report):
        import json
        with open(report, encoding="utf-8") as f:
            data = json.load(f)
        counts = {k: data[k] for k in ("p0", "p1", "p2", "p3", "info")}
        issues = data.get("issues", [])
    else:
        counts = {}
        issues = []
    return passed, counts, issues


def fixture_md(name):
    return os.path.join(FIXTURES_DIR, name, "md file")


def fixture_profile(name):
    return os.path.join(FIXTURES_DIR, name, "md file", "Project_Profile.yaml")


def expected_json(name):
    return os.path.join(EXPECTED_DIR, name)

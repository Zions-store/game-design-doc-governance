# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Audit engine core — AuditContext, Finding, and config validation.

The v2 engine encapsulates audit state in an AuditContext and models
results as structured Findings. It validates configuration strictly
before running any checks.

Usage (v2 path):
    from game_design_doc_governance.engine import AuditContext, Finding, run_audit
    ctx = AuditContext(root="...", style="...", profile="...", out="...")
    findings = run_audit(ctx)
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

SCRIPT_VERSION = "v1.4.0-generic"


# ─── Data classes ──────────────────────────────────────────────

@dataclass
class Finding:
    """A single audit finding with stable identity."""
    id: str
    level: str          # P0 / P1 / P2 / P3 / INFO
    rule: str
    message: str
    file: str = ""
    location: str = ""
    suppressed: bool = False

    @staticmethod
    def make_id(level: str, rule: str, message: str, file: str = "") -> str:
        """Stable issue ID based on rule + location fingerprint, not message text."""
        seed = f"{level}|{rule}|{file}|{message}"
        h = hashlib.md5(seed.encode("utf-8")).hexdigest()[:8]
        return f"AUD-{level}-{h}"


@dataclass
class AuditContext:
    """Encapsulates all audit configuration and mutable state."""
    # Inputs
    root: str
    style: str
    profile: str
    out: str
    language: str = ""

    # Options
    strict: bool = False
    no_state: bool = False
    no_history: bool = False
    md_only: bool = False
    json_only: bool = False
    baseline_file: Optional[str] = None
    engine_version: int = 1   # 1 = legacy, 2 = strict validation

    # Loaded state
    profile_data: dict = field(default_factory=dict)
    style_rules: dict = field(default_factory=dict)

    # Results
    findings: list = field(default_factory=list)
    run_id: str = ""
    started_at: str = ""
    completed_at: str = ""


# ─── Config validation ─────────────────────────────────────────

def validate_profile(profile_data: dict, strict: bool = False) -> list[Finding]:
    """Validate profile structure before running audit checks.
    
    Returns a list of config-level Findings. Empty list = valid.
    """
    issues = []

    if not isinstance(profile_data, dict):
        issues.append(Finding(
            id=Finding.make_id("P0", "CONFIG-INVALID-PROFILE", "Profile is not a valid YAML dict"),
            level="P0", rule="CONFIG-INVALID-PROFILE",
            message="Profile file does not contain a valid YAML dictionary."
        ))
        return issues

    if "enabled_docs" not in profile_data:
        issues.append(Finding(
            id=Finding.make_id("P0", "CONFIG-MISSING-ENABLED-DOCS", "enabled_docs is required"),
            level="P0", rule="CONFIG-MISSING-ENABLED-DOCS",
            message="Profile is missing required field: enabled_docs"
        ))

    # Strict-mode checks
    if strict:
        schema_version = profile_data.get("schema_version")
        if schema_version is None:
            issues.append(Finding(
                id=Finding.make_id("P1", "CONFIG-NO-SCHEMA-VERSION", "schema_version is missing"),
                level="P1", rule="CONFIG-NO-SCHEMA-VERSION",
                message="Profile missing schema_version field."
            ))

        # Check deprecated_terms structure if present
        deprecated = profile_data.get("deprecated_terms", [])
        if isinstance(deprecated, list):
            for i, dt in enumerate(deprecated):
                if not isinstance(dt, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-DEPRECATED", f"deprecated_terms[{i}] is not a dict"),
                        level="P2", rule="CONFIG-BAD-DEPRECATED",
                        message=f"deprecated_terms[{i}] is not a dictionary."
                    ))
                elif "old" not in dt:
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-DEPRECATED", f"deprecated_terms[{i}] missing 'old'"),
                        level="P2", rule="CONFIG-BAD-DEPRECATED",
                        message=f"deprecated_terms[{i}] missing required field: old"
                    ))

        # Check boundary_checks structure
        boundary = profile_data.get("boundary_checks", [])
        if isinstance(boundary, list):
            for i, bc in enumerate(boundary):
                if not isinstance(bc, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-BOUNDARY", f"boundary_checks[{i}] is not a dict"),
                        level="P2", rule="CONFIG-BAD-BOUNDARY",
                        message=f"boundary_checks[{i}] is not a dictionary."
                    ))
                elif "id" not in bc:
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-BOUNDARY", f"boundary_checks[{i}] missing 'id'"),
                        level="P2", rule="CONFIG-BAD-BOUNDARY",
                        message=f"boundary_checks[{i}] missing required field: id"
                    ))

        # Check exceptions structure
        exceptions = profile_data.get("exceptions", [])
        if isinstance(exceptions, list):
            for i, exc in enumerate(exceptions):
                if not isinstance(exc, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-EXCEPTION", f"exceptions[{i}] is not a dict"),
                        level="P2", rule="CONFIG-BAD-EXCEPTION",
                        message=f"exceptions[{i}] is not a dictionary."
                    ))

    return issues


def validate_style_loaded(style_rules: dict) -> list[Finding]:
    """Verify that the STYLE_GUIDE was parsed with minimum requirements."""
    issues = []
    if not style_rules.get("expected_docs"):
        issues.append(Finding(
            id=Finding.make_id("P1", "STYLE-NO-DOCS", "No documents found in STYLE_GUIDE"),
            level="P1", rule="STYLE-NO-DOCS",
            message="STYLE_GUIDE.md did not yield any expected documents."
        ))
    return issues


# ─── Report rendering helpers ──────────────────────────────────

def render_counts(findings: list[Finding]) -> dict:
    """Aggregate findings by level."""
    counts = defaultdict(int)
    for f in findings:
        if not f.suppressed:
            counts[f.level] += 1
    return dict(counts)


def render_verdict(counts: dict, strict: bool = False) -> str:
    """Determine pass/fail from counts."""
    p0 = counts.get("P0", 0)
    p1 = counts.get("P1", 0)
    p2 = counts.get("P2", 0)
    if p0 > 0 or p1 > 0:
        return "FAIL"
    if strict and p2 > 0:
        return "FAIL"
    return "PASS"


def _make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("AUDIT-%Y%m%d-%H%M")

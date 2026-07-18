# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Audit engine core — AuditContext, Finding, waiver management, state, and reports.

The v2 engine encapsulates audit state, models results as structured Findings
with stable identities, manages waivers with expiration, tracks per-issue state
with atomic writes, and produces versioned reports.

Usage:
    from game_design_doc_governance.engine import AuditContext, Finding, WaiverManager, StateManager
"""

import os
import re
import json
import hashlib
import tempfile
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

SCRIPT_VERSION = "v1.7.0-generic"
STATE_SCHEMA_VERSION = 1


# ─── Data classes ──────────────────────────────────────────────

@dataclass
class Finding:
    """A single audit finding with stable identity (v2 fingerprint)."""
    id: str
    level: str
    rule: str
    message: str
    file: str = ""
    location: str = ""
    suppressed: bool = False
    suppression_reason: str = ""

    @staticmethod
    def make_id(level: str, rule: str, message: str, file: str = "") -> str:
        """Stable issue ID based on rule + file fingerprint, NOT message text.

        Two findings with the same rule and file will share the same ID
        even if the message text changes between audits. This prevents
        wording improvements from appearing as "new issues."
        """
        seed = f"{level}|{rule}|{file}"
        h = hashlib.md5(seed.encode("utf-8")).hexdigest()[:8]
        return f"AUD-{level}-{h}"

    def to_dict(self) -> dict:
        d = {"id": self.id, "level": self.level, "rule": self.rule,
             "message": self.message, "file": self.file}
        if self.location:
            d["location"] = self.location
        if self.suppressed:
            d["suppressed"] = True
            d["suppression_reason"] = self.suppression_reason
        return d


@dataclass
class AuditContext:
    """Encapsulates all audit configuration and mutable state."""
    root: str
    style: str
    profile: str
    out: str
    language: str = ""
    strict: bool = False
    no_state: bool = False
    no_history: bool = False
    md_only: bool = False
    json_only: bool = False
    baseline_file: Optional[str] = None
    engine_version: int = 1
    profile_data: dict = field(default_factory=dict)
    style_rules: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)
    run_id: str = ""
    started_at: str = ""
    completed_at: str = ""


# ─── Waiver management ──────────────────────────────────────────

@dataclass
class Waiver:
    """A registered waiver that suppresses a specific finding."""
    id: str              # finding rule ID (e.g. "CONFIG-BAD-DEPRECATED")
    file: str = ""       # optional: scoped to a specific file
    reason: str = ""
    expires: Optional[str] = None   # ISO 8601 date, or None = never

    @staticmethod
    def from_dict(d: dict) -> "Waiver":
        return Waiver(
            id=d.get("id", ""),
            file=d.get("file", ""),
            reason=d.get("reason", ""),
            expires=d.get("expires")
        )

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if not self.expires:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires)
        except (ValueError, TypeError):
            return False
        ref = now or datetime.now(timezone.utc)
        # Normalize timezone: compare naive-to-naive or aware-to-aware
        if expiry.tzinfo is None and ref.tzinfo is not None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        elif expiry.tzinfo is not None and ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)
        return ref > expiry

    def matches(self, finding_rule: str, finding_file: str = "") -> bool:
        """Match waiver by rule name (e.g. 'GDD-SUMMARY-ONLY-ENERGY'), not hash ID."""
        if finding_rule != self.id:
            return False
        if self.file and self.file != finding_file:
            return False
        return True


class WaiverManager:
    """Manages a collection of waivers with expiration enforcement."""

    def __init__(self):
        self._waivers: list[Waiver] = []

    def load_from_profile(self, exceptions: list):
        """Load waivers from profile.exceptions[].id / .file / .reason / .expires."""
        for exc in exceptions:
            if isinstance(exc, dict):
                self._waivers.append(Waiver.from_dict(exc))

    def apply(self, findings: list[Finding]) -> tuple[list[Finding], list[Waiver], list[Waiver]]:
        """Apply waivers to findings. Returns (suppressed_findings, active_waivers, expired_waivers)."""
        now = datetime.now(timezone.utc)
        active = []
        expired = []

        for w in self._waivers:
            if w.is_expired(now):
                expired.append(w)
                continue
            active.append(w)

        for f in findings:
            for w in active:
                if w.matches(f.rule, f.file):
                    f.suppressed = True
                    f.suppression_reason = f"waiver: {w.reason}" if w.reason else "waiver"
                    break

        return findings, active, expired


# ─── State management ───────────────────────────────────────────

STATE_FILE = "issue_state.jsonl"


class StateManager:
    """Versioned per-issue state ledger with atomic writes and corruption detection."""

    def __init__(self, out_dir: str):
        self.path = os.path.join(out_dir, STATE_FILE)

    def load(self) -> dict:  # {issue_id: {status, updated_at, ...}}
        if not os.path.exists(self.path):
            return {}

        states = {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        iid = entry.get("issue_id")
                        if iid:
                            states[iid] = entry
                    except json.JSONDecodeError:
                        # Corrupt line: record but don't crash
                        cid = f"CORRUPT-{line_no}"
                        states[cid] = {
                            "issue_id": cid, "status": "CORRUPT",
                            "error": f"invalid JSON on line {line_no}",
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
            return states
        except (OSError, UnicodeDecodeError) as e:
            return {
                "STATE_FILE_ERROR": {
                    "issue_id": "STATE_FILE_ERROR",
                    "status": "CORRUPT",
                    "error": f"Cannot read state file: {e}",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }

    def save(self, findings: list[Finding], prev_state: dict) -> dict:
        """Write updated state file atomically. Returns the new state dict."""
        updated = dict(prev_state)
        now = datetime.now(timezone.utc).isoformat()

        for f in findings:
            if f.id not in updated:
                updated[f.id] = {"issue_id": f.id, "status": "OPEN", "updated_at": now}
            else:
                entry = updated[f.id]
                if entry["status"] == "OPEN":
                    pass  # keep OPEN
                elif entry["status"] == "FIXED_PENDING_VERIFY":
                    entry["status"] = "VERIFIED"
                    entry["updated_at"] = now
                elif entry["status"] == "REOPENED":
                    pass

        # Write atomically: temp file + rename
        try:
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path), prefix=".issue_state_")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                for iid in sorted(updated):
                    entry = updated[iid]
                    entry.setdefault("_schema", STATE_SCHEMA_VERSION)
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            os.replace(tmp, self.path)
        except OSError:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

        return updated

    def get_suppressed_ids(self, states: dict) -> set:
        """Return issue IDs that are human-confirmed as false-positive or accepted-exception."""
        return {iid for iid, e in states.items()
                if e.get("status") in ("FALSE_POSITIVE", "ACCEPTED_EXCEPTION")}


# ─── Report rendering ───────────────────────────────────────────

def render_report_v2(findings: list[Finding], ctx: AuditContext,
                     waivers_active: list[Waiver] = None,
                     waivers_expired: list[Waiver] = None) -> str:
    """Render v2 audit report with UTC timestamps and waiver details."""
    waivers_active = waivers_active or []
    waivers_expired = waivers_expired or []

    now = datetime.now(timezone.utc)
    run_id = ctx.run_id or now.strftime("AUDIT-%Y%m%d-%H%M%S")
    started = ctx.started_at or now.isoformat()

    counts = render_counts(findings)
    suppressed_count = sum(1 for f in findings if f.suppressed)
    total = len(findings)

    lines = [
        "# Audit Report v2",
        "",
        f"- **Run ID**: {run_id}",
        f"- **Started**: {started}",
        f"- **Engine**: v{ctx.engine_version}",
        f"- **Script**: {SCRIPT_VERSION}",
        f"- **Root**: {ctx.root}",
        f"- **Profile**: {os.path.basename(ctx.profile)}",
        f"- **Style**: {os.path.basename(ctx.style)}",
        "",
        "## Summary",
        "",
        "| Level | Count |",
        "|-------|-------|",
    ]

    for level in ("P0", "P1", "P2", "P3", "INFO"):
        lines.append(f"| {level} | {counts.get(level, 0)} |")
    lines.append(f"| _suppressed_ | {suppressed_count} |")

    if waivers_active:
        lines.append(f"\n**Active waivers**: {len(waivers_active)}")
    if waivers_expired:
        lines.append(f"\n**Expired waivers**: {len(waivers_expired)}")

    for level in ("P0", "P1", "P2", "P3", "INFO"):
        level_findings = [f for f in findings if f.level == level and not f.suppressed]
        if level_findings:
            lines.append(f"\n## {level}")
            for f in level_findings:
                loc = f" ({f.location})" if f.location else ""
                lines.append(f"- [{f.id}] **{f.file}**{loc}: {f.message}")

    # Suppressed section
    suppressed_findings = [f for f in findings if f.suppressed]
    if suppressed_findings:
        lines.append(f"\n## Suppressed")
        for f in suppressed_findings:
            lines.append(f"- [{f.id}] **{f.file}**: {f.message} _(reason: {f.suppression_reason})_")

    # Expired waivers
    if waivers_expired:
        lines.append(f"\n## Expired Waivers")
        for w in waivers_expired:
            fid = f" [{w.file}]" if w.file else ""
            lines.append(f"- `{w.id}`{fid}: expired {w.expires}")

    verdict = render_verdict(counts, ctx.strict)
    lines.append(f"\n## Verdict")
    lines.append(f"- **{verdict}** "
                 f"(P0={counts.get('P0',0)} P1={counts.get('P1',0)} "
                 f"P2={counts.get('P2',0)} P3={counts.get('P3',0)})")

    return "\n".join(lines)


def render_counts(findings: list[Finding]) -> dict:
    counts = defaultdict(int)
    for f in findings:
        if not f.suppressed:
            counts[f.level] += 1
    return dict(counts)


def render_verdict(counts: dict, strict: bool = False) -> str:
    p0 = counts.get("P0", 0)
    p1 = counts.get("P1", 0)
    p2 = counts.get("P2", 0)
    if p0 > 0 or p1 > 0:
        return "FAIL"
    if strict and p2 > 0:
        return "FAIL"
    return "PASS"


# ─── Config validation ─────────────────────────────────────────

def validate_profile(profile_data: dict, strict: bool = False) -> list[Finding]:
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
    if strict:
        schema_version = profile_data.get("schema_version")
        if schema_version is None:
            issues.append(Finding(
                id=Finding.make_id("P1", "CONFIG-NO-SCHEMA-VERSION", "schema_version is missing"),
                level="P1", rule="CONFIG-NO-SCHEMA-VERSION",
                message="Profile missing schema_version field."
            ))
        deprecated = profile_data.get("deprecated_terms", [])
        if isinstance(deprecated, list):
            for i, dt in enumerate(deprecated):
                if not isinstance(dt, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-DEPRECATED", f"depr_term[{i}]"),
                        level="P2", rule="CONFIG-BAD-DEPRECATED",
                        message=f"deprecated_terms[{i}] is not a dictionary."
                    ))
                elif "old" not in dt:
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-DEPRECATED", f"depr_term[{i}]"),
                        level="P2", rule="CONFIG-BAD-DEPRECATED",
                        message=f"deprecated_terms[{i}] missing required field: old"
                    ))
        boundary = profile_data.get("boundary_checks", [])
        if isinstance(boundary, list):
            for i, bc in enumerate(boundary):
                if not isinstance(bc, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-BOUNDARY", f"boundary[{i}]"),
                        level="P2", rule="CONFIG-BAD-BOUNDARY",
                        message=f"boundary_checks[{i}] is not a dictionary."
                    ))
                elif "id" not in bc:
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-BOUNDARY", f"boundary[{i}]"),
                        level="P2", rule="CONFIG-BAD-BOUNDARY",
                        message=f"boundary_checks[{i}] missing required field: id"
                    ))
        exceptions = profile_data.get("exceptions", [])
        if isinstance(exceptions, list):
            for i, exc in enumerate(exceptions):
                if not isinstance(exc, dict):
                    issues.append(Finding(
                        id=Finding.make_id("P2", "CONFIG-BAD-EXCEPTION", f"exc[{i}]"),
                        level="P2", rule="CONFIG-BAD-EXCEPTION",
                        message=f"exceptions[{i}] is not a dictionary."
                    ))
    return issues

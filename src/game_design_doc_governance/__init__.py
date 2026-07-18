# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
game-design-doc-governance - a reusable governance framework for game design
documentation. This package provides console-script entry points for the auditor
and profile validator, plus the v2 audit engine core.

v2 engine (engine.py) provides AuditContext, Finding, and config validation.
"""

from game_design_doc_governance.engine import (
    AuditContext, Finding, Waiver, WaiverManager, StateManager,
    validate_profile, render_report_v2, render_counts, render_verdict
)

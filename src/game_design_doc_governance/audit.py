# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Console-script entry point for `gdd-audit`.

Resolves the canonical audit engine (tools/global_doc_audit.py) relative to this
package, then re-runs it as __main__, forwarding all CLI arguments unchanged.
"""
import os
import sys
import runpy


def main():
    # The tools/ directory is a sibling of src/ at the package root
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    engine = os.path.join(root, "tools", "global_doc_audit.py")
    if not os.path.exists(engine):
        sys.stderr.write("ERROR: canonical audit engine not found at: %s\n" % engine)
        return 1
    runpy.run_path(engine, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

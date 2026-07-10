# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Console-script entry point for `gdd-scaffold`."""
import os, sys, runpy

def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tool = os.path.join(root, "tools", "scaffold_project.py")
    if not os.path.exists(tool):
        sys.stderr.write("ERROR: scaffold engine not found at: %s\n" % tool)
        return 1
    runpy.run_path(tool, run_name="__main__")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

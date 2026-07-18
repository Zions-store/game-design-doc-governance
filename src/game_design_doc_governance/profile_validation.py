# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Console-script entry point for `gdd-profile-validate`.

Resolves the canonical validator (tools/validate_profile.py) relative to this
package, then re-runs it as __main__, forwarding all CLI arguments unchanged.
"""
import os
import sys
import runpy


def main():
    package_tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tools", "validate_profile.py")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    validator = package_tool if os.path.exists(package_tool) else os.path.join(root, "tools", "validate_profile.py")
    if not os.path.exists(validator):
        sys.stderr.write("ERROR: profile validator not found at: %s\n" % validator)
        return 1
    runpy.run_path(validator, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

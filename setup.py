# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build-time packaging hooks for runtime governance assets."""

from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


ROOT = Path(__file__).parent.resolve()
ASSET_DIRECTORIES = ("doc_modules", "profiles", "rules", "schemas", "templates")
RUNTIME_TOOLS = ("global_doc_audit.py", "scaffold_project.py", "validate_profile.py")


class BuildPyWithRuntimeAssets(_build_py):
    """Bundle root-owned runtime assets without duplicating their source."""

    def run(self) -> None:
        super().run()
        package_root = Path(self.build_lib) / "game_design_doc_governance"
        assets_root = package_root / "assets"
        for directory in ASSET_DIRECTORIES:
            copytree(ROOT / directory, assets_root / directory, dirs_exist_ok=True)

        tools_root = package_root / "_tools"
        tools_root.mkdir(parents=True, exist_ok=True)
        for tool in RUNTIME_TOOLS:
            copy2(ROOT / "tools" / tool, tools_root / tool)


setup(cmdclass={"build_py": BuildPyWithRuntimeAssets})

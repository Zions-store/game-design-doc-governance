#!/usr/bin/env python3
# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Initialize a new project's design-document directory from a genre profile.

Usage:
  gdd-scaffold --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \\
               --out "<project>/Design Document/md file" \\
               --project-name "My Game" [--language en-US]

The tool copies doc_module skeletons, fills STYLE_GUIDE / Project_Profile /
Design_Document templates, and creates an audit/ directory. No lore, faction
names, or gameplay numbers are invented.
"""

import os
import sys
import shutil
import argparse

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_MODULES = os.path.join(SKILL_ROOT, "doc_modules")
TEMPLATES = os.path.join(SKILL_ROOT, "templates")

LANGS = {
    "en-US": {
        "gdd_title": "Design Document (GDD)",
        "gdd_tagline": "Index only - sub-documents carry full content.",
        "gdd_systems": "## Systems",
        "gdd_system_link": "- See [{doc}]({doc}.md)",
        "style_chapters": {
            "2": "Authoritative File List",
            "6.2": "Anchor registry",
            "6.3": "Deprecated-term registry",
        },
    },
    "zh-CN": {
        "gdd_title": "璁捐鏂囨。 (GDD)",
        "gdd_tagline": "浠呬綔绱㈠紩--瀹屾暣鍐呭鍦ㄥ瓙鏂囨。涓€?,
        "gdd_systems": "## 绯荤粺",
        "gdd_system_link": "- 鍙傝 [{doc}]({doc}.md)",
        "style_chapters": {
            "2": "鏂囦欢娓呭崟",
            "6.2": "宸插缓绔嬮敋鐐规竻鍗?,
            "6.3": "搴熷純璇存硶鐧昏琛?,
        },
    },
}


def _fill_template(tmpl_path, out_path, replacements):
    with open(tmpl_path, encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements.items():
        text = text.replace(old, new)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def scaffold(profile_path, out_dir, project_name="Untitled Game", language="en-US"):
    lang = LANGS.get(language, LANGS["en-US"])

    # 1. Load the genre profile
    try:
        import yaml
    except ImportError:
        print("PyYAML is required. Install it: pip install pyyaml", file=sys.stderr)
        return False
    with open(profile_path, encoding="utf-8") as f:
        profile = yaml.safe_load(f) or {}
    recommended = profile.get("recommended_docs") or profile.get("enabled_docs") or []
    optional = profile.get("optional_docs") or []
    enabled = list(dict.fromkeys(recommended + optional))  # dedupe, preserve order

    os.makedirs(out_dir, exist_ok=True)

    # 2. Copy doc_module skeletons for each enabled doc
    for doc in enabled:
        base = doc.replace(".md", "")
        src = os.path.join(DOC_MODULES, base + ".md.tmpl")
        dst = os.path.join(out_dir, doc)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            # Minimal skeleton
            with open(dst, "w", encoding="utf-8") as f:
                f.write(f"# {base}\n\n馃敳 TODO - skeleton for {doc}.\n")

    # 3. Design_Document.md from template or minimal
    gdd_tmpl = os.path.join(TEMPLATES, "DESIGN_DOCUMENT_TEMPLATE.md")
    gdd_out = os.path.join(out_dir, "Design_Document.md")
    if os.path.exists(gdd_tmpl):
        _fill_template(gdd_tmpl, gdd_out, {
            "{{PROJECT_NAME}}": project_name,
            "{{ONE_LINE_PITCH}}": f"{project_name} - {profile.get('profile', {}).get('description', '')}"[:120],
            "{{PRIMARY_TYPE}}": profile.get("profile", {}).get("primary_type", ""),
            "{{GAMEPLAY_SUMMARY}}": "",
            "{{MISSION_SUMMARY}}": "",
            "{{WORLD_SUMMARY}}": "",
            "{{NARRATIVE_SUMMARY}}": "",
            "{{CHARACTER_SUMMARY}}": "",
            "{{RESOURCE_SUMMARY}}": "",
            "{{COLLECTIBLES_SUMMARY}}": "",
        })
    else:
        links = "\n".join(lang["gdd_system_link"].format(doc=d.replace(".md", ""))
                          for d in enabled if d != "Design_Document.md" and d != "STYLE_GUIDE.md")
        with open(gdd_out, "w", encoding="utf-8") as f:
            f.write(f"# {project_name} - {lang['gdd_title']}\n\n"
                    f"{lang['gdd_tagline']}\n\n"
                    f"{lang['gdd_systems']}\n{links}\n")

    # 4. STYLE_GUIDE.md from template
    style_tmpl = os.path.join(TEMPLATES, "STYLE_GUIDE_TEMPLATE.md")
    style_out = os.path.join(out_dir, "STYLE_GUIDE.md")
    if os.path.exists(style_tmpl):
        # Build a minimal enabled-docs table
        rows = "\n".join(f"| {d} | - | 鉁?|" for d in enabled)
        _fill_template(style_tmpl, style_out, {
            "{{PROJECT_NAME}}": project_name,
            "{{ENABLED_DOCS_TABLE}}": rows,
            "{{AUTHORITY_MATRIX}}": "| Content type | Authority doc |\n|---|---|",
            "{{BOUNDARY_RULES}}": "",
            "{{ANCHOR_REGISTRY}}": "| Anchor ID | Setting |\n|---|---|",
            "{{DEPRECATED_TERMS_TABLE}}": "| Deprecated | Correct |\n|---|---|",
            "{{NON_AUTHORITY_FILES}}": "",
            "{{NUMBERING_EXCEPTIONS}}": "",
            "{{DO_NOT_CREATE_LIST}}": "",
            "{{KNOWN_EXCEPTIONS_TABLE}}": "",
        })

    # 5. Project_Profile.yaml from template
    prof_tmpl = os.path.join(TEMPLATES, "PROJECT_PROFILE_TEMPLATE.yaml")
    prof_out = os.path.join(out_dir, "Project_Profile.yaml")
    if os.path.exists(prof_tmpl):
        docs_yaml = "\n".join(f"  - {d}" for d in enabled)
        _fill_template(prof_tmpl, prof_out, {
            "{{PROJECT_NAME}}": project_name,
            "{{PROFILE_NAME}}": profile.get("profile", {}).get("name", ""),
            "{{PRIMARY_TYPE}}": profile.get("profile", {}).get("primary_type", ""),
            "{{SNAPSHOT_OR_LOG_FILE}}": "Design_Document.docx",
        })
        # Write enabled_docs into the file if the template uses placeholder
        with open(prof_out, encoding="utf-8") as f:
            text = f.read()
        text = text.replace("enabled_docs: []", f"enabled_docs:\n{docs_yaml}")
        text = text.replace("enabled_docs: []", f"enabled_docs:\n{docs_yaml}")
        with open(prof_out, "w", encoding="utf-8") as f:
            f.write(text)

    # 6. audit/ directory
    audit_dir = os.path.join(os.path.dirname(out_dir), "audit")
    os.makedirs(audit_dir, exist_ok=True)
    readme = os.path.join(audit_dir, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Audit\n\nRun `gdd-audit` here after populating the design documents.\n")

    return True


def main():
    ap = argparse.ArgumentParser(description="Initialize a new design-doc project from a genre profile.")
    ap.add_argument("--profile", required=True, help="Path to genre profile (.yaml)")
    ap.add_argument("--out", required=True, help="Output directory (e.g. '<project>/Design Document/md file')")
    ap.add_argument("--project-name", default="Untitled Game", help="Project name")
    ap.add_argument("--language", default="en-US", choices=["en-US", "zh-CN"],
                    help="Output language (default: en-US)")
    args = ap.parse_args()

    if not os.path.exists(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        return 1
    if not os.path.exists(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        return 1

    ok = scaffold(args.profile, args.out, args.project_name, args.language)
    if ok:
        print(f"Scaffolded project '{args.project_name}' in {args.out}")
        print(f"  enabled docs: {len(os.listdir(args.out)) - sum(1 for _ in os.scandir(args.out) if _.is_dir())} md files + Project_Profile.yaml")
        print("  Next: populate docs 鈫?run gdd-audit")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

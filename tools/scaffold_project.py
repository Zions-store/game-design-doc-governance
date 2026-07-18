#!/usr/bin/env python3
# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Initialize a new project's design-document directory from a genre profile.

Usage:
  gdd-scaffold --profile profiles/genre/open_world_narrative_tactical_shooter.yaml \\
               --out "<project>/Design Document/md file" \\
               --project-name "My Game" [--language en-US]

Safety (v2, default):
  - Refuses to write to non-empty directories without --force.
  - --dry-run previews without writing.
  - Optional docs only created when explicitly selected with --enable-doc.
  - All paths validated against directory traversal.
  - Failure cleans up partial output.

v1 legacy (--legacy): restores pre-1.6 behavior (all optional docs, no safety).
"""

import os
import re
import sys
import shutil
import argparse
import tempfile

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
        "gdd_title": "设计文档 (GDD)",
        "gdd_tagline": "仅作索引——完整内容在子文档中。",
        "gdd_systems": "## 系统",
        "gdd_system_link": "- 参见 [{doc}]({doc}.md)",
        "style_chapters": {
            "2": "文件清单",
            "6.2": "已建立锚点清单",
            "6.3": "废弃说法登记表",
        },
    },
}

CREATED = []  # Track created paths for cleanup


def _safe_write(path: str, content: str):
    """Atomic write via temp file + rename."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d or ".", prefix=".scaffold_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except OSError:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    CREATED.append(path)


def _safe_copy(src: str, dst: str):
    d = os.path.dirname(dst)
    if d:
        os.makedirs(d, exist_ok=True)
    shutil.copy2(src, dst)
    CREATED.append(dst)


def _validate_path(out_dir: str) -> str:
    """Prevent directory traversal. Returns normalized absolute path."""
    # Check BEFORE normalization — raw '..' patterns are the threat
    raw = out_dir.replace('\\', '/')
    if '/../' in f'/{raw}/' or raw.startswith('../'):
        raise ValueError(f"Path contains traversal: {out_dir}")
    resolved = os.path.normpath(os.path.abspath(out_dir))
    if '..' in resolved.split(os.sep):
        raise ValueError(f"Path resolves with traversal: {out_dir} -> {resolved}")
    if resolved == os.sep or (os.path.splitdrive(resolved)[1] in ('\\', '/')):
        raise ValueError(f"Path must not be filesystem root: {out_dir}")
    return resolved


def _fill_template(tmpl_path, out_path, replacements):
    with open(tmpl_path, encoding="utf-8") as f:
        text = f.read()
    for old, new in replacements.items():
        text = text.replace(old, new)
    _safe_write(out_path, text)


def _is_empty_dir(path: str) -> bool:
    if not os.path.isdir(path):
        return True
    return len(os.listdir(path)) == 0


def scaffold(profile_path, out_dir, project_name="Untitled Game", language="en-US",
             dry_run=False, force=False, extra_docs=None, disabled_docs=None,
             legacy=False):
    extra_docs = extra_docs or []
    disabled_docs = disabled_docs or []
    lang = LANGS.get(language, LANGS["en-US"])

    # Normalize language for any-language support
    try:
        from game_design_doc_governance.i18n import normalize_language
        language = normalize_language(language)
    except ImportError:
        pass
    # Safety: restrict language value to prevent YAML injection
    if not re.match(r'^[a-z]{2,3}(-[A-Z]{2,3})?$', language):
        print(f"Warning: language '{language}' is not a valid BCP-47 tag; falling back to en-US", file=sys.stderr)
        language = "en-US"

    # 1. Load the genre profile
    try:
        import yaml
    except ImportError:
        print("PyYAML is required. Install it: pip install pyyaml", file=sys.stderr)
        return False

    if not os.path.exists(profile_path):
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        return False

    with open(profile_path, encoding="utf-8") as f:
        profile = yaml.safe_load(f) or {}

    recommended = profile.get("recommended_docs") or profile.get("enabled_docs") or []
    optional = profile.get("optional_docs") or []
    profile_disabled = profile.get("disabled_docs") or []

    # Compute enabled docs
    if legacy:
        enabled = list(dict.fromkeys(recommended + optional))
    else:
        # v2: Recommended always, Optional only when explicitly selected
        enabled = list(recommended)
        for od in optional:
            if od in extra_docs:
                enabled.append(od)
    # Remove explicitly disabled
    enabled = [d for d in enabled if d not in disabled_docs and d not in profile_disabled]
    # Dedupe, preserve order
    seen = set()
    enabled = [d for d in enabled if not (d in seen or seen.add(d))]

    # Plan output
    plan = _build_plan(profile, enabled, out_dir, project_name, language)
    if dry_run:
        # Validate first, then preview
        if not legacy:
            if os.path.exists(out_dir) and not _is_empty_dir(out_dir) and not force:
                print(f"ERROR: Output directory is not empty: {out_dir}", file=sys.stderr)
                print("Use --force to overwrite, or --dry-run to preview.", file=sys.stderr)
                return False
            try:
                _validate_path(out_dir)
            except ValueError as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return False
        print(f"[DRY RUN] Would create {len(plan)} file(s) in {out_dir}:")
        for p in plan:
            print(f"  {p}")
        print(f"\nEnabled docs ({len(enabled)}): {enabled}")
        return True

    # Directory safety check (v2)
    if not legacy:
        if os.path.exists(out_dir) and not _is_empty_dir(out_dir) and not force:
            print(f"ERROR: Output directory is not empty: {out_dir}", file=sys.stderr)
            print("Use --force to overwrite, or --dry-run to preview.", file=sys.stderr)
            return False
        # Path boundary check
        try:
            _validate_path(out_dir)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return False

    # Execute plan
    try:
        _execute_plan(profile, enabled, out_dir, project_name, lang, language)
    except Exception as e:
        print(f"ERROR during scaffold: {e}", file=sys.stderr)
        _cleanup()
        return False

    # Audit directory
    audit_dir = os.path.join(os.path.dirname(out_dir), "audit")
    os.makedirs(audit_dir, exist_ok=True)
    readme = os.path.join(audit_dir, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Audit\n\nRun `gdd-audit` here after populating the design documents.\n")

    actual = sum(1 for p in plan if os.path.exists(p)) if not dry_run else len(plan)
    print(f"Scaffolded project '{project_name}' in {out_dir}")
    print(f"  enabled docs: {len(enabled)}")
    print("  Next: populate docs → run gdd-audit")
    return True


def _build_plan(profile, enabled, out_dir, project_name, language):
    plan = []
    for doc in enabled:
        plan.append(os.path.join(out_dir, doc))
    # Always scaffold Design_Document, STYLE_GUIDE, Project_Profile
    out = os.path.join(out_dir, "Design_Document.md")
    if out not in plan:
        plan.append(out)
    out = os.path.join(out_dir, "STYLE_GUIDE.md")
    if out not in plan:
        plan.append(out)
    out = os.path.join(out_dir, "Project_Profile.yaml")
    plan.append(out)
    return plan


def _execute_plan(profile, enabled, out_dir, project_name, lang, language="en-US"):
    os.makedirs(out_dir, exist_ok=True)

    # Copy doc_module skeletons
    for doc in enabled:
        base = doc.replace(".md", "")
        src = os.path.join(DOC_MODULES, base + ".md.tmpl")
        dst = os.path.join(out_dir, doc)
        if os.path.exists(src):
            _safe_copy(src, dst)
        else:
            # Mark as unsupported - no TODO fallback
            with open(dst, "w", encoding="utf-8") as f:
                f.write(f"# {base}\n\nThis document has no formal skeleton yet.\n"
                        f"Refer to the STYLE_GUIDE for authority and boundary rules.\n")

    # Design_Document.md
    gdd_tmpl = os.path.join(TEMPLATES, "DESIGN_DOCUMENT_TEMPLATE.md")
    gdd_out = os.path.join(out_dir, "Design_Document.md")
    desc = profile.get("profile", {}).get("description", "")
    if os.path.exists(gdd_tmpl):
        _fill_template(gdd_tmpl, gdd_out, {
            "{{PROJECT_NAME}}": project_name,
            "{{ONE_LINE_PITCH}}": f"{project_name} - {desc}"[:120],
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
        content = (f"# {project_name} - {lang['gdd_title']}\n\n"
                   f"{lang['gdd_tagline']}\n\n"
                   f"{lang['gdd_systems']}\n{links}\n")
        _safe_write(gdd_out, content)

    # STYLE_GUIDE.md
    style_tmpl = os.path.join(TEMPLATES, "STYLE_GUIDE_TEMPLATE.md")
    style_out = os.path.join(out_dir, "STYLE_GUIDE.md")
    if os.path.exists(style_tmpl):
        rows = "\n".join(f"| {d} | - | ✅ |" for d in enabled)
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

    # Project_Profile.yaml
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
        with open(prof_out, encoding="utf-8") as f:
            text = f.read()
        text = text.replace("enabled_docs: []", f"enabled_docs:\n{docs_yaml}")
        # Add v2 fields: profile_type at top level, language inside existing profile block
        text = text.replace("schema_version: 1",
                           f"schema_version: 1\nprofile_type: project")
        # Inject language into the existing profile: mapping safely
        text = text.replace("profile:\n  name:", f"profile:\n  language: {language}\n  name:")
        _safe_write(prof_out, text)


def _cleanup():
    """Remove partially created files on failure."""
    for path in reversed(CREATED):
        try:
            if os.path.isfile(path):
                os.unlink(path)
        except OSError:
            pass
    CREATED.clear()


def main():
    ap = argparse.ArgumentParser(description="Initialize a new design-doc project from a genre profile.")
    ap.add_argument("--profile", required=True, help="Path to genre profile (.yaml)")
    ap.add_argument("--out", required=True, help="Output directory (e.g. '<project>/Design Document/md file')")
    ap.add_argument("--project-name", default="Untitled Game", help="Project name")
    ap.add_argument("--language", default="en-US",
                    help="Output language (e.g. en-US, zh-CN, ja, fr, ar). Default: en-US")
    ap.add_argument("--dry-run", action="store_true", help="Preview plan without writing files")
    ap.add_argument("--force", action="store_true", help="Allow writing to non-empty directory")
    ap.add_argument("--enable-doc", action="append", default=[],
                    help="Explicitly enable an optional doc (repeatable)")
    ap.add_argument("--disable-doc", action="append", default=[],
                    help="Disable a recommended doc (repeatable)")
    ap.add_argument("--legacy", action="store_true",
                    help="Use v1 legacy behavior (all optional docs, no safety checks)")
    args = ap.parse_args()

    if not os.path.exists(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        return 1

    ok = scaffold(args.profile, args.out, args.project_name, args.language,
                  dry_run=args.dry_run, force=args.force,
                  extra_docs=args.enable_doc, disabled_docs=args.disable_doc,
                  legacy=args.legacy)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

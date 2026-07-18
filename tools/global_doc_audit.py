#!/usr/bin/env python3
# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Generic game-design documentation auditor.

Rules come from two sources:
  * STYLE_GUIDE.md  -> document list, anchor registry, deprecated-term registry
                       (a project's "constitution", machine-readable tables).
  * Project_Profile.yaml -> enabled docs, data-driven boundary_checks /
                       consistency_checks / deprecated_terms / exceptions,
                       audit thresholds and paths.

The engine only executes rules; no project-specific fact is hard-coded here.
That is the difference from a per-project script: the same engine audits any
project by pointing --profile / --style at that project's files.

Usage:
  python global_doc_audit.py --root "<md dir>" --out "<audit dir>" \
      --profile "<Project_Profile.yaml>" --style "<STYLE_GUIDE.md>"
"""

import os, re, argparse, json, sys, glob, hashlib
from datetime import datetime
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None

SCRIPT_VERSION = "v2.0.0-generic"

# ─── rule registries loaded from STYLE_GUIDE.md ───
EXPECTED_DOCS = []
ANCHOR_LIST = {}
DEPRECATED_LIST = []          # list of (old_str, new_str, search_scope)
AUTH_DOCS = set()


ANCHOR_PREFIX = r'(FACT|TERM|RULE|PARAM|FLOW|RESOURCE|COLLECTIBLE|PROGRESSION|ECONOMY|MULTIPLAYER|LIVEOPS|UI|TECH)'


def _marker_block(clean, key):
    """Return the text between <!-- AUDIT: KEY_START --> and _END, or None.
    Language-independent; the primary parse path for generated STYLE files."""
    m = re.search(r'<!--\s*AUDIT:\s*' + re.escape(key) + r'_START\s*-->(.*?)'
                  r'<!--\s*AUDIT:\s*' + re.escape(key) + r'_END\s*-->', clean, re.DOTALL)
    return m.group(1) if m else None


def _parse_docs(lines):
    for line in lines:
        if line.strip().startswith("|") and ".md" in line:
            m = re.search(r'`?([A-Z][A-Za-z_]+\.md)`?', line)
            if m and m.group(1) not in EXPECTED_DOCS:
                EXPECTED_DOCS.append(m.group(1))


def _parse_anchors(lines):
    for line in lines:
        if line.strip().startswith("|"):
            cells = [c.strip().strip('`') for c in line.split("|")]
            if len(cells) >= 4 and '---' not in cells[1] and cells[1]:
                aid = cells[1]
                if re.match(r'^' + ANCHOR_PREFIX + r'-', aid):
                    ANCHOR_LIST[aid] = {"desc": cells[2] if len(cells) > 2 else "",
                                        "authority": cells[3] if len(cells) > 3 else ""}


def _parse_deprecated(lines):
    for line in lines:
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 5 and cells[1] and '---' not in cells[1] \
                    and '废弃说法' not in cells[1] and 'Deprecated' not in cells[1]:
                old = cells[1]; new = cells[2] if len(cells) > 2 else ""
                sr = cells[5] if len(cells) > 5 else "*"
                if old and not old.startswith('---'):
                    DEPRECATED_LIST.append((old, new, sr))


def load_style_rules(style_text):
    """Parse the machine-readable tables inside STYLE_GUIDE.md.

    Language-independent path first: <!-- AUDIT: X_START/END --> markers.
    Fallback path (no markers): the legacy title heuristic, so an existing
    project STYLE (e.g. Chinese headings, no markers) still parses unchanged."""
    global EXPECTED_DOCS, ANCHOR_LIST, DEPRECATED_LIST, AUTH_DOCS
    EXPECTED_DOCS = []; ANCHOR_LIST = {}; DEPRECATED_LIST = []

    clean = re.sub(r'```.*?```', '', style_text, flags=re.DOTALL)

    # ── file list ──
    block = _marker_block(clean, "ENABLED_DOCS")
    if block is not None:
        _parse_docs(block.split("\n"))
    else:
        in_21 = False
        for line in clean.split("\n"):
            if "### 2.1" in line or ("## 2." in line and "文件清单" in line):
                in_21 = True; continue
            if "### 2.2" in line or "### 2.3" in line:
                in_21 = False; continue
            if in_21 and line.strip().startswith("|") and ".md" in line:
                m = re.search(r'`?([A-Z][A-Za-z_]+\.md)`?', line)
                if m and m.group(1) not in EXPECTED_DOCS:
                    EXPECTED_DOCS.append(m.group(1))

    # ── anchor registry ──
    block = _marker_block(clean, "ANCHOR_REGISTRY")
    if block is not None:
        _parse_anchors(block.split("\n"))
    else:
        in_anchor = False
        for line in clean.split("\n"):
            if "已建立锚点清单" in line or "anchor registry" in line.lower():
                in_anchor = True; continue
            if in_anchor:
                if line.strip().startswith("|"):
                    cells = [c.strip().strip('`') for c in line.split("|")]
                    if len(cells) >= 4 and '---' not in cells[1] and cells[1]:
                        aid = cells[1]
                        if re.match(r'^' + ANCHOR_PREFIX + r'-', aid):
                            ANCHOR_LIST[aid] = {"desc": cells[2] if len(cells) > 2 else "",
                                                "authority": cells[3] if len(cells) > 3 else ""}
                elif not line.strip():
                    continue
                elif line.strip().startswith("###") or line.strip().startswith("####"):
                    in_anchor = False

    # ── deprecated-term registry ──
    block = _marker_block(clean, "DEPRECATED_TERMS")
    if block is not None:
        _parse_deprecated(block.split("\n"))
    else:
        in_dep = False
        for line in clean.split("\n"):
            if "废弃说法" in line and "当前正确说法" in line:
                in_dep = True; continue
            if in_dep:
                if line.strip().startswith("|"):
                    cells = [c.strip() for c in line.split("|")]
                    if len(cells) >= 5 and cells[1] and '---' not in cells[1] and '废弃说法' not in cells[1]:
                        old = cells[1]; new = cells[2] if len(cells) > 2 else ""
                        sr = cells[5] if len(cells) > 5 else "*"
                        if old and not old.startswith('---'):
                            DEPRECATED_LIST.append((old, new, sr))
                elif not line.strip():
                    continue
                elif line.strip().startswith("登记原则"):
                    in_dep = False

    AUTH_DOCS = set(EXPECTED_DOCS)


# ─── profile ───
def load_profile(path):
    if path is None:
        return {}
    if yaml is None:
        print("[WARN] PyYAML not installed; --profile ignored.", file=sys.stderr)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


# ─── issue tracker ───
class Issue:
    def __init__(self, p, file, msg, rule=None):
        self.p = p; self.file = file; self.msg = msg; self.rule = rule
        self.id = None

    def set_id(self):
        raw = f"{self.file}|{self.rule or ''}|{self.msg}"
        self.id = f"AUD-{self.p}-{hashlib.md5(raw.encode()).hexdigest()[:8]}"
        return self.id

    def as_dict(self):
        return {"issue_id": self.id, "status": "OPEN", "level": self.p,
                "file": self.file, "msg": self.msg, "rule": self.rule}


issues = []
def add(p, file, msg, rule=None):
    iss = Issue(p, file, msg, rule); iss.set_id(); issues.append(iss)


# ─── file helpers ───
def match_versioned_doc(filename, expected_name, version_pattern=r'\((\d+)\)'):
    """Does `filename` denote `expected_name`, either canonical or with the
    configured version suffix? Returns (ok, version). Strict: only base.md or
    base + <version_pattern> + .md match — so STYLE_GUIDE_TEMPLATE.md /
    STYLE_GUIDE_BACKUP.md / STYLE_GUIDE_OLD.md are rejected."""
    base, ext = os.path.splitext(expected_name)
    version_re = re.compile(r'^' + re.escape(base) + r'(?:' + version_pattern + r')?' + re.escape(ext) + r'$')
    if not version_re.match(filename):
        return False, None
    vm = re.search(version_pattern, filename)
    version = int(vm.group(1)) if vm and vm.group(1) and vm.group(1).isdigit() else 0
    return True, version


def find_latest(root, name, version_pattern=r'\((\d+)\)'):
    base, ext = os.path.splitext(name)
    candidates = []
    for path in glob.glob(os.path.join(root, f"{base}*{ext}")):
        ok, version = match_versioned_doc(os.path.basename(path), name, version_pattern)
        if ok:
            candidates.append((version, path))
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], candidates[0][0]


def doc_exists(root, name, version_pattern=r'\((\d+)\)'):
    path, _ = find_latest(root, name, version_pattern)
    return path is not None


def read_doc(root, name, version_pattern=r'\((\d+)\)'):
    path, _ = find_latest(root, name, version_pattern)
    if path is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_for_scan(text):
    return re.sub(r'```.*?```', '', text, flags=re.DOTALL)


def resolve_files(files, enabled_docs):
    if not files or files == ["*"]:
        return [d for d in enabled_docs if d != "STYLE_GUIDE.md"]
    return files


# ─── generic checks (engine) ───
def check_file_list(root, enabled_docs, non_authority, version_pattern=r'\((\d+)\)'):
    for name in enabled_docs:
        if not doc_exists(root, name, version_pattern):
            add("P0", name, "Missing expected authority doc")
    for n in non_authority:
        if os.path.exists(os.path.join(root, n)):
            add("INFO", n, "Non-authority file in document directory")


def check_tables(doc_name, text):
    clean = clean_for_scan(text); lines = clean.split("\n"); col = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            actual = len(s[1:-1].split("|"))
            if "---" in s:
                col = actual
            elif col and actual != col:
                add("P2", doc_name, f"L{i+1}: table row has {actual} cols, expected {col}")
        else:
            col = None
        if s.startswith("<!--") and s.endswith("-->") and 0 < i < len(lines) - 1:
            prev, nxt = lines[i-1].strip(), lines[i+1].strip()
            if prev.startswith("|") and prev.endswith("|") and nxt.startswith("|") and nxt.endswith("|"):
                add("P2", doc_name, f"L{i+1}: HTML comment between table rows")


def check_anchors(all_texts):
    if not ANCHOR_LIST:
        return
    am = defaultdict(list)
    for doc_name, text in all_texts:
        c = clean_for_scan(text)
        for m in re.finditer(r"<!--\s*(" + ANCHOR_PREFIX + r"-[\w-]+)\s*-->", c):
            if m.group(1) in ANCHOR_LIST:
                am[m.group(1)].append("auth")
        for m in re.finditer(r"<!--\s*REF:\s*(" + ANCHOR_PREFIX + r"-[\w-]+)\s*-->", c):
            if m.group(1) in ANCHOR_LIST:
                am[m.group(1)].append("ref")
    for aid in ANCHOR_LIST:
        entries = am.get(aid, [])
        if not entries:
            add("P1", aid, "Registered anchor has zero occurrences")
        else:
            if "auth" not in entries:
                add("P1", aid, "No authority occurrence")
            if aid.startswith("FACT-") and "ref" not in entries:
                add("P2", aid, "FACT anchor has no REF")
            elif aid.startswith("RULE-") and "ref" not in entries:
                add("P3", aid, "RULE anchor has no REF")


def check_deprecated(all_texts, profile_terms):
    combined = list(DEPRECATED_LIST)
    for t in profile_terms:
        olds = t.get("old", [])
        olds = olds if isinstance(olds, list) else [olds]
        combined.append(("/".join(olds), t.get("current", ""), "/".join(t.get("search_scope", ["*"]))))
    for old_entry, new_entry, sr in combined:
        for kw in [k.strip() for k in old_entry.split("/") if len(k.strip()) > 1]:
            for doc_name, text in all_texts:
                if doc_name == "STYLE_GUIDE.md":
                    continue
                if sr not in ("*", "全部正式权威文档") and doc_name not in sr:
                    continue
                c = clean_for_scan(text)
                if kw not in c:
                    continue
                for m in re.finditer(re.escape(kw), c):
                    ctx = c[max(0, m.start()-30):m.end()+30]
                    if re.search(r'不是|并非|禁止|非|deprecated|旧称|误称', ctx):
                        continue
                    sev = "P1" if len(kw) > 5 else "P2"
                    add(sev, doc_name, f"Deprecated term '{kw}' (-> {new_entry})")
                    break


def check_links(all_texts, root_dir, ignored_dirs=None, version_pattern=r'\((\d+)\)'):
    ignored_dirs = ignored_dirs or []
    for doc_name, text in all_texts:
        if doc_name == "STYLE_GUIDE.md":
            continue
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', clean_for_scan(text)):
            base = m.group(2).split('#')[0]           # strip #fragment first
            if not base.endswith('.md'):
                continue
            if any(seg in ignored_dirs for seg in base.split('/')[:-1]):
                continue
            tf = base.split('/')[-1]
            if tf != doc_name and not doc_exists(root_dir, tf, version_pattern):
                add("P1", doc_name, f"Broken link: [{m.group(1)}]({m.group(2)})")


# ─── data-driven checks (from profile) ───
def run_boundary_checks(texts, checks, enabled_docs):
    for chk in checks:
        level = chk.get("level", "P2")
        msg = chk.get("message", f"boundary check {chk.get('id','')}")
        window = int(chk.get("near_window", 200))
        near = chk.get("unless_near", []) or []
        stop = chk.get("stop_at")
        mode = chk.get("match", "all")   # "all" | "first_per_term"
        patterns = ([chk["forbid_regex"]] if chk.get("forbid_regex") else []) + \
                   [re.escape(w) for w in (chk.get("forbid_any") or [])]
        for doc_name in resolve_files(chk.get("files"), enabled_docs):
            text = texts.get(doc_name)
            if not text:
                continue
            c = clean_for_scan(text)
            if stop:
                c = c.split(stop)[0]
            reported = False
            for pat in patterns:
                if mode == "first_per_term":
                    m = re.search(pat, c)
                    ms = [m] if m else []
                else:
                    ms = list(re.finditer(pat, c))
                for m in ms:
                    win = c[max(0, m.start()-window):m.end()+window]
                    if near and any(n in win for n in near):
                        continue
                    add(level, doc_name, msg, rule=chk.get("id"))
                    reported = True
                    break
                if reported and mode != "first_per_term":
                    break


def run_consistency_checks(texts, checks, enabled_docs):
    for chk in checks:
        term = chk.get("term")
        if not term:
            continue
        level = chk.get("level", "P1")
        msg = chk.get("message", f"consistency check {chk.get('id','')}")
        window = int(chk.get("near_window", 40))
        neg = chk.get("require_negation_near", []) or []
        need_all = chk.get("require_all_context_near", []) or []
        for doc_name in resolve_files(chk.get("files"), enabled_docs):
            text = texts.get(doc_name)
            if not text:
                continue
            c = clean_for_scan(text)
            for m in re.finditer(re.escape(term), c):
                win = c[max(0, m.start()-window):m.end()+window]
                if neg and any(n in win for n in neg):
                    continue
                if need_all and not all(x in win for x in need_all):
                    continue
                add(level, doc_name, msg, rule=chk.get("id"))
                break


def apply_exceptions(exceptions):
    if not exceptions:
        return
    keep = []
    ex_ids = {e.get("id") for e in exceptions if e.get("id")}
    ex_files = {(e.get("file"), e.get("id")) for e in exceptions}
    for iss in issues:
        if iss.rule and iss.rule in ex_ids:
            continue
        if (iss.file, iss.rule) in ex_files:
            continue
        keep.append(iss)
    issues[:] = keep


# ─── issue state (jsonl) ───
STATE_FILE = "issue_state.jsonl"
HUMAN_STATES = ("FALSE_POSITIVE", "ACCEPTED_EXCEPTION")


def load_issue_state(out_dir):
    path = os.path.join(out_dir, STATE_FILE)
    state = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("issue_id"):
                        state[e["issue_id"]] = e
                except Exception:
                    pass
    return state


def suppress_by_state(state):
    """Move human-marked (false-positive / accepted-exception) issues out of the
    active list so they do not re-alarm. Returns the suppressed [(issue, status)]."""
    if not state:
        return []
    active, suppressed = [], []
    for i in issues:
        st = state.get(i.id, {}).get("status")
        if st in HUMAN_STATES:
            suppressed.append((i, st))
        else:
            active.append(i)
    issues[:] = active
    return suppressed


def write_issue_state(out_dir, active_issues, suppressed, prev, when):
    new = {}
    for i, st in suppressed:
        pe = prev.get(i.id, {})
        new[i.id] = {"issue_id": i.id, "status": st, "level": i.p, "file": i.file,
                     "msg": i.msg, "reason": pe.get("reason", ""),
                     "updated_at": pe.get("updated_at", when)}
    for i in active_issues:
        pe = prev.get(i.id)
        if pe:
            ps = pe.get("status")
            ns = "REOPENED" if ps == "VERIFIED" else (ps or "OPEN")
        else:
            ns = "OPEN"
        new[i.id] = {"issue_id": i.id, "status": ns, "level": i.p, "file": i.file,
                     "msg": i.msg, "reason": pe.get("reason", "") if pe else "",
                     "updated_at": when}
    for pid, pe in prev.items():
        if pid in new:
            continue
        ps = pe.get("status")
        if ps in HUMAN_STATES or ps == "VERIFIED":
            new[pid] = pe
        else:
            e = dict(pe); e["status"] = "VERIFIED"; e["updated_at"] = when
            new[pid] = e
    with open(os.path.join(out_dir, STATE_FILE), "w", encoding="utf-8") as f:
        for e in new.values():
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


# ─── main ───
def run_audit(root_dir, out_dir, profile_path, style_path,
              strict=False, pedantic=False, write_history=True,
              json_only=False, md_only=False, baseline_path=None,
              write_state=True, lang="en", engine_version=1):
    global issues
    issues = []
    now = datetime.now()
    audit_time = now.strftime("%Y-%m-%d %H:%M")
    audit_id = f"AUDIT-{now.strftime('%Y%m%d-%H%M')}"

    profile = load_profile(profile_path)

    # ─── v2 engine: pre-validate config ───────────────────
    if engine_version >= 2:
        try:
            from game_design_doc_governance.engine import validate_profile, WaiverManager
        except ImportError:
            print("Warning: engine module not importable; falling back to v1 validation")
        else:
            config_issues = validate_profile(profile, strict=True)
            if config_issues:
                for ci in config_issues:
                    add(ci.level, ci.rule, ci.message)
                if any(ci.level in ("P0", "P1") for ci in config_issues):
                    return False

            # v2 waiver manager: enforce (rule, file) binding + expires
            wm = WaiverManager()
            wm.load_from_profile(profile.get("exceptions", []))
            # Store for later use after issues are collected
            _v2_waiver_manager = wm
    if not style_path:
        # try profile paths or default
        style_path, _ = find_latest(root_dir, "STYLE_GUIDE.md")
    if style_path and os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            load_style_rules(f.read())
        style_file = os.path.basename(style_path)
    else:
        add("P0", "STYLE_GUIDE.md", "Cannot load STYLE_GUIDE")
        style_file = "STYLE_GUIDE.md"

    enabled_docs = profile.get("enabled_docs") or EXPECTED_DOCS
    non_authority = profile.get("non_authority_files",
                                ["Design_Document.docx", "prompts.md", "人工笔记.txt"])
    audit_cfg = profile.get("audit", {})
    ver_pat = (profile.get("file_versioning", {}) or {}).get("version_pattern", r'\((\d+)\)')

    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(root_dir), "audit")
    os.makedirs(out_dir, exist_ok=True)

    check_file_list(root_dir, enabled_docs, non_authority, version_pattern=ver_pat)

    texts = {}
    all_texts = []
    for name in enabled_docs:
        t = read_doc(root_dir, name, version_pattern=ver_pat)
        if t:
            texts[name] = t
            all_texts.append((name, t))

    for doc_name, text in all_texts:
        check_tables(doc_name, text)

    check_anchors(all_texts)
    check_deprecated(all_texts, profile.get("deprecated_terms", []))
    lc = profile.get("link_checks", {}) or {}
    if lc.get("enabled", True):
        check_links(all_texts, root_dir, ignored_dirs=lc.get("ignored_dirs"), version_pattern=ver_pat)
    run_boundary_checks(texts, profile.get("boundary_checks", []), enabled_docs)
    run_consistency_checks(texts, profile.get("consistency_checks", []), enabled_docs)
    apply_exceptions(profile.get("exceptions", []))

    prev_state = load_issue_state(out_dir) if write_state else {}
    suppressed = suppress_by_state(prev_state)

    buckets = {p: [i for i in issues if i.p == p] for p in ("P0", "P1", "P2", "P3", "INFO")}
    counts = {p: len(v) for p, v in buckets.items()}

    profile_name = os.path.basename(profile_path) if profile_path else "(none)"
    rl = ["# Global Documentation Audit Report", "",
          f"- **Audit ID**: {audit_id}",
          f"- **Time**: {audit_time}",
          f"- **Script**: {SCRIPT_VERSION}",
          f"- **STYLE file**: {style_file}",
          f"- **Profile file**: {profile_name}",
          f"- **Root dir**: {root_dir}",
          f"- **Output dir**: {out_dir}",
          f"- **Docs scanned**: {len(all_texts)}",
          f"- **Loaded rules**: anchors {len(ANCHOR_LIST)} / deprecated {len(DEPRECATED_LIST)} / "
          f"docs {len(enabled_docs)} / boundary {len(profile.get('boundary_checks', []))} / "
          f"consistency {len(profile.get('consistency_checks', []))}", "",
          "## Summary", "", "| Level | Count |", "|-------|-------|"]
    for p in ("P0", "P1", "P2", "P3", "INFO"):
        rl.append(f"| {p} | {counts[p]} |")
    if suppressed:
        rl.append(f"\n_Suppressed (false-positive / accepted-exception): {len(suppressed)}_")
    for p in ("P0", "P1", "P2", "P3", "INFO"):
        if buckets[p]:
            rl.append(f"\n## {p}")
            for it in buckets[p]:
                rl.append(f"- [{it.id}] **{it.file}**: {it.msg}")
    passed = not ((audit_cfg.get("fail_on_p0", True) and counts["P0"] > 0) or
                  (audit_cfg.get("fail_on_p1", True) and counts["P1"] > 0))
    if (strict or pedantic) and audit_cfg.get("fail_on_p2_in_strict_mode", True):
        passed = passed and counts["P2"] == 0
    rl.append("\n## Verdict")
    rl.append(f"- Result: **{'PASS' if passed else 'FAIL'}** "
              f"(P0={counts['P0']} P1={counts['P1']} P2={counts['P2']} P3={counts['P3']})")
    report_text = "\n".join(rl)
    print(report_text)

    if not json_only:
        with open(os.path.join(out_dir, "audit_report.md"), "w", encoding="utf-8") as f:
            f.write(report_text)
    if not md_only:
        jdata = {"audit_id": audit_id, "time": audit_time, "script_version": SCRIPT_VERSION,
                 "style_file": style_file, "profile_file": profile_name,
                 "root_dir": root_dir, "out_dir": out_dir,
                 "p0": counts["P0"], "p1": counts["P1"], "p2": counts["P2"],
                 "p3": counts["P3"], "info": counts["INFO"],
                 "suppressed": len(suppressed),
                 "issues": [i.as_dict() for i in issues],
                 "loaded_rules": {"docs": len(enabled_docs), "anchors": len(ANCHOR_LIST),
                                  "deprecated": len(DEPRECATED_LIST),
                                  "boundary_checks": len(profile.get("boundary_checks", [])),
                                  "consistency_checks": len(profile.get("consistency_checks", []))}}
        with open(os.path.join(out_dir, "audit_report.json"), "w", encoding="utf-8") as f:
            json.dump(jdata, f, ensure_ascii=False, indent=2)

    if write_history and not json_only:
        hist = os.path.join(out_dir, "audit_history.md")
        new = not os.path.exists(hist)
        with open(hist, "a", encoding="utf-8") as f:
            if new:
                f.write("# Audit History\n\n")
            f.write(f"## {audit_id} — {audit_time}\n\n")
            f.write(f"**Script**: {SCRIPT_VERSION} | **STYLE**: {style_file} | "
                    f"**Profile**: {profile_name} | **Root**: {root_dir}\n\n")
            f.write("| Level | Count |\n|-------|-------|\n")
            for p in ("P0", "P1", "P2", "P3", "INFO"):
                f.write(f"| {p} | {counts[p]} |\n")
            f.write("\n")
            for it in issues:
                f.write(f"- [{it.id}] **{it.p}** {it.file}: {it.msg}\n")
            if not issues:
                f.write("No issues.\n")
            f.write("\n---\n\n")

    if write_state:
        write_issue_state(out_dir, issues, suppressed, prev_state, audit_time)

    print(f"\nReport: {os.path.join(out_dir, 'audit_report.md')} | "
          f"History: {os.path.join(out_dir, 'audit_history.md')}")

    if baseline_path and os.path.exists(baseline_path):
        with open(baseline_path, "r", encoding="utf-8") as f:
            base = json.load(f)
        keys = ["p0", "p1", "p2", "p3"]   # INFO is informational; not a regression gate
        cur = {"p0": counts["P0"], "p1": counts["P1"], "p2": counts["P2"],
               "p3": counts["P3"], "info": counts["INFO"]}
        eq = all(base.get(k) == cur.get(k) for k in keys)
        print(f"Baseline compare: {'EQUIVALENT' if eq else 'DIVERGED'} "
              f"(baseline {[base.get(k) for k in keys]} vs current {[cur.get(k) for k in keys]})")
        if not eq:
            passed = False

    return passed


def main():
    ap = argparse.ArgumentParser(description="Generic game-design documentation auditor")
    ap.add_argument("--root", required=True, help="Directory of source .md docs")
    ap.add_argument("--out", default=None, help="Output directory for reports")
    ap.add_argument("--profile", default=None, help="Project_Profile.yaml")
    ap.add_argument("--style", default=None, help="STYLE_GUIDE.md (default: found under --root)")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--fail-on-p2", action="store_true")
    ap.add_argument("--pedantic", action="store_true")
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--md-only", action="store_true")
    ap.add_argument("--no-history", action="store_true")
    ap.add_argument("--no-state", action="store_true", help="Do not read/write issue_state.jsonl")
    ap.add_argument("--baseline", default=None, help="Baseline JSON to compare counts against")
    ap.add_argument("--engine", type=int, default=2, choices=[1, 2],
                    help="Engine version: 1=legacy, 2=v2 (default)")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"Error: root dir not found: {args.root}"); sys.exit(1)

    passed = run_audit(args.root, args.out, args.profile, args.style,
                       strict=args.strict, pedantic=args.pedantic or args.fail_on_p2,
                       write_history=not args.no_history,
                       json_only=args.json_only, md_only=args.md_only,
                       baseline_path=args.baseline, write_state=not args.no_state,
                       engine_version=args.engine)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

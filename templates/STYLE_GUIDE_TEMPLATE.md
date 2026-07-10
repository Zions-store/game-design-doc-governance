<!-- Copyright (C) 2026 ZionXiaoxiSuOGLocGo -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# {{PROJECT_NAME}} - Documentation Style Guide

> The document-system **constitution**. It defines which documents exist, who owns
> what, how cross-document change is kept safe, and how the audit runs. Update this
> before changing any document's responsibility.
>
> This is a template. Replace every `{{PLACEHOLDER}}` from the Project Profile. When
> generating in a non-English language, translate headings/labels but keep the
> `{{PLACEHOLDER}}` markers, anchor IDs and machine-readable table shapes intact.

## 1. Documentation System Principles

Single authority; content ownership beats appearance; summaries may repeat, bodies
may not; full-volume first (light content OK, light structure not).

## 2. Authoritative File List

<!-- AUDIT: ENABLED_DOCS_START -->
{{ENABLED_DOCS_TABLE}}
<!-- AUDIT: ENABLED_DOCS_END -->
<!-- one row per enabled doc: | File | Role | Status | -->

## 3. Non-Authority Auxiliary Files

{{NON_AUTHORITY_FILES}}
<!-- snapshots (.docx/.pdf), prompt logs, scratch notes - not design sources -->

## 4. Content Authority Matrix

{{AUTHORITY_MATRIX}}
<!-- | Content type | Authority doc | May reference | Must NOT store | -->

## 5. Cross-Document Boundary Rules

{{BOUNDARY_RULES}}
<!-- one rule per high-risk boundary from the Profile -->

## 6. Cross-Document Change-Safety Mechanism

Five layers: authority matrix (§4) · change-type classification · anchors ·
deprecated registry · change checklist.

### 6.1 Anchor rules

Authority uses the raw anchor `<!-- ANCHOR-ID -->`; references use
`<!-- REF: ANCHOR-ID -->`. High-risk recurring facts must be anchored.
Prefixes: FACT/TERM/RULE/PARAM/FLOW/RESOURCE/COLLECTIBLE/PROGRESSION/ECONOMY/
MULTIPLAYER/LIVEOPS/UI/TECH.

### 6.2 Anchor registry

<!-- AUDIT: ANCHOR_REGISTRY_START -->
{{ANCHOR_REGISTRY}}
<!-- AUDIT: ANCHOR_REGISTRY_END -->
<!-- | Anchor ID | Setting | Authority doc | Referencing docs | -->

### 6.3 Deprecated-term registry

<!-- AUDIT: DEPRECATED_TERMS_START -->
{{DEPRECATED_TERMS_TABLE}}
<!-- AUDIT: DEPRECATED_TERMS_END -->
<!-- | Deprecated | Correct now | Type | Keyword | Search scope | -->

### 6.4 Change checklist

Classify change → find authority → list impacted docs → search old wording →
search anchor ID → run audit; drive P0/P1 to zero.

## 7. Full-Volume Document Rule

Authority docs are built to final shape; unfinished sections use `🔲 TODO`. No
`misc/other/global` catch-all buckets. Headers state final responsibility.

## 8. Numbering & Hierarchy

`##`/`###`/`####` use consistent numeric prefixes. {{NUMBERING_EXCEPTIONS}}

## 9. Splitting & New-Document Rules

Answer the five questions (see governance module 01) before adding a document.
Registered "do-not-create" list: {{DO_NOT_CREATE_LIST}}

## 10. Cross-Reference Rules

All references point to the authority doc; moved content updates its old references;
non-authority records are never cited as a design source.

## 11. Non-Authority Document Rules

Snapshots/logs are read-only renders; never edited as source; not referenced as authority.

## 12. Review Checklist

One authority per content type? No duplicated bodies? No catch-all buckets? No
temporary structure posing as permanent? No broken/mis-authority links? No numbers
in character docs? No event bodies in world docs? No world truth in script? No
resources in collectibles?

## 13. Scripted Audit Spec

Audit is run by `game-design-doc-governance/tools/global_doc_audit.py`, using this
STYLE and the Project Profile as rule sources. Reports: `audit/audit_report.md` +
`audit/audit_report.json`; history appended to `audit/audit_history.md`; per-issue
states tracked in `audit/issue_state.jsonl`. The audit parses the
`<!-- AUDIT: *_START/END -->` marker blocks in §2/§6 (language-independent), so this
STYLE audits correctly in any generated language. The script is a tool, not the
design authority.

## 14. Audit Records & Issue States

Levels P0/P1/P2/P3/INFO. Issue IDs are stable (`AUD-{LEVEL}-{hash}`). States:
OPEN / FIXED_PENDING_VERIFY / VERIFIED / FALSE_POSITIVE / ACCEPTED_EXCEPTION / REOPENED.

- `audit/issue_state.jsonl` - per-issue state ledger. Issues marked
  FALSE_POSITIVE / ACCEPTED_EXCEPTION are suppressed from the counts on later runs.

## 15. Legacy-Issue Handling

Resolved scratch/legacy items migrate into an authority doc or this STYLE and are
marked migrated; deprecated wording is registered in §6.3.

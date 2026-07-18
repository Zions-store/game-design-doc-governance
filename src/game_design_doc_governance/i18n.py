# Copyright (C) 2026 ZionXiaoxiSuOGLocGo
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Any-language document generation with structure protection.

Core abstractions:
  - LanguageProvider: abstract base for a model/translator that generates
    documents in a target language.
  - FakeProvider: offline implementation for CI/testing (no network required).
  - GenerationMetadata: tracks what was generated, by whom, and validation result.
  - validate_structure(): post-generation structure integrity check.

Design invariant:
  Any-language generation is performed by an LLM/Agent. The static CLI
  without a configured Provider MUST degrade clearly, never claiming
  to have completed translation when none was performed.

Structure protection:
  The following MUST remain intact after generation:
    - {{PLACEHOLDER}} markers
    - YAML keys and values (keys never translated)
    - Anchor IDs (<!-- FACT-... -->, <!-- RULE-... -->, etc.)
    - REF references (<!-- REF: ... -->)
    - Document IDs and rule IDs
    - Link targets ([...](./doc.md))
"""

import re
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Optional


@dataclass
class GenerationMetadata:
    """Tracks the provenance and validation status of a generated document."""
    target_language: str
    provider_type: str
    model_identifier: str = ""
    prompt_version: str = ""
    profile_id: str = ""
    structure_valid: bool = False
    structure_issues: list = field(default_factory=list)
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


# ─── Provider abstraction ──────────────────────────────────────

class LanguageProvider(ABC):
    """Abstract provider for generating documents in a target language.

    Implementations MUST NOT store API keys in the repository.
    Implementations MUST NOT upload project content without authorization.
    """

    def __init__(self, provider_type: str, model: str = ""):
        self.provider_type = provider_type
        self.model = model

    @abstractmethod
    def generate(self, source_text: str, target_language: str,
                 template_context: dict = None) -> tuple[str, GenerationMetadata]:
        """Translate/generate source text into target_language.

        Args:
            source_text: The original text to translate.
            target_language: BCP 47 language tag (e.g. 'ja', 'fr-CA', 'ar').
            template_context: Optional dict of template variables.

        Returns:
            (translated_text, metadata) — metadata includes validation status.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider can generate output now."""
        ...


class FakeProvider(LanguageProvider):
    """Offline provider for CI/testing. Produces tagged output without a model.

    Does NOT claim to have translated content — it wraps the source text
    with language markers so structure validation can run in CI without
    network access.
    """

    def __init__(self):
        super().__init__(provider_type="fake", model="offline")

    def generate(self, source_text: str, target_language: str,
                 template_context: dict = None) -> tuple[str, GenerationMetadata]:
        """Return source text with language markers. NOT a real translation."""
        meta = GenerationMetadata(
            target_language=target_language,
            provider_type="fake",
            model_identifier="offline",
            prompt_version="v1",
            structure_valid=False  # will be set by caller
        )
        # Wrap with language marker — structure tests can verify placeholders survive
        wrapped = (
            f"<!-- generated:lang={target_language} provider=fake -->\n"
            f"{source_text}\n"
            f"<!-- /generated -->"
        )
        return wrapped, meta

    def is_available(self) -> bool:
        return True


# ─── Structure protection ───────────────────────────────────────

# Patterns that MUST survive generation unchanged
PROTECTED_PATTERNS = [
    # Placeholders
    (r'\{\{[A-Z_]+\}\}', 'PLACEHOLDER'),
    (r'\{\{[a-z_]+\}\}', 'PLACEHOLDER_VAR'),
    # YAML keys — any key at start of line followed by :
    (r'^[a-z_]+:', 'YAML_KEY', re.MULTILINE),
    # Anchor IDs
    (r'<!--\s*(FACT|TERM|RULE|PARAM|FLOW|RESOURCE)\s*[-:]\s*\w+', 'ANCHOR_ID'),
    # REF references
    (r'<!--\s*REF\s*:\s*\w+', 'REF_MARKER'),
    # Document links
    (r'\[([^\]]+)\]\(([^)]+\.md)\)', 'DOC_LINK'),
    # Rule IDs
    (r'[A-Z]+-[A-Z]+-\w+-\w+', 'RULE_ID'),
]


def validate_structure(source_text: str, generated_text: str) -> list[str]:
    """Check that critical structure elements survived generation.

    Args:
        source_text: Original source text before generation.
        generated_text: Text after generation/translation.

    Returns:
        List of issue descriptions (empty = structure intact).
    """
    issues = []

    for pattern, label in [
        (r'\{\{[A-Z_]+\}\}', 'PLACEHOLDER'),
        (r'\{\{[a-z_]+\}\}', 'PLACEHOLDER_VAR'),
        (r'<!--\s*(FACT|TERM|RULE|PARAM|FLOW|RESOURCE|COLLECTIBLE|PROGRESSION|ECONOMY|'
         r'MULTIPLAYER|LIVEOPS|UI|TECH)\s*[-:]\s*\w+', 'ANCHOR_ID'),
        (r'<!--\s*REF\s*:\s*\w+', 'REF_MARKER'),
    ]:
        source_matches = set(re.findall(pattern, source_text))
        gen_matches = set(re.findall(pattern, generated_text))
        missing = source_matches - gen_matches
        if missing:
            issues.append(f"{label}: {len(missing)} missing after generation: {sorted(missing)[:5]}")

    # Check YAML keys survived
    source_yaml_keys = set(re.findall(r'^([a-z_]+):', source_text, re.MULTILINE))
    gen_yaml_keys = set(re.findall(r'^([a-z_]+):', generated_text, re.MULTILINE))
    missing_keys = source_yaml_keys - gen_yaml_keys
    if missing_keys:
        issues.append(f"YAML_KEY: {len(missing_keys)} missing: {sorted(missing_keys)[:10]}")

    # Check document links
    source_links = set(re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', source_text))
    gen_links = set(re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', generated_text))
    if len(gen_links) < len(source_links):
        issues.append(f"DOC_LINK: {len(source_links) - len(gen_links)} links missing")

    return issues


# ─── Scaffold helpers ────────────────────────────────────────────

SUPPORTED_LANGUAGES = {
    "en-US", "zh-CN", "ja", "ko", "fr", "fr-CA", "de", "es", "pt-BR",
    "ar", "ru", "it", "nl", "pl", "tr", "th", "vi", "id", "ms", "hi",
}


def normalize_language(lang: str) -> str:
    """Normalize a language tag to a supported BCP 47 tag.

    If the requested language is not in the known set, it is still returned
    as-is — the provider may still handle it. Unknown languages should NOT
    be rejected; the provider is responsible for reporting unsupported languages.
    """
    lang = lang.strip().replace("_", "-")
    if lang in SUPPORTED_LANGUAGES:
        return lang
    # Try prefix match (e.g. "fr" matches "fr")
    prefix = lang.split("-")[0]
    for supported in SUPPORTED_LANGUAGES:
        if supported.startswith(prefix):
            return supported
    return lang  # Return as-is; provider handles unsupported


def get_scaffold_language_label(lang: str) -> str:
    """Return a human-readable label for a language tag in scaffold output."""
    labels = {
        "en-US": "English (US)", "zh-CN": "简体中文", "ja": "日本語",
        "ko": "한국어", "fr": "Français", "de": "Deutsch", "es": "Español",
        "pt-BR": "Português (Brasil)", "ar": "العربية", "ru": "Русский",
        "it": "Italiano", "nl": "Nederlands", "pl": "Polski",
        "tr": "Türkçe", "th": "ไทย", "vi": "Tiếng Việt",
        "id": "Bahasa Indonesia", "ms": "Bahasa Melayu", "hi": "हिन्दी",
    }
    return labels.get(lang, lang)

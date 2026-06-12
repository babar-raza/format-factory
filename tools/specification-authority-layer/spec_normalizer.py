"""
spec_normalizer.py — Normalize parsed spec content to canonical form.

Normalization:
  - Strip excess whitespace from headings and content
  - Lowercase headings for index matching
  - Remove control characters
  - Deduplicate consecutive blank lines
  - Store normalized artifact in .local/spec-artifacts/
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .spec_parser import ParsedSpec, SpecSection
except ImportError:
    from spec_parser import ParsedSpec


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_text(text: str) -> str:
    """Remove control characters, normalize whitespace."""
    text = "".join(c for c in text if unicodedata.category(c)[0] != 'C' or c in '\n\t')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@dataclass
class NormalizedSpec:
    source_id: str
    sha256: str
    format_id: str
    sections_normalized: int = 0
    canonical_headings: List[str] = field(default_factory=list)
    artifact_path: Optional[str] = None
    normalized_at: str = field(default_factory=_now_iso)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "sha256": self.sha256,
            "format_id": self.format_id,
            "sections_normalized": self.sections_normalized,
            "canonical_headings": self.canonical_headings,
            "artifact_path": self.artifact_path,
            "normalized_at": self.normalized_at,
            "warnings": self.warnings,
        }


def normalize_spec(
    parsed: ParsedSpec,
    artifacts_dir: Optional[str] = None,
) -> NormalizedSpec:
    """
    Normalize all sections of a ParsedSpec.
    Stores normalized artifact as JSON in .local/spec-artifacts/.
    """
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_root.mkdir(parents=True, exist_ok=True)

    normalized_sections = []
    headings = []

    for section in parsed.sections:
        norm_heading = _normalize_text(section.heading)
        norm_content = _normalize_text(section.content)
        normalized_sections.append({
            "section_id": section.section_id,
            "heading": norm_heading,
            "heading_lower": norm_heading.lower(),
            "level": section.level,
            "content": norm_content,
            "line_start": section.line_start,
            "line_end": section.line_end,
            "parent_section_id": section.parent_section_id,
        })
        headings.append(norm_heading.lower())

    artifact = {
        "source_id": parsed.source_id,
        "sha256": parsed.sha256,
        "format_id": parsed.format_id,
        "parse_method": parsed.parse_method,
        "total_lines": parsed.total_lines,
        "sections": normalized_sections,
        "normalized_at": _now_iso(),
    }

    art_path = art_root / f"{parsed.source_id}-normalized.json"
    with open(art_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    return NormalizedSpec(
        source_id=parsed.source_id,
        sha256=parsed.sha256,
        format_id=parsed.format_id,
        sections_normalized=len(normalized_sections),
        canonical_headings=headings,
        artifact_path=str(art_path),
    )


def load_normalized_artifact(source_id: str, artifacts_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load a previously normalized artifact."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_path = art_root / f"{source_id}-normalized.json"
    if not art_path.exists():
        return None
    with open(art_path, "r", encoding="utf-8") as f:
        return json.load(f)

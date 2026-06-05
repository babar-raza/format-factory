"""
requirement_extractor.py — Extract candidate requirements from parsed spec sections.

A "candidate requirement" is a statement in a specification that implies a product
capability obligation (MUST, SHALL, SHOULD, MAY, supports, requires, etc.).

Output: list of CandidateRequirement records, stored in .local/spec-artifacts/
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# RFC 2119 / ODF spec keywords
_REQUIREMENT_PATTERNS = [
    r'\bMUST\b',
    r'\bSHALL\b',
    r'\bSHOULD\b',
    r'\bMAY\b',
    r'\bREQUIRED\b',
    r'\bOPTIONAL\b',
    r'\bsupports?\b',
    r'\brequires?\b',
    r'\bmust\b',
    r'\bshall\b',
    r'\bshould\b',
]

_COMPILED_PATTERNS = [re.compile(p) for p in _REQUIREMENT_PATTERNS]


def _contains_requirement_keyword(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED_PATTERNS)


@dataclass
class CandidateRequirement:
    req_id: str
    source_id: str
    section_id: str
    heading: str
    text_fragment: str
    keyword: str
    format_id: str
    status: str = "candidate"  # candidate | verified | rejected
    extracted_at: str = field(default_factory=_now_iso)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "req_id": self.req_id,
            "source_id": self.source_id,
            "section_id": self.section_id,
            "heading": self.heading,
            "text_fragment": self.text_fragment,
            "keyword": self.keyword,
            "format_id": self.format_id,
            "status": self.status,
            "extracted_at": self.extracted_at,
            "extra": self.extra,
        }


def extract_requirements(
    source_id: str,
    format_id: str,
    normalized_artifact: Dict[str, Any],
    artifacts_dir: Optional[str] = None,
) -> List[CandidateRequirement]:
    """
    Extract candidate requirements from a normalized artifact.
    Returns list of CandidateRequirement, stores result in artifacts_dir.
    """
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_root.mkdir(parents=True, exist_ok=True)

    sections = normalized_artifact.get("sections", [])
    requirements: List[CandidateRequirement] = []

    for sec in sections:
        content = sec.get("content", "")
        heading = sec.get("heading", "")
        section_id = sec.get("section_id", "")

        # Extract sentences containing requirement keywords
        sentences = re.split(r'(?<=[.!?])\s+', content)
        for sentence in sentences:
            for pattern in _COMPILED_PATTERNS:
                m = pattern.search(sentence)
                if m:
                    req = CandidateRequirement(
                        req_id=f"REQ-{source_id[:8]}-{uuid.uuid4().hex[:8]}",
                        source_id=source_id,
                        section_id=section_id,
                        heading=heading,
                        text_fragment=sentence[:300].strip(),
                        keyword=m.group(0),
                        format_id=format_id,
                    )
                    requirements.append(req)
                    break  # one req per sentence

    # Store
    out = {
        "source_id": source_id,
        "format_id": format_id,
        "requirements_count": len(requirements),
        "requirements": [r.to_dict() for r in requirements],
        "extracted_at": _now_iso(),
    }
    out_path = art_root / f"{source_id}-requirements.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    return requirements


def load_requirements(source_id: str, artifacts_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load previously extracted requirements for a source."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    out_path = art_root / f"{source_id}-requirements.json"
    if not out_path.exists():
        return []
    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("requirements", [])

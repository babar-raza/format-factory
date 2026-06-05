"""
spec_indexer.py — Build a searchable term/section index from a normalized spec.

Index format (stored as JSON):
  - terms: {term -> [section_id, ...]}
  - sections_by_id: {section_id -> {heading, level, ...}}
  - format_id, source_id, sha256, indexed_at

Storage: .local/spec-artifacts/{source_id}-index.json
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Common English stop-words to exclude from index
_STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "in", "of", "to", "for", "is", "are",
    "be", "by", "on", "with", "as", "at", "from", "that", "this", "which",
    "it", "not", "but", "if", "so", "can", "may", "must", "shall", "should",
    "will", "have", "has", "had", "do", "does", "did", "been", "was", "were",
    "all", "any", "each", "its", "no", "up", "out", "when", "than", "then",
}


def _tokenize(text: str) -> List[str]:
    """Split text into lowercase tokens, filtered for relevance."""
    tokens = re.findall(r'[a-zA-Z0-9_\-]{2,}', text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) >= 2]


@dataclass
class SpecIndex:
    source_id: str
    sha256: str
    format_id: str
    term_count: int = 0
    section_count: int = 0
    index_path: Optional[str] = None
    indexed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "sha256": self.sha256,
            "format_id": self.format_id,
            "term_count": self.term_count,
            "section_count": self.section_count,
            "index_path": self.index_path,
            "indexed_at": self.indexed_at,
        }


def build_index(
    source_id: str,
    sha256: str,
    format_id: str,
    normalized_artifact: Dict[str, Any],
    artifacts_dir: Optional[str] = None,
) -> SpecIndex:
    """
    Build a term → [section_id] index from a normalized artifact dict.
    """
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_root.mkdir(parents=True, exist_ok=True)

    sections = normalized_artifact.get("sections", [])
    terms: Dict[str, List[str]] = {}
    sections_by_id: Dict[str, Any] = {}

    for sec in sections:
        sid = sec["section_id"]
        sections_by_id[sid] = {
            "heading": sec["heading"],
            "level": sec["level"],
            "line_start": sec["line_start"],
        }
        combined = sec["heading"] + " " + sec.get("content", "")
        for tok in _tokenize(combined):
            if tok not in terms:
                terms[tok] = []
            if sid not in terms[tok]:
                terms[tok].append(sid)

    index_doc = {
        "source_id": source_id,
        "sha256": sha256,
        "format_id": format_id,
        "terms": terms,
        "sections_by_id": sections_by_id,
        "indexed_at": _now_iso(),
    }

    index_path = art_root / f"{source_id}-index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_doc, f, indent=2)

    return SpecIndex(
        source_id=source_id,
        sha256=sha256,
        format_id=format_id,
        term_count=len(terms),
        section_count=len(sections),
        index_path=str(index_path),
        indexed_at=index_doc["indexed_at"],
    )


def search_index(
    source_id: str,
    query: str,
    artifacts_dir: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search the index for terms matching query. Returns list of section dicts."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    index_path = art_root / f"{source_id}-index.json"
    if not index_path.exists():
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    query_tokens = _tokenize(query)
    matching_sids: Dict[str, int] = {}
    for tok in query_tokens:
        for sid in index.get("terms", {}).get(tok, []):
            matching_sids[sid] = matching_sids.get(sid, 0) + 1

    # Sort by match count descending
    results = []
    sections_by_id = index.get("sections_by_id", {})
    for sid, score in sorted(matching_sids.items(), key=lambda x: -x[1]):
        sec = sections_by_id.get(sid, {})
        results.append({
            "section_id": sid,
            "heading": sec.get("heading", ""),
            "level": sec.get("level", 1),
            "match_score": score,
        })
    return results


def load_index(source_id: str, artifacts_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load the full index document for a source."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    index_path = art_root / f"{source_id}-index.json"
    if not index_path.exists():
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)

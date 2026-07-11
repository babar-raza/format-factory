"""
ABW paragraph analytics — file-path based paragraph-level statistics.

Extends word_document.py with additional analytics. Uses load from abw_codec.
No spec_qname claim — analytics modules do not represent ABW element types.
"""
from __future__ import annotations

from pathlib import Path

from .abw_codec import load

spec_qname = "abw:document"
spec_fact_ref = "FACT-ABW-001"


def abw_total_char_count(source: "str | bytes | Path") -> int:
    """Return total character count across all paragraph texts (excluding whitespace between paragraphs)."""
    doc = load(source)
    return sum(len(p) for p in doc.get("paragraphs", []))


def abw_unique_paragraph_count(source: "str | bytes | Path") -> int:
    """Return count of paragraphs with distinct (unique) text content."""
    doc = load(source)
    return len(set(doc.get("paragraphs", [])))


def abw_has_repeated_paragraphs(source: "str | bytes | Path") -> bool:
    """Return True if any paragraph text appears more than once."""
    doc = load(source)
    paras = doc.get("paragraphs", [])
    return len(paras) != len(set(paras))


def abw_max_paragraph_char_count(source: "str | bytes | Path") -> int:
    """Return character count of the longest paragraph. 0 if no paragraphs."""
    doc = load(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0
    return max(len(p) for p in paras)


def abw_min_paragraph_char_count(source: "str | bytes | Path") -> int:
    """Return character count of the shortest paragraph. 0 if no paragraphs."""
    doc = load(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0
    return min(len(p) for p in paras)


def abw_avg_paragraph_char_count(source: "str | bytes | Path") -> float:
    """Return average character count per paragraph. 0.0 if no paragraphs."""
    doc = load(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0.0
    return sum(len(p) for p in paras) / len(paras)

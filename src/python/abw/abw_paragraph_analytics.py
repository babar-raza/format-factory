"""
ABW paragraph analytics — file-path based paragraph-level statistics.

Extends word_document.py with additional analytics. Uses load from abw_codec.
No spec_qname claim — analytics modules do not represent ABW element types.
"""
from __future__ import annotations

from pathlib import Path

from .abw_codec import load

spec_qname = "abw:document"
spec_fact_ref = "SAL-ABW-00001"


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


def abw_paragraph_count(source: "str | bytes | Path") -> int:
    """Return the total number of paragraphs in the ABW document.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("paragraph_count", 0)


def abw_section_count(source: "str | bytes | Path") -> int:
    """Return the total number of sections in the ABW document.

    Spec: ABW document section element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("section_count", 0)


def abw_is_abw(source: "str | bytes | Path") -> bool:
    """Return True if the document is identified as a valid ABW file.

    Spec: ABW document format (SAL-ABW-00001)
    """
    doc = load(source)
    return bool(doc.get("is_abw", False))


def abw_has_content(source: "str | bytes | Path") -> bool:
    """Return True if the document contains at least one paragraph.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("paragraph_count", 0) > 0


def abw_first_paragraph(source: "str | bytes | Path") -> str:
    """Return the text of the first paragraph, or empty string if none.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    paras = doc.get("paragraphs", [])
    return paras[0] if paras else ""


def abw_total_word_count(source: "str | bytes | Path") -> int:
    """Return the total word count across all paragraphs.

    Words are split by whitespace. Empty paragraphs contribute 0 words.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return sum(len(p.split()) for p in doc.get("paragraphs", []))


def abw_has_sections(source: "str | bytes | Path") -> bool:
    """Return True if the document contains at least one section.

    Spec: ABW document section element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("section_count", 0) > 0


def abw_last_paragraph(source: "str | bytes | Path") -> str:
    """Return text of the last paragraph, or empty string if none.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    paras = doc.get("paragraphs", [])
    return paras[-1] if paras else ""


def abw_is_single_paragraph(source: "str | bytes | Path") -> bool:
    """Return True if the document contains exactly one paragraph.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("paragraph_count", 0) == 1


def abw_paragraph_texts(source: "str | bytes | Path") -> list:
    """Return list of all paragraph text strings in document order.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return list(doc.get("paragraphs", []))


def abw_avg_word_count(source: "str | bytes | Path") -> float:
    """Return average word count per paragraph. 0.0 if no paragraphs.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0.0
    return sum(len(p.split()) for p in paras) / len(paras)


def abw_has_empty_paragraphs(source: "str | bytes | Path") -> bool:
    """Return True if any paragraph text is empty or whitespace-only.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return any(not p.strip() for p in doc.get("paragraphs", []))


def abw_nonempty_paragraph_count(source: "str | bytes | Path") -> int:
    """Return count of paragraphs that have at least one non-whitespace character.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return sum(1 for p in doc.get("paragraphs", []) if p.strip())


def abw_longest_paragraph(source: "str | bytes | Path") -> str:
    """Return the longest paragraph text by character count. Empty string if no paragraphs.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    paras = doc.get("paragraphs", [])
    return max(paras, key=len) if paras else ""


def abw_total_section_paragraph_count(source: "str | bytes | Path") -> int:
    """Return total paragraph count (synonym for abw_paragraph_count for clarity).

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return doc.get("paragraph_count", 0)


def abw_all_paragraphs_nonempty(source: "str | bytes | Path") -> bool:
    """Return True if every paragraph has non-empty, non-whitespace text.

    True vacuously when there are no paragraphs.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return all(p.strip() for p in doc.get("paragraphs", []))


def abw_paragraph_char_counts(source: "str | bytes | Path") -> list:
    """Return list of character counts per paragraph in document order.

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return [len(p) for p in doc.get("paragraphs", [])]


def abw_has_long_paragraphs(source: "str | bytes | Path", threshold: int = 200) -> bool:
    """Return True if any paragraph exceeds the character count threshold.

    Args:
        source: ABW file path.
        threshold: Minimum character count to consider a paragraph 'long' (default 200).

    Spec: ABW document paragraph element (SAL-ABW-00001)
    """
    doc = load(source)
    return any(len(p) >= threshold for p in doc.get("paragraphs", []))

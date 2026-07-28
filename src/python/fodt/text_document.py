"""
text_document.py — FODT text-document domain module.

Whole-document metric and summary operations over the parsed FODT text
document (paragraph / heading / word counts and related whole-document
properties). Each function accepts a file path, parses the document, and
describes a property of the document as a whole — the sanctioned
domain-module role for a ``*_document.py`` file (see
tests/test_source_structure.py). Parser source: parser.py
(parse_fodt_strict); spec concept: OpenDocument office:document.
"""
from __future__ import annotations

spec_qname = "office:document"
spec_fact_ref = "SAL-FODT-00001"
namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

import os


def fodt_paragraph_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the number of paragraph blocks in a FODT file.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer paragraph count.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for b in doc.get("blocks", []) if b.get("type") == "paragraph")


def fodt_word_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the total word count of a FODT file.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer word count.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            text = run.get("text", "")
            if text:
                count += len(text.split())
    return count


def fodt_heading_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the number of heading blocks in a FODT file.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer heading count.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for b in doc.get("blocks", []) if b.get("type") == "heading")


def fodt_has_tables(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the FODT file contains at least one table.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Boolean.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("tables", [])) > 0


def fodt_average_paragraph_length(file_path: "str | os.PathLike[str]") -> float:
    """Return the average character length of paragraphs. 0.0 if none."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = [b for b in doc.get("blocks", []) if b.get("type") == "paragraph"]
    if not blocks:
        return 0.0
    total = sum(len(b.get("text", "")) for b in blocks)
    return total / len(blocks)


def fodt_max_paragraph_length(file_path: "str | os.PathLike[str]") -> int:
    """Return the length in characters of the longest paragraph. 0 if no paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = [b for b in doc.get("blocks", []) if b.get("type") == "paragraph"]
    if not blocks:
        return 0
    return max(len(b.get("text", "")) for b in blocks)


def fodt_list_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the number of lists in the FODT document.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer count of top-level lists from the 'lists' key of the parsed doc.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("lists", []))


def fodt_empty_paragraph_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the count of paragraphs that contain no text.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer count of empty paragraphs (text is empty or whitespace-only).
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        if block.get("type") == "paragraph" and not block.get("text", "").strip():
            count += 1
    return count


def fodt_table_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the number of tables in the FODT document.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer count of tables from the 'tables' key of the parsed doc.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("tables", []))


def fodt_min_paragraph_length(file_path: "str | os.PathLike[str]") -> int:
    """Return the minimum character length of non-empty paragraphs.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        Integer min paragraph length, or 0 if no non-empty paragraphs.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = [
        len(b.get("text", ""))
        for b in doc.get("blocks", [])
        if b.get("type") == "paragraph" and b.get("text", "").strip()
    ]
    return min(lengths) if lengths else 0


def fodt_has_lists(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the FODT document contains any lists.

    Args:
        file_path: Path to a .fodt file.

    Returns:
        True if there is at least one list in the document.
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("lists", [])) > 0


def fodt_char_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the total character count across all paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for b in doc.get("blocks", []):
        if b.get("type") == "paragraph":
            total += len(b.get("text", ""))
    return total


def fodt_vocabulary_richness(file_path: "str | os.PathLike[str]") -> float:
    """Return unique_words / total_words. 0.0 if no words."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    words = []
    for b in doc.get("blocks", []):
        if b.get("type") == "paragraph":
            words.extend(b.get("text", "").split())
    if not words:
        return 0.0
    return len(set(w.lower() for w in words)) / len(words)


def fodt_is_empty(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the document has no content (no blocks or all empty)."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    if not blocks:
        return True
    for b in blocks:
        if b.get("text", "").strip():
            return False
    return True


def fodt_has_headings(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the document contains at least one heading block."""
    return fodt_heading_count(file_path) > 0


def fodt_is_single_paragraph(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the document has exactly one paragraph."""
    return fodt_paragraph_count(file_path) == 1


def fodt_avg_words_per_paragraph(file_path: "str | os.PathLike[str]") -> float:
    """Return average word count per paragraph. 0.0 if no paragraphs."""
    paras = fodt_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return fodt_word_count(file_path) / paras


def fodt_nonempty_paragraph_count(file_path: "str | os.PathLike[str]") -> int:
    """Return the count of paragraphs that contain at least one character."""
    return fodt_paragraph_count(file_path) - fodt_empty_paragraph_count(file_path)


def fodt_char_density(file_path: "str | os.PathLike[str]") -> float:
    """Return average characters per word. 0.0 if no words."""
    words = fodt_word_count(file_path)
    if words == 0:
        return 0.0
    return fodt_char_count(file_path) / words


def fodt_sentence_count(file_path: "str | os.PathLike[str]") -> int:
    """Return estimated sentence count based on sentence-ending punctuation."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    text = ""
    for block in doc.get("blocks", []):
        if isinstance(block, dict):
            text += block.get("text", "") + " "
    import re
    return len(re.findall(r'[.!?]+', text))


def fodt_words_per_sentence(file_path: "str | os.PathLike[str]") -> float:
    """Return words / sentences. 0.0 if no sentences."""
    sents = fodt_sentence_count(file_path)
    if sents == 0:
        return 0.0
    return fodt_word_count(file_path) / sents


def fodt_unique_word_count(file_path: "str | os.PathLike[str]") -> int:
    """Return count of distinct words (case-insensitive)."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    words = set()
    for block in doc.get("blocks", []):
        if isinstance(block, dict):
            for w in block.get("text", "").split():
                words.add(w.lower().strip(".,;:!?\"'()[]{}"))
    words.discard("")
    return len(words)


def fodt_avg_chars_per_word(file_path: "str | os.PathLike[str]") -> float:
    """Return average characters per word. 0.0 if no words."""
    words = fodt_word_count(file_path)
    if words == 0:
        return 0.0
    return fodt_char_count(file_path) / words


def fodt_heading_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of headings to total paragraphs. 0.0 if no paragraphs."""
    paragraphs = fodt_paragraph_count(file_path)
    if paragraphs == 0:
        return 0.0
    return fodt_heading_count(file_path) / paragraphs


def fodt_is_multi_paragraph(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if the document has more than one non-empty paragraph."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("text", "").strip():
            count += 1
            if count > 1:
                return True
    return False


def fodt_whitespace_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of whitespace characters to total characters. 0.0 if empty."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    text = ""
    for block in doc.get("blocks", []):
        if isinstance(block, dict):
            text += block.get("text", "")
    if not text:
        return 0.0
    ws = sum(1 for ch in text if ch.isspace())
    return ws / len(text)


def fodt_longest_word(file_path: "str | os.PathLike[str]") -> str:
    """Return the longest word in the document. Empty string if no words."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    longest = ""
    for block in doc.get("blocks", []):
        if isinstance(block, dict):
            for word in block.get("text", "").split():
                clean = word.strip(".,;:!?\"'()-")
                if len(clean) > len(longest):
                    longest = clean
    return longest


def fodt_avg_heading_length(file_path: "str | os.PathLike[str]") -> float:
    """Return average character length of headings. 0.0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = []
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") == "heading":
            lengths.append(len(block.get("text", "")))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def fodt_table_density(file_path: "str | os.PathLike[str]") -> float:
    """Return tables per 1000 words. 0.0 if no words."""
    wc = fodt_word_count(file_path)
    if wc == 0:
        return 0.0
    tc = fodt_table_count(file_path)
    return (tc / wc) * 1000


def fodt_heading_to_paragraph_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of headings to paragraphs. 0.0 if no paragraphs."""
    pc = fodt_paragraph_count(file_path)
    if pc == 0:
        return 0.0
    hc = fodt_heading_count(file_path)
    return hc / pc


def fodt_total_table_cells(file_path: "str | os.PathLike[str]") -> int:
    """Return total number of table cells across all tables. 0 if no tables."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") == "table":
            for row in block.get("rows", []):
                total += len(row.get("cells", []))
    return total


def fodt_total_text_length(file_path: "str | os.PathLike[str]") -> int:
    """Return total character count across all blocks (paragraphs and headings)."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") in ("paragraph", "heading"):
            total += len(block.get("text", ""))
    return total


def fodt_nonempty_paragraph_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of non-empty paragraphs to total paragraphs. 0.0 if none."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    paragraphs = [
        b for b in doc.get("blocks", [])
        if isinstance(b, dict) and b.get("type") == "paragraph"
    ]
    if not paragraphs:
        return 0.0
    nonempty = sum(1 for p in paragraphs if p.get("text", "").strip())
    return nonempty / len(paragraphs)


def fodt_has_numeric_content(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if any paragraph or heading contains a digit."""
    from .parser import parse_fodt_strict
    import re
    doc = parse_fodt_strict(file_path)
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") in ("paragraph", "heading"):
            if re.search(r"\d", block.get("text", "")):
                return True
    return False


def fodt_avg_sentence_length(file_path: "str | os.PathLike[str]") -> float:
    """Return average sentence length in characters. 0.0 if no sentences."""
    from .parser import parse_fodt_strict
    import re
    doc = parse_fodt_strict(file_path)
    all_text = " ".join(
        b.get("text", "")
        for b in doc.get("blocks", [])
        if isinstance(b, dict) and b.get("type") in ("paragraph", "heading")
    )
    sentences = [s.strip() for s in re.split(r"[.!?]+", all_text) if s.strip()]
    if not sentences:
        return 0.0
    return sum(len(s) for s in sentences) / len(sentences)


def fodt_longest_paragraph_index(file_path: "str | os.PathLike[str]") -> int:
    """Return 0-based index of the longest paragraph by character count. -1 if none."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    paragraphs = [
        b for b in doc.get("blocks", [])
        if isinstance(b, dict) and b.get("type") == "paragraph"
    ]
    if not paragraphs:
        return -1
    return max(range(len(paragraphs)), key=lambda i: len(paragraphs[i].get("text", "")))


def fodt_paragraph_length_range(file_path: "str | os.PathLike[str]") -> int:
    """Return the range (max - min) of paragraph lengths in characters. 0 if fewer than 2."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = []
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") == "paragraph":
            lengths.append(len(block.get("text", "")))
    if len(lengths) < 2:
        return 0
    return max(lengths) - min(lengths)


def fodt_max_heading_depth(file_path: "str | os.PathLike[str]") -> int:
    """Return the maximum heading outline level. 0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    max_depth = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") == "heading":
            level = block.get("outline_level", 1)
            if isinstance(level, int) and level > max_depth:
                max_depth = level
    return max_depth


def fodt_total_char_count(file_path: "str | os.PathLike[str]") -> int:
    """Return total character count across all paragraphs. 0 if none."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict) and block.get("type") == "paragraph":
            total += len(block.get("text", ""))
    return total


def fodt_heading_to_para_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of heading count to paragraph count. 0.0 if no paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    headings = 0
    paragraphs = 0
    for block in doc.get("blocks", []):
        if isinstance(block, dict):
            if block.get("type") == "heading":
                headings += 1
            elif block.get("type") == "paragraph":
                paragraphs += 1
    if paragraphs == 0:
        return 0.0
    return headings / paragraphs


def fodt_words_per_paragraph(file_path: "str | os.PathLike[str]") -> float:
    """Return word count divided by paragraph count. 0.0 if no paragraphs."""
    paras = fodt_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return fodt_word_count(file_path) / paras


def fodt_is_text_heavy(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if total char count exceeds 50."""
    return fodt_char_count(file_path) > 50


# ---------------------------------------------------------------------------
# Analytics functions added in FF-HEAL-QNAME-20260621-114042
# Spec refs: SAL-FODT-00001 (text content), SAL-FODT-00013 (paragraph),
#            SAL-FODT-00015 (headings), SAL-FODT-00002 (document structure)
# ---------------------------------------------------------------------------

def fodt_lowercase_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return ratio of lowercase letters to total letters in all text. 0.0 if no letters."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    lower = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            text = run.get("text", "")
            for ch in text:
                if ch.isalpha():
                    total += 1
                    if ch.islower():
                        lower += 1
    if total == 0:
        return 0.0
    return lower / total


def fodt_word_count_variance(file_path: "str | os.PathLike[str]") -> float:
    """Return variance of word counts across paragraphs. 0.0 if fewer than 2 paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    counts = []
    for block in doc.get("blocks", []):
        if block.get("type") == "paragraph":
            wc = sum(len(r.get("text", "").split()) for r in block.get("runs", []))
            counts.append(wc)
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fodt_paragraph_to_heading_ratio(file_path: "str | os.PathLike[str]") -> float:
    """Return paragraph count divided by heading count. 0.0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    paragraphs = sum(1 for b in doc.get("blocks", []) if b.get("type") == "paragraph")
    headings = sum(1 for b in doc.get("blocks", []) if b.get("type") == "heading")
    if headings == 0:
        return 0.0
    return paragraphs / headings


def fodt_digit_count(file_path: "str | os.PathLike[str]") -> int:
    """Return count of digit characters across all text runs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            count += sum(1 for ch in run.get("text", "") if ch.isdigit())
    return count



"""
ODT analytics functions extracted from odt_parser.py (TC-HEAL-FORMATS-BATCH2).
"""
from __future__ import annotations


spec_qname = "office:document"
spec_fact_ref = "FACT-ODT-001"
namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

import zipfile
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Any

from .odt_parser import (
    NS,
    _check_file_size,
    _validate_container,
    parse_odt_strict,
)


def odt_word_count(file_path: str | Path) -> int:
    """Count total words across all paragraphs, headings, and list items in an ODT file."""
    doc = parse_odt_strict(file_path)
    total = 0
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str):
            total += len(text.split())
    return total


def odt_heading_count(file_path: str | Path) -> int:
    """Count the number of headings in an ODT document."""
    doc = parse_odt_strict(file_path)
    return len(doc.headings)


def odt_paragraph_count(file_path: str | Path) -> int:
    """Count the number of paragraphs in an ODT document."""
    doc = parse_odt_strict(file_path)
    return len(doc.paragraphs)


def odt_char_count(file_path: str | Path) -> int:
    """Return the total character count across all paragraphs in an ODT document."""
    doc = parse_odt_strict(file_path)
    return sum(len(p.text) for p in doc.paragraphs)


def odt_list_count(file_path: str | Path) -> int:
    """Count the number of top-level lists in an ODT document.

    Counts text:list elements that are direct children of the text body.
    ODF 1.3 §5.3.1 — text:list is the element for ordered/unordered lists.

    Args:
        file_path: Path to .odt file.

    Returns:
        Number of top-level text:list elements.
    """
    path = Path(file_path)
    _check_file_size(path)
    with zipfile.ZipFile(path, "r") as zf:
        _validate_container(zf)
        content = zf.read("content.xml")
    root = ET.fromstring(content)
    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return 0
    text_body = body.find(f"{{{NS['office']}}}text")
    if text_body is None:
        return 0
    list_tag = f"{{{NS['text']}}}list"
    return sum(1 for child in text_body if child.tag == list_tag)


def odt_table_count(file_path: str | Path) -> int:
    """Count the number of tables in an ODT document.

    Counts table:table elements that are direct children of the text body.
    ODF 1.3 §9.1.2 — table:table is the element for tables in text documents.

    Args:
        file_path: Path to .odt file.

    Returns:
        Number of table:table elements in the text body.
    """
    path = Path(file_path)
    _check_file_size(path)
    with zipfile.ZipFile(path, "r") as zf:
        _validate_container(zf)
        content = zf.read("content.xml")
    root = ET.fromstring(content)
    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return 0
    text_body = body.find(f"{{{NS['office']}}}text")
    if text_body is None:
        return 0
    table_tag = f"{{{NS['table']}}}table"
    return sum(1 for child in text_body if child.tag == table_tag)


def odt_sentence_count(file_path: str | Path) -> int:
    """Estimate the number of sentences in an ODT document.

    Counts sentence-ending punctuation (.!?) across all paragraphs and
    headings.  This is a heuristic — abbreviations like "Dr." will be
    over-counted, but for most prose it gives a reasonable approximation.

    Args:
        file_path: Path to .odt file.

    Returns:
        Estimated number of sentences.
    """
    import re
    doc = parse_odt_strict(file_path)
    total = 0
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            total += len(re.findall(r"[.!?]+", text))
    return total


def odt_average_word_length(file_path: str | Path) -> float:
    """Return the average word length (characters per word) in an ODT document.

    Args:
        file_path: Path to .odt file.

    Returns:
        Float average word length. Returns 0.0 if document has no words.
    """
    doc = parse_odt_strict(file_path)
    words: list[str] = []
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            words.extend(text.split())
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def odt_unique_word_count(file_path: str | Path) -> int:
    """Return the number of distinct words (case-insensitive) in an ODT document.

    Args:
        file_path: Path to .odt file.

    Returns:
        Integer count of unique words.
    """
    doc = parse_odt_strict(file_path)
    unique: set[str] = set()
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            unique.update(w.lower() for w in text.split())
    return len(unique)


def odt_longest_paragraph(file_path: str | Path) -> int:
    """Return the character count of the longest paragraph in an ODT document.

    Returns 0 if no paragraphs exist.
    """
    doc = parse_odt_strict(file_path)
    max_len = 0
    for elem in doc.elements:
        elem_type = getattr(elem, "type", getattr(elem, "tag", ""))
        text = getattr(elem, "text", "")
        if isinstance(text, str) and ("paragraph" in str(elem_type).lower() or "p" == str(elem_type).lower()):
            max_len = max(max_len, len(text))
    if max_len == 0:
        for elem in doc.elements:
            text = getattr(elem, "text", "")
            if isinstance(text, str):
                max_len = max(max_len, len(text))
    return max_len


def odt_has_tables(file_path: str | Path) -> bool:
    """Return True if the ODT document contains at least one table."""
    return odt_table_count(file_path) > 0


def odt_avg_paragraph_length(file_path: str | Path) -> float:
    """Return the average character length of paragraphs.

    Args:
        file_path: Path to an ODT file.

    Returns:
        Float average characters per paragraph, or 0.0 if no paragraphs.
    """
    para_count = odt_paragraph_count(file_path)
    if para_count == 0:
        return 0.0
    return odt_char_count(file_path) / para_count


def odt_words_per_sentence(file_path: str | Path) -> float:
    """Return the average number of words per sentence.

    Args:
        file_path: Path to an ODT file.

    Returns:
        Float average words per sentence, or 0.0 if no sentences.
    """
    sentence_count = odt_sentence_count(file_path)
    if sentence_count == 0:
        return 0.0
    return odt_word_count(file_path) / sentence_count


def odt_vocabulary_richness(file_path: str | Path) -> float:
    """Return vocabulary richness: unique_words / total_words.

    Also known as type-token ratio (TTR). Higher values mean more
    diverse vocabulary.

    Args:
        file_path: Path to an ODT file.

    Returns:
        Float ratio 0.0-1.0, or 0.0 if no words.
    """
    total = odt_word_count(file_path)
    if total == 0:
        return 0.0
    unique = odt_unique_word_count(file_path)
    return unique / total


def odt_chars_per_word(file_path: str | Path) -> float:
    """Return the average number of characters per word.

    Args:
        file_path: Path to an ODT file.

    Returns:
        Float average, or 0.0 if no words.
    """
    words = odt_word_count(file_path)
    if words == 0:
        return 0.0
    return odt_char_count(file_path) / words


def odt_has_headings(file_path: str | Path) -> bool:
    """Return True if the ODT document contains at least one heading."""
    doc = parse_odt_strict(file_path)
    return len(doc.headings) > 0


def odt_max_paragraph_length(file_path: str | Path) -> int:
    """Return the character count of the longest paragraph. Returns 0 if none."""
    doc = parse_odt_strict(file_path)
    if not doc.paragraphs:
        return 0
    return max(len(p.text) for p in doc.paragraphs)


def odt_min_paragraph_length(file_path: str | Path) -> int:
    """Return the character count of the shortest paragraph. Returns 0 if none."""
    doc = parse_odt_strict(file_path)
    if not doc.paragraphs:
        return 0
    return min(len(p.text) for p in doc.paragraphs)


def odt_heading_to_paragraph_ratio(file_path: str | Path) -> float:
    """Return the ratio of headings to paragraphs. 0.0 if no paragraphs."""
    doc = parse_odt_strict(file_path)
    if not doc.paragraphs:
        return 0.0
    return len(doc.headings) / len(doc.paragraphs)


def odt_total_elements(file_path: str | Path) -> int:
    """Return the total count of parsed elements (paragraphs + headings)."""
    doc = parse_odt_strict(file_path)
    return len(doc.paragraphs) + len(doc.headings)


def odt_is_empty(file_path: str | Path) -> bool:
    """Return True if the document has no paragraphs or headings."""
    doc = parse_odt_strict(file_path)
    return len(doc.paragraphs) == 0 and len(doc.headings) == 0


def odt_shortest_word(file_path: str | Path) -> int:
    """Return the length of the shortest word across all paragraphs. 0 if none."""
    doc = parse_odt_strict(file_path)
    words = []
    for p in doc.paragraphs:
        words.extend(p.text.split())
    if not words:
        return 0
    return min(len(w) for w in words)


def odt_paragraph_density(file_path: str | Path) -> float:
    """Return total paragraph characters / total elements. 0.0 if no elements."""
    doc = parse_odt_strict(file_path)
    total_elements = len(doc.paragraphs) + len(doc.headings)
    if total_elements == 0:
        return 0.0
    total_chars = sum(len(p.text) for p in doc.paragraphs)
    return total_chars / total_elements


def odt_heading_density(file_path: str | Path) -> float:
    """Return heading count / total elements. 0.0 if no elements."""
    doc = parse_odt_strict(file_path)
    total = len(doc.paragraphs) + len(doc.headings)
    if total == 0:
        return 0.0
    return len(doc.headings) / total


def odt_longest_word(file_path: str | Path) -> int:
    """Return the length of the longest word across all paragraphs. 0 if none."""
    doc = parse_odt_strict(file_path)
    words = []
    for p in doc.paragraphs:
        words.extend(p.text.split())
    if not words:
        return 0
    return max(len(w) for w in words)


def odt_list_to_paragraph_ratio(file_path: str | Path) -> float:
    """Return list count / paragraph count. 0.0 if no paragraphs."""
    paras = odt_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return odt_list_count(file_path) / paras


def odt_has_lists(file_path: str | Path) -> bool:
    """Return True if the document contains at least one list."""
    return odt_list_count(file_path) > 0


def odt_has_unicode(file_path: str | Path) -> bool:
    """Return True if any paragraph contains non-ASCII (Unicode) characters."""
    doc = parse_odt_strict(file_path)
    return any(ord(c) > 127 for p in doc.paragraphs for c in p.text)


def odt_max_words_per_paragraph(file_path: str | Path) -> int:
    """Return the maximum word count in any paragraph; 0 if no paragraphs."""
    doc = parse_odt_strict(file_path)
    counts = [len(p.text.split()) for p in doc.paragraphs if p.text.strip()]
    return max(counts) if counts else 0


def odt_min_words_per_paragraph(file_path: str | Path) -> int:
    """Return the minimum word count in any non-empty paragraph; 0 if none."""
    doc = parse_odt_strict(file_path)
    counts = [len(p.text.split()) for p in doc.paragraphs if p.text.strip()]
    return min(counts) if counts else 0


def odt_word_density(file_path: str | Path) -> float:
    """Return words / paragraphs. 0.0 if no paragraphs."""
    doc = parse_odt_strict(file_path)
    paras = len(doc.paragraphs)
    if paras == 0:
        return 0.0
    words = sum(len(p.text.split()) for p in doc.paragraphs)
    return words / paras


def odt_sentence_density(file_path: str | Path) -> float:
    """Return sentences / paragraphs. 0.0 if no paragraphs."""
    paras = odt_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return odt_sentence_count(file_path) / paras


def odt_table_density(file_path: str | Path) -> float:
    """Return tables / total elements (paragraphs + headings). 0.0 if no elements."""
    total = odt_total_elements(file_path)
    if total == 0:
        return 0.0
    return odt_table_count(file_path) / total


def odt_nonempty_paragraph_count(file_path: str | Path) -> int:
    """Return the count of paragraphs that contain non-whitespace text."""
    doc = parse_odt_strict(file_path)
    return sum(1 for p in doc.paragraphs if p.text.strip())


def odt_char_density(file_path: str | Path) -> float:
    """Return characters / paragraphs. 0.0 if no paragraphs."""
    doc = parse_odt_strict(file_path)
    paras = len(doc.paragraphs)
    if paras == 0:
        return 0.0
    chars = sum(len(p.text) for p in doc.paragraphs)
    return chars / paras


def odt_empty_paragraph_count(file_path: str | Path) -> int:
    """Return the count of paragraphs with only whitespace text."""
    doc = parse_odt_strict(file_path)
    return sum(1 for p in doc.paragraphs if not p.text.strip())


def odt_words_per_heading(file_path: str | Path) -> float:
    """Return total words / headings. 0.0 if no headings."""
    doc = parse_odt_strict(file_path)
    headings = len(doc.headings)
    if headings == 0:
        return 0.0
    words = sum(len(p.text.split()) for p in doc.paragraphs)
    return words / headings


def odt_avg_words_per_sentence(file_path: str | Path) -> float:
    """Return average words per sentence. 0.0 if no sentences."""
    doc = parse_odt_strict(file_path)
    sentences = odt_sentence_count(file_path)
    if sentences == 0:
        return 0.0
    words = sum(len(p.text.split()) for p in doc.paragraphs)
    return words / sentences


def odt_shortest_paragraph_length(file_path: str | Path) -> int:
    """Return the character length of the shortest non-empty paragraph. 0 if none."""
    doc = parse_odt_strict(file_path)
    lengths = [len(p.text) for p in doc.paragraphs if p.text.strip()]
    if not lengths:
        return 0
    return min(lengths)




def odt_avg_chars_per_paragraph(file_path: str | Path) -> float:
    """Return the average character count per non-empty paragraph. 0.0 if none."""
    doc = parse_odt_strict(file_path)
    lengths = [len(p.text) for p in doc.paragraphs if p.text.strip()]
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def odt_paragraph_variance(file_path: str | Path) -> float:
    """Return variance of word counts across non-empty paragraphs. 0.0 if fewer than 2."""
    doc = parse_odt_strict(file_path)
    counts = [len(p.text.split()) for p in doc.paragraphs if p.text.strip()]
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def odt_is_single_paragraph(file_path: str | Path) -> bool:
    """Return True if the document has exactly one non-empty paragraph."""
    doc = parse_odt_strict(file_path)
    nonempty = [p for p in doc.paragraphs if p.text.strip()]
    return len(nonempty) == 1


def odt_list_density(file_path: str | Path) -> float:
    """Return lists / total elements. 0.0 if no elements."""
    total = odt_total_elements(file_path)
    if total == 0:
        return 0.0
    return odt_list_count(file_path) / total


def odt_heading_per_paragraph(file_path: str | Path) -> float:
    """Return headings / paragraphs. 0.0 if no paragraphs."""
    paras = odt_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return odt_heading_count(file_path) / paras


def odt_is_multi_paragraph(file_path: str | Path) -> bool:
    """Return True if the document has more than one non-empty paragraph."""
    doc = parse_odt_strict(file_path)
    nonempty = [p for p in doc.paragraphs if p.text.strip()]
    return len(nonempty) > 1


def odt_avg_chars_per_word(file_path: str | Path) -> float:
    """Return average characters per word. 0.0 if no words."""
    words = odt_word_count(file_path)
    if words == 0:
        return 0.0
    return odt_char_count(file_path) / words


def odt_is_content_rich(file_path: str | Path) -> bool:
    """Return True if the document has more than 2 words."""
    return odt_word_count(file_path) > 2


def odt_whitespace_ratio(file_path: str | Path) -> float:
    """Return ratio of whitespace characters to total characters. 0.0 if empty."""
    doc = parse_odt_strict(file_path)
    text = " ".join(p.text for p in doc.paragraphs)
    if not text:
        return 0.0
    ws = sum(1 for ch in text if ch.isspace())
    return ws / len(text)


def odt_total_text_length(file_path: str | Path) -> int:
    """Return total character count across all paragraphs (including spaces)."""
    doc = parse_odt_strict(file_path)
    return sum(len(p.text) for p in doc.paragraphs)


def odt_nonempty_paragraph_ratio(file_path: str | Path) -> float:
    """Return ratio of non-empty paragraphs to total paragraphs. 0.0 if no paragraphs."""
    doc = parse_odt_strict(file_path)
    paras = doc.paragraphs
    if not paras:
        return 0.0
    nonempty = sum(1 for p in paras if p.text.strip())
    return nonempty / len(paras)


def odt_avg_sentence_length(file_path: str | Path) -> float:
    """Return average character length per sentence. 0.0 if no sentences."""
    import re as _re
    doc = parse_odt_strict(file_path)
    text = " ".join(p.text for p in doc.paragraphs)
    sentences = [s.strip() for s in _re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    return sum(len(s) for s in sentences) / len(sentences)


def odt_longest_paragraph_index(file_path: str | Path) -> int:
    """Return 0-based index of the longest paragraph by character count. -1 if none."""
    doc = parse_odt_strict(file_path)
    paras = doc.paragraphs
    if not paras:
        return -1
    return max(range(len(paras)), key=lambda i: len(paras[i].text))


def odt_has_numeric_content(file_path: str | Path) -> bool:
    """Return True if any paragraph contains at least one digit."""
    doc = parse_odt_strict(file_path)
    return any(any(ch.isdigit() for ch in p.text) for p in doc.paragraphs)


def odt_numeric_value_sum(file_path: str | Path) -> float:
    """Return sum of all numeric tokens found in the document text. 0.0 if none."""
    import re as _re
    doc = parse_odt_strict(file_path)
    text = " ".join(p.text for p in doc.paragraphs)
    tokens = _re.findall(r"-?\d+(?:\.\d+)?", text)
    if not tokens:
        return 0.0
    return sum(float(t) for t in tokens)


def odt_unique_char_count(file_path: str | Path) -> int:
    """Return count of unique characters across all paragraph text."""
    doc = parse_odt_strict(file_path)
    text = " ".join(p.text for p in doc.paragraphs)
    return len(set(text))


def odt_nonspace_char_count(file_path: str | Path) -> int:
    """Return count of non-whitespace characters across all paragraph text."""
    doc = parse_odt_strict(file_path)
    text = " ".join(p.text for p in doc.paragraphs)
    return sum(1 for c in text if not c.isspace())


"""
ABW analytics — extracted analytics/computation functions for AbiWord documents.

These functions are separated from the core codec to keep abw_codec.py within
the source-structure policy limits (800 LOC / 60 functions).

All functions here import load/extract_text/count_words from the core codec.
"""

from __future__ import annotations

spec_qname = "abw:document"
spec_fact_ref = "SAL-ABW-00001"
namespace_uri = "http://www.abisource.com/awml.dtd"

import re
from pathlib import Path

from .abw_codec import extract_text, load
from .abw_word_stats import count_words


def abw_sentence_count(model: dict) -> int:
    """Return an approximate sentence count by counting sentence-ending punctuation."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    all_text = " ".join(model.get("paragraphs", []))
    return sum(1 for c in all_text if c in ".!?")


def abw_longest_word(model: dict) -> str:
    """Return the longest word found across all paragraphs.

    Args:
        model: Parsed ABW model dict with 'paragraphs' key.

    Returns:
        The longest word as a string. Returns empty string if no words found.
        If multiple words share the maximum length, the first one is returned.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    all_text = " ".join(str(p) for p in model.get("paragraphs", []))
    words = all_text.split()
    if not words:
        return ""
    return max(words, key=len)


def abw_total_char_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of characters across all paragraphs.

    Convenience file-path API: loads the document internally and sums
    the character counts of all paragraph text.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer total character count (spaces included within paragraphs,
        inter-paragraph separators excluded).

    Raises:
        AbwParseError: If the file cannot be parsed.
    """
    lines = extract_text(file_path)
    return sum(len(line) for line in lines)


def abw_nonempty_paragraph_count(file_path: "str | bytes | Path") -> int:
    """Return the count of paragraphs that contain at least one non-whitespace character.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer count of non-empty paragraphs.

    Raises:
        AbwParseError: If the file cannot be parsed.
    """
    lines = extract_text(file_path)
    return sum(1 for line in lines if line.strip())


def abw_word_count(file_path: "str | bytes | Path") -> int:
    """Return the total word count across all paragraphs in an ABW file.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer total word count.
    """
    model = load(file_path)
    return count_words(model)


def abw_empty_paragraph_count(file_path: "str | bytes | Path") -> int:
    """Return the count of paragraphs that are empty or contain only whitespace.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer count of empty/whitespace-only paragraphs.

    Raises:
        AbwParseError: If the file cannot be parsed.
    """
    lines = extract_text(file_path)
    return sum(1 for line in lines if not line.strip())


def abw_average_word_length(file_path: "str | bytes | Path") -> float:
    """Return the average word length (characters per word) across all paragraphs.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Float average word length. Returns 0.0 if there are no words.
    """
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    total_chars = 0
    total_words = 0
    for p in paragraphs:
        words = p.split()
        total_words += len(words)
        total_chars += sum(len(w) for w in words)
    if total_words == 0:
        return 0.0
    return total_chars / total_words


def abw_max_paragraph_length(file_path: "str | bytes | Path") -> int:
    """Return the character count of the longest paragraph.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer length of longest paragraph. Returns 0 if no paragraphs.
    """
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return 0
    return max(len(p) for p in paragraphs)


def abw_unique_word_count(file_path: "str | bytes | Path") -> int:
    """Return the number of distinct words (case-insensitive) across all paragraphs.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer count of unique words.
    """
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    words: set[str] = set()
    for p in paragraphs:
        words.update(w.lower() for w in p.split())
    return len(words)


def get_paragraphs(model: dict) -> list[str]:
    """Return a copy of all paragraph texts from a loaded ABW model.

    Args:
        model: A dict returned by :func:`load`.

    Returns:
        List of paragraph strings (may include empty strings for blank paragraphs).

    Raises:
        TypeError: If *model* is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return list(model.get("paragraphs", []))


def abw_paragraph_count(file_path: "str | bytes | Path") -> int:
    """Return the number of paragraphs in an ABW file.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer count of paragraphs.
    """
    model = load(file_path)
    return len(model.get("paragraphs", []))


def abw_shortest_word(file_path: "str | bytes | Path") -> str:
    """Return the shortest word in the ABW document.

    Args:
        file_path: Path to an ABW file.

    Returns:
        The shortest word string. Empty string if no words.
    """
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    shortest = ""
    for para in paragraphs:
        text = para if isinstance(para, str) else para.get("text", "") if isinstance(para, dict) else ""
        if isinstance(text, str):
            for word in text.split():
                if word and (not shortest or len(word) < len(shortest)):
                    shortest = word
    return shortest


def abw_has_sections(file_path: "str | bytes | Path") -> bool:
    """Return True if the ABW file contains section elements.

    Args:
        file_path: Path to an ABW file.

    Returns:
        True if section count > 0.
    """
    model = load(file_path)
    return model.get("section_count", 0) > 0


def abw_has_metadata(file_path: "str | bytes | Path") -> bool:
    """Return True if the ABW file contains any metadata fields.

    Args:
        file_path: Path to an ABW file.

    Returns:
        True if metadata dict is non-empty.
    """
    model = load(file_path)
    meta = model.get("metadata", {})
    return bool(meta)


def abw_total_word_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of words across all paragraphs."""
    model = load(file_path)
    total = 0
    for para in model.get("paragraphs", []):
        text = para if isinstance(para, str) else para.get("text", "") if isinstance(para, dict) else ""
        if isinstance(text, str):
            total += len(text.split())
    return total


def abw_char_count(file_path: "str | bytes | Path") -> int:
    """Return the total character count across all paragraphs.

    Args:
        file_path: Path to an ABW file.

    Returns:
        Integer total character count.
    """
    model = load(file_path)
    total = 0
    for para in model.get("paragraphs", []):
        text = para if isinstance(para, str) else para.get("text", "") if isinstance(para, dict) else ""
        if isinstance(text, str):
            total += len(text)
    return total


def abw_min_paragraph_length(file_path: "str | bytes | Path") -> int:
    """Return the character count of the shortest non-empty paragraph; 0 if none."""
    model = load(file_path)
    min_len = None
    for para in model.get("paragraphs", []):
        text = para if isinstance(para, str) else para.get("text", "") if isinstance(para, dict) else ""
        if isinstance(text, str) and text.strip():
            length = len(text)
            if min_len is None or length < min_len:
                min_len = length
    return min_len if min_len is not None else 0


def abw_has_content(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has at least one non-empty paragraph."""
    model = load(file_path)
    for para in model.get("paragraphs", []):
        text = para if isinstance(para, str) else para.get("text", "") if isinstance(para, dict) else ""
        if isinstance(text, str) and text.strip():
            return True
    return False


def abw_heading_count(file_path: "str | bytes | Path") -> int:
    """Return the number of heading-style paragraphs (style contains 'heading')."""
    model = load(file_path)
    count = 0
    for para in model.get("paragraphs", []):
        if isinstance(para, dict):
            style = para.get("style", "")
            if isinstance(style, str) and "heading" in style.lower():
                count += 1
    return count


def abw_vocabulary_richness(file_path: "str | bytes | Path") -> float:
    """Return unique_words / total_words. 0.0 if no words."""
    total = abw_total_word_count(file_path)
    if total == 0:
        return 0.0
    unique = abw_unique_word_count(file_path)
    return unique / total


def abw_average_paragraph_length(file_path: "str | bytes | Path") -> float:
    """Return the average length of paragraphs in characters. 0.0 if none."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    texts = []
    for p in paragraphs:
        if isinstance(p, dict):
            texts.append(p.get("text", ""))
        elif isinstance(p, str):
            texts.append(p)
    if not texts:
        return 0.0
    return sum(len(t) for t in texts) / len(texts)


def abw_is_empty(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has no content (no paragraphs or all empty)."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return True
    for p in paragraphs:
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        if text.strip():
            return False
    return True


def abw_sentence_density(file_path: "str | bytes | Path") -> float:
    """Return sentences / paragraphs. 0.0 if no paragraphs."""
    paras = abw_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    model = load(file_path)
    return abw_sentence_count(model) / paras


def abw_has_unicode(file_path: "str | bytes | Path") -> bool:
    """Return True if any paragraph contains non-ASCII characters."""
    model = load(file_path)
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        if any(ord(c) > 127 for c in text):
            return True
    return False


def abw_is_single_paragraph(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has exactly one paragraph."""
    return abw_paragraph_count(file_path) == 1


def abw_avg_words_per_paragraph(file_path: "str | bytes | Path") -> float:
    """Return the average number of words per paragraph. 0.0 if no paragraphs."""
    paras = abw_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return abw_word_count(file_path) / paras


def abw_char_density(file_path: "str | bytes | Path") -> float:
    """Return characters / paragraphs. 0.0 if no paragraphs."""
    paras = abw_paragraph_count(file_path)
    if paras == 0:
        return 0.0
    return abw_char_count(file_path) / paras


def abw_longest_paragraph_length(file_path: "str | bytes | Path") -> int:
    """Return the length in characters of the longest paragraph. 0 if none."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return 0
    return max(len(p.get("text", "") if isinstance(p, dict) else str(p)) for p in paragraphs)


def abw_words_per_sentence(file_path: "str | bytes | Path") -> float:
    """Return average words per sentence. 0.0 if no sentences."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    text = " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in paragraphs)
    sentences = len(re.findall(r'[.!?]+', text))
    if sentences == 0:
        return 0.0
    words = len(text.split())
    return words / sentences


def abw_paragraph_length_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of paragraph lengths (in chars). 0.0 if fewer than 2 paragraphs."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    lengths = [len(p.get("text", "") if isinstance(p, dict) else str(p)) for p in paragraphs if (p.get("text", "") if isinstance(p, dict) else str(p)).strip()]
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    return sum((ln - mean) ** 2 for ln in lengths) / len(lengths)


def abw_is_multi_paragraph(file_path: "str | bytes | Path") -> bool:
    """Return True if document has more than one non-empty paragraph."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    nonempty = [p for p in paragraphs if (p.get("text", "") if isinstance(p, dict) else str(p)).strip()]
    return len(nonempty) > 1


def abw_heading_density(file_path: "str | bytes | Path") -> float:
    """Return headings / total paragraphs. 0.0 if no paragraphs."""
    total = abw_paragraph_count(file_path)
    if total == 0:
        return 0.0
    return abw_heading_count(file_path) / total


def abw_is_content_rich(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has more than one unique word."""
    return abw_unique_word_count(file_path) > 1


def abw_avg_chars_per_word(file_path: "str | bytes | Path") -> float:
    """Return average characters per word. 0.0 if no words."""
    words = abw_word_count(file_path)
    if words == 0:
        return 0.0
    return abw_char_count(file_path) / words


def abw_whitespace_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of whitespace characters to total characters. 0.0 if empty."""
    model = load(file_path)
    text = ""
    for p in model.get("paragraphs", []):
        text += p.get("text", "") if isinstance(p, dict) else str(p)
    if not text:
        return 0.0
    ws = sum(1 for ch in text if ch.isspace())
    return ws / len(text)


def abw_avg_sentence_length(file_path: "str | bytes | Path") -> float:
    """Return average sentence length in characters. 0.0 if no sentences."""
    model = load(file_path)
    all_text = " ".join(
        (p.get("text", "") if isinstance(p, dict) else str(p))
        for p in model.get("paragraphs", [])
    )
    sentences = [s.strip() for s in re.split(r"[.!?]+", all_text) if s.strip()]
    if not sentences:
        return 0.0
    return sum(len(s) for s in sentences) / len(sentences)


def abw_punctuation_count(file_path: "str | bytes | Path") -> int:
    """Return total count of punctuation characters in the document."""
    model = load(file_path)
    count = 0
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        count += sum(1 for ch in text if ch in ".,;:!?\"'()-[]{}…–—")
    return count


def abw_median_paragraph_length(file_path: "str | bytes | Path") -> int:
    """Return median paragraph length in characters. 0 if no paragraphs."""
    model = load(file_path)
    lengths = []
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        lengths.append(len(text))
    if not lengths:
        return 0
    lengths.sort()
    mid = len(lengths) // 2
    if len(lengths) % 2 == 0:
        return (lengths[mid - 1] + lengths[mid]) // 2
    return lengths[mid]


def abw_longest_paragraph_words(file_path: "str | bytes | Path") -> int:
    """Return the word count of the longest paragraph. 0 if no paragraphs."""
    model = load(file_path)
    max_words = 0
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        wc = len(text.split())
        if wc > max_words:
            max_words = wc
    return max_words


def abw_distinct_word_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of distinct words to total words. 0.0 if no words."""
    model = load(file_path)
    all_words = []
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        all_words.extend(text.lower().split())
    if not all_words:
        return 0.0
    return len(set(all_words)) / len(all_words)


def abw_total_text_length(file_path: "str | bytes | Path") -> int:
    """Return total character count across all paragraphs."""
    model = load(file_path)
    total = 0
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        total += len(text)
    return total


def abw_nonempty_paragraph_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty paragraphs to total paragraphs. 0.0 if none."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return 0.0
    nonempty = sum(
        1 for p in paragraphs
        if (p.get("text", "") if isinstance(p, dict) else str(p)).strip()
    )
    return nonempty / len(paragraphs)


def abw_has_numeric_content(file_path: "str | bytes | Path") -> bool:
    """Return True if any paragraph contains a digit."""
    model = load(file_path)
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        if re.search(r"\d", text):
            return True
    return False


def abw_longest_paragraph_index(file_path: "str | bytes | Path") -> int:
    """Return 0-based index of the longest paragraph. -1 if no paragraphs."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return -1
    texts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in paragraphs]
    return max(range(len(texts)), key=lambda i: len(texts[i]))


def abw_unique_char_count(file_path: "str | bytes | Path") -> int:
    """Return count of unique characters across all paragraph text. 0 if empty."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    text = " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in paragraphs)
    return len(set(text)) if text else 0


def abw_nonspace_char_count(file_path: "str | bytes | Path") -> int:
    """Return count of non-whitespace characters across all paragraph text."""
    model = load(file_path)
    paragraphs = model.get("paragraphs", [])
    text = " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in paragraphs)
    return sum(1 for c in text if not c.isspace())


def abw_line_count(file_path: "str | bytes | Path") -> int:
    """Return total number of lines across all paragraphs. 0 if empty."""
    model = load(file_path)
    total = 0
    for p in model.get("paragraphs", []):
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        total += text.count("\n") + (1 if text else 0)
    return total


def abw_uppercase_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of uppercase letters to total letters. 0.0 if no letters."""
    model = load(file_path)
    all_text = " ".join(
        p.get("text", "") if isinstance(p, dict) else str(p)
        for p in model.get("paragraphs", [])
    )
    letters = [c for c in all_text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def abw_section_count(file_path: "str | bytes | Path") -> int:
    """Return the number of <section> elements in the ABW document.

    Closes: GAP-ABW-FOSS-ABW_SECTION_-001

    Args:
        file_path: Path to .abw file, bytes, or XML string.

    Returns:
        Number of sections. 0 if document has no sections.
    """
    model = load(file_path)
    return model.get("section_count", 0)


def abw_has_headings(file_path: "str | bytes | Path") -> bool:
    """Return True if the document contains any heading-style paragraphs.

    Closes: GAP-ABW-FOSS-ABW_HAS_HEAD-001

    Args:
        file_path: Path to .abw file, bytes, or XML string.

    Returns:
        True if any paragraph has a heading-style attribute, False otherwise.
    """
    return abw_heading_count(file_path) > 0


VOWELS = set("aeiouAEIOU")
CONSONANTS = set("bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ")


def _all_text(file_path: "str | bytes | Path") -> str:
    model = load(file_path)
    return " ".join(
        p.get("text", "") if isinstance(p, dict) else str(p)
        for p in model.get("paragraphs", [])
    )


def _all_words(file_path: "str | bytes | Path") -> list:
    import re
    return re.findall(r"\b\w+\b", _all_text(file_path))


def abw_digit_count(file_path: "str | bytes | Path") -> int:
    """Return count of digit characters across all paragraphs."""
    return sum(1 for c in _all_text(file_path) if c.isdigit())


def abw_alpha_char_count(file_path: "str | bytes | Path") -> int:
    """Return count of alphabetic characters across all paragraphs."""
    return sum(1 for c in _all_text(file_path) if c.isalpha())


def abw_alpha_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of alphabetic characters to total paragraph characters. 0.0 if empty."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    total = sum(len(p.get("text", "") if isinstance(p, dict) else str(p)) for p in paras)
    if not total:
        return 0.0
    alpha = sum(
        1 for p in paras
        for c in (p.get("text", "") if isinstance(p, dict) else str(p))
        if c.isalpha()
    )
    return alpha / total


def abw_avg_paragraph_length(file_path: "str | bytes | Path") -> float:
    """Return average paragraph length in characters."""
    return abw_average_paragraph_length(file_path)


def abw_avg_paragraph_words(file_path: "str | bytes | Path") -> float:
    """Return average number of words per paragraph."""
    import re
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0.0
    total = sum(
        len(re.findall(r"\b\w+\b", p.get("text", "") if isinstance(p, dict) else str(p)))
        for p in paras
    )
    return total / len(paras)


def abw_char_per_paragraph(file_path: "str | bytes | Path") -> float:
    """Return average characters per paragraph."""
    return abw_average_paragraph_length(file_path)


def abw_chars_per_word(file_path: "str | bytes | Path") -> float:
    """Return total paragraph chars divided by word count. 0.0 if no words."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    total_chars = sum(len(p.get("text", "") if isinstance(p, dict) else str(p)) for p in paras)
    words = []
    for p in paras:
        words.extend((p.get("text", "") if isinstance(p, dict) else str(p)).split())
    if not words:
        return 0.0
    return total_chars / len(words)


def abw_consonant_to_vowel_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of consonants to vowels. 0.0 if no vowels."""
    text = _all_text(file_path)
    vowels = sum(1 for c in text if c in VOWELS)
    consonants = sum(1 for c in text if c in CONSONANTS)
    if not vowels:
        return 0.0
    return consonants / vowels


def abw_empty_paragraph_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of empty paragraphs to total paragraphs. 0.0 if none."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0.0
    empty = sum(
        1 for p in paras
        if not (p.get("text", "") if isinstance(p, dict) else str(p)).strip()
    )
    return empty / len(paras)


def abw_file_size_bytes(file_path: "str | bytes | Path") -> int:
    """Return file size in bytes. Returns 0 for non-file sources."""
    try:
        return Path(file_path).stat().st_size
    except (TypeError, OSError):
        return 0


def abw_has_multiple_paragraphs(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has more than one paragraph."""
    return load(file_path).get("paragraph_count", 0) > 1


def abw_has_punctuation(file_path: "str | bytes | Path") -> bool:
    """Return True if any paragraph contains punctuation characters."""
    import string
    return any(c in string.punctuation for c in _all_text(file_path))


def abw_has_single_paragraph(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has exactly one paragraph."""
    return load(file_path).get("paragraph_count", 0) == 1


def abw_letter_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of letter characters to total characters. 0.0 if empty."""
    return abw_alpha_ratio(file_path)


def abw_longest_paragraph_chars(file_path: "str | bytes | Path") -> int:
    """Return character count of the longest paragraph."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0
    return max(
        len(p.get("text", "") if isinstance(p, dict) else str(p))
        for p in paras
    )


def abw_max_paragraph_word_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum word count across all paragraphs."""
    import re
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0
    return max(
        len(re.findall(r"\b\w+\b", p.get("text", "") if isinstance(p, dict) else str(p)))
        for p in paras
    )


def abw_shortest_paragraph_chars(file_path: "str | bytes | Path") -> int:
    """Return character count of the shortest paragraph."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0
    return min(
        len(p.get("text", "") if isinstance(p, dict) else str(p))
        for p in paras
    )


def abw_vowel_count(file_path: "str | bytes | Path") -> int:
    """Return count of vowel characters across all paragraphs."""
    return sum(1 for c in _all_text(file_path) if c in VOWELS)


def abw_vowel_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of vowels to total characters (including spaces/punctuation). 0.0 if empty."""
    text = _all_text(file_path)
    if not text:
        return 0.0
    return sum(1 for c in text if c in VOWELS) / len(text)


def abw_word_length_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of word lengths (split by whitespace). 0.0 if < 2 words."""
    model = load(file_path)
    words = []
    for p in model.get("paragraphs", []):
        words.extend((p.get("text", "") if isinstance(p, dict) else str(p)).split())
    if len(words) < 2:
        return 0.0
    lengths = [len(w) for w in words]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def abw_words_per_char(file_path: "str | bytes | Path") -> float:
    """Return words per character (inverse of chars_per_word). 0.0 if no text."""
    text = _all_text(file_path)
    if not text:
        return 0.0
    words = _all_words(file_path)
    return len(words) / len(text)


def abw_all_words_unique(file_path: "str | bytes | Path") -> bool:
    """Return True if every word in the document appears exactly once."""
    words = [w.lower() for w in _all_words(file_path)]
    if not words:
        return True
    return len(words) == len(set(words))


def abw_avg_word_length_per_para(file_path: "str | bytes | Path") -> float:
    """Return average paragraph character length (trailing punctuation stripped). 0.0 if empty."""
    import string as _string
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0.0
    lengths = [
        len((p.get("text", "") if isinstance(p, dict) else str(p)).rstrip(_string.punctuation))
        for p in paras
    ]
    return sum(lengths) / len(lengths)


def abw_avg_word_per_paragraph(file_path: "str | bytes | Path") -> float:
    """Return average number of words per paragraph."""
    return abw_avg_paragraph_words(file_path)


def abw_capital_word_count(file_path: "str | bytes | Path") -> int:
    """Return count of words that start with a capital letter."""
    import re
    return sum(1 for w in re.findall(r"\b[A-Z]\w*\b", _all_text(file_path)))


def abw_consonant_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of consonants to total letter characters. 0.0 if no letters."""
    text = _all_text(file_path)
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c in CONSONANTS) / len(letters)


def abw_digit_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of digit characters to total characters. 0.0 if empty."""
    text = _all_text(file_path)
    if not text:
        return 0.0
    return sum(1 for c in text if c.isdigit()) / len(text)


def abw_has_multi_para(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has more than one paragraph."""
    return abw_has_multiple_paragraphs(file_path)


def abw_is_empty_document(file_path: "str | bytes | Path") -> bool:
    """Return True if the document has no non-empty paragraphs."""
    return abw_is_empty(file_path)


def abw_lowercase_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of lowercase letters to total letters. 0.0 if no letters."""
    text = _all_text(file_path)
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.islower()) / len(letters)


def abw_max_paragraph_words(file_path: "str | bytes | Path") -> int:
    """Return the maximum word count across all paragraphs."""
    return abw_max_paragraph_word_count(file_path)


def abw_max_word_count_para(file_path: "str | bytes | Path") -> int:
    """Return maximum word count in any single paragraph."""
    return abw_max_paragraph_word_count(file_path)


def abw_short_paragraph_count(file_path: "str | bytes | Path", max_words: int = 2) -> int:
    """Return count of paragraphs with at most max_words words (default 2)."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    return sum(
        1 for p in paras
        if len((p.get("text", "") if isinstance(p, dict) else str(p)).split()) <= max_words
    )


def abw_short_word_count(file_path: "str | bytes | Path") -> int:
    """Return count of words with 3 or fewer characters."""
    return sum(1 for w in _all_words(file_path) if len(w) <= 3)


def abw_space_count(file_path: "str | bytes | Path") -> int:
    """Return count of space characters across all paragraphs."""
    model = load(file_path)
    return sum(
        str(p.get("text", "") if isinstance(p, dict) else p).count(" ")
        for p in model.get("paragraphs", [])
    )


def abw_total_word_length(file_path: "str | bytes | Path") -> int:
    """Return sum of lengths of all words across all paragraphs."""
    return sum(len(w) for w in _all_words(file_path))


def abw_unique_words_per_paragraph(file_path: "str | bytes | Path") -> float:
    """Return global unique word count divided by number of paragraphs. 0.0 if empty."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0.0
    all_words: set = set()
    for p in paras:
        text = p.get("text", "") if isinstance(p, dict) else str(p)
        all_words.update(w.lower() for w in text.split())
    return len(all_words) / len(paras)


def abw_min_word_count_para(file_path: "str | bytes | Path") -> int:
    """Return minimum word count in any single paragraph."""
    import re
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0
    return min(
        len(re.findall(r"\b\w+\b", p.get("text", "") if isinstance(p, dict) else str(p)))
        for p in paras
    )


def abw_numeric_char_count(file_path: "str | bytes | Path") -> int:
    """Return count of numeric (digit) characters. Alias for abw_digit_count."""
    return abw_digit_count(file_path)


def abw_para_char_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of paragraph character lengths. 0.0 if < 2 paragraphs."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if len(paras) < 2:
        return 0.0
    lengths = [len(p.get("text", "") if isinstance(p, dict) else str(p)) for p in paras]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def abw_text_density(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-space characters to total characters. 0.0 if empty."""
    text = _all_text(file_path)
    if not text:
        return 0.0
    return sum(1 for c in text if c != " ") / len(text)


def abw_total_para_char_count(file_path: "str | bytes | Path") -> int:
    """Return total character count across all paragraphs."""
    return sum(
        len(p.get("text", "") if isinstance(p, dict) else str(p))
        for p in load(file_path).get("paragraphs", [])
    )


def abw_uppercase_count(file_path: "str | bytes | Path") -> int:
    """Return count of uppercase letter characters across all paragraphs."""
    return sum(1 for c in _all_text(file_path) if c.isupper())


def abw_digit_char_count(file_path: "str | bytes | Path") -> int:
    """Return count of digit characters. Alias for abw_digit_count."""
    return abw_digit_count(file_path)


def abw_nonempty_para_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty paragraphs to total. 0.0 if none."""
    model = load(file_path)
    paras = model.get("paragraphs", [])
    if not paras:
        return 0.0
    return sum(1 for p in paras if (p.get("text","") if isinstance(p,dict) else str(p)).strip()) / len(paras)


def abw_numeric_word_count(file_path: "str | bytes | Path") -> int:
    """Return count of words that consist entirely of digits."""
    return sum(1 for w in _all_words(file_path) if w.isdigit())


def abw_avg_paragraph_word_count(file_path: "str | bytes | Path") -> float:
    """Return average number of words per paragraph. Same as abw_avg_paragraph_words."""
    return abw_avg_paragraph_words(file_path)


def abw_longest_word_length(file_path: "str | bytes | Path") -> int:
    """Return length of the longest word across all paragraphs. 0 if no words."""
    max_len = 0
    for word in _all_words(file_path):
        if len(word) > max_len:
            max_len = len(word)
    return max_len


def abw_total_sentence_count(file_path: "str | bytes | Path") -> int:
    """Return total count of sentences (split on . ! ?) across all paragraphs."""
    model = load(file_path)
    count = 0
    for para in model.get("paragraphs", []):
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        sentences = re.split(r'[.!?]+', text.strip())
        count += sum(1 for s in sentences if s.strip())
    return count

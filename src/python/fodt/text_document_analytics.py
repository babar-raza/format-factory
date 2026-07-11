"""
fodt_text_document_analytics.py — additional analytics for FODT (split from text_document.py).

Functions accept file_path as first argument, parse the document,
and return a single analytic value.
"""
from __future__ import annotations

import os


def fodt_max_run_count(file_path: "str | os.PathLike[str]") -> int:
    """Return maximum number of text runs in any single block. 0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    counts = [len(b.get("runs", [])) for b in doc.get("blocks", [])]
    return max(counts) if counts else 0


def fodt_numeric_word_count(file_path: "str | os.PathLike[str]") -> int:
    """Return count of words consisting entirely of digits."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            count += sum(1 for w in run.get("text", "").split() if w.isdigit())
    return count


def fodt_heading_char_sum(file_path: "str | os.PathLike[str]") -> int:
    """Return total character count across all heading blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        if block.get("type") == "heading":
            total += sum(len(r.get("text", "")) for r in block.get("runs", []))
    return total


def fodt_paragraph_char_sum(file_path: "str | os.PathLike[str]") -> int:
    """Return total character count across all paragraph blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        if block.get("type") == "paragraph":
            total += sum(len(r.get("text", "")) for r in block.get("runs", []))
    return total


def fodt_max_words_in_heading(file_path: "str | os.PathLike[str]") -> int:
    """Return maximum word count in any single heading block. 0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    counts = []
    for block in doc.get("blocks", []):
        if block.get("type") == "heading":
            wc = sum(len(r.get("text", "").split()) for r in block.get("runs", []))
            counts.append(wc)
    return max(counts) if counts else 0


def fodt_short_paragraph_count(file_path: "str | os.PathLike[str]", max_words: int = 10) -> int:
    """Return count of paragraphs with fewer than max_words words (default 10)."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        if block.get("type") == "paragraph":
            wc = sum(len(r.get("text", "").split()) for r in block.get("runs", []))
            if wc < max_words:
                count += 1
    return count



# ---------------------------------------------------------------------------
# Batch analytics functions -- FF-HEAL-QNAME-20260621-114042 (34 functions)
# Spec refs: FACT-FODT-001, FACT-FODT-013, FACT-FODT-015, FACT-FODT-002
# ---------------------------------------------------------------------------

def _fodt_all_text(doc):
    parts = []
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            parts.append(run.get("text", ""))
    return "".join(parts)


def _fodt_block_text(block):
    return "".join(r.get("text", "") for r in block.get("runs", []))


def fodt_vowel_count(file_path):
    """Return count of vowel characters (aeiouAEIOU) in all text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    vowels = set("aeiouAEIOU")
    return sum(1 for ch in _fodt_all_text(doc) if ch in vowels)


def fodt_space_count(file_path):
    """Return count of space characters in all text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return _fodt_all_text(doc).count(" ")


def fodt_inline_count(file_path):
    """Return count of inline runs carrying a non-None href. 0 for plain text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    count = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            if run.get("href") is not None:
                count += 1
    return count


def fodt_max_block_word_count(file_path):
    """Return maximum word count in any single block. 0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    counts = [len(_fodt_block_text(b).split()) for b in doc.get("blocks", [])]
    return max(counts) if counts else 0


def fodt_punctuation_count(file_path):
    """Return count of punctuation characters in all text."""
    import string
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    punct = set(string.punctuation)
    return sum(1 for ch in _fodt_all_text(doc) if ch in punct)


def fodt_list_block_count(file_path):
    """Return count of list structures in the document."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("lists", []))


def fodt_file_size_bytes(file_path):
    """Return the file size in bytes."""
    import os
    return os.path.getsize(file_path)


def fodt_has_more_words_than_unique(file_path):
    """Return True if total word count exceeds unique word count."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    all_words = []
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            all_words.extend(run.get("text", "").lower().split())
    return len(all_words) > len(set(all_words))


def fodt_all_words_unique(file_path):
    """Return True if all words in the document are unique (case-insensitive)."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    all_words = []
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            all_words.extend(run.get("text", "").lower().split())
    return len(all_words) == len(set(all_words))


def fodt_uppercase_char_count(file_path):
    """Return count of uppercase letters in all text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for ch in _fodt_all_text(doc) if ch.isupper())


def fodt_lowercase_char_count(file_path):
    """Return count of lowercase letters in all text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for ch in _fodt_all_text(doc) if ch.islower())


def fodt_uppercase_ratio(file_path):
    """Return ratio of uppercase letters to total characters. 0.0 if no text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    text = _fodt_all_text(doc)
    if not text:
        return 0.0
    return sum(1 for ch in text if ch.isupper()) / len(text)


def fodt_min_heading_length(file_path):
    """Return minimum character length of any heading. 0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = [len(_fodt_block_text(b)) for b in doc.get("blocks", []) if b.get("type") == "heading"]
    return min(lengths) if lengths else 0


def fodt_char_per_word(file_path):
    """Return average characters per word. 0.0 if no words."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    all_words = []
    char_sum = 0
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            words = run.get("text", "").split()
            all_words.extend(words)
            char_sum += sum(len(w) for w in words)
    return char_sum / len(all_words) if all_words else 0.0


def fodt_avg_block_length(file_path):
    """Return average character length of blocks. 0.0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    if not blocks:
        return 0.0
    return sum(len(_fodt_block_text(b)) for b in blocks) / len(blocks)


def fodt_max_block_text_length(file_path):
    """Return maximum character length of any block. 0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = [len(_fodt_block_text(b)) for b in doc.get("blocks", [])]
    return max(lengths) if lengths else 0


def fodt_min_block_text_length(file_path):
    """Return minimum character length of any block. 0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    lengths = [len(_fodt_block_text(b)) for b in doc.get("blocks", [])]
    return min(lengths) if lengths else 0


def fodt_word_per_heading(file_path):
    """Return average words per heading block. 0.0 if no headings."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    heading_blocks = [b for b in doc.get("blocks", []) if b.get("type") == "heading"]
    if not heading_blocks:
        return 0.0
    total_heading_words = sum(len(_fodt_block_text(b).split()) for b in heading_blocks)
    return total_heading_words / len(heading_blocks)


def fodt_block_text_sum(file_path):
    """Return total character count across all block texts."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(len(_fodt_block_text(b)) for b in doc.get("blocks", []))


def fodt_consonant_ratio(file_path):
    """Return ratio of consonant letters to total letters. 0.0 if no letters."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    vowels = set("aeiouAEIOU")
    total = 0
    consonants = 0
    for ch in _fodt_all_text(doc):
        if ch.isalpha():
            total += 1
            if ch not in vowels:
                consonants += 1
    return consonants / total if total > 0 else 0.0


def fodt_avg_run_count(file_path):
    """Return average number of runs per block. 0.0 if no blocks."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    if not blocks:
        return 0.0
    return sum(len(b.get("runs", [])) for b in blocks) / len(blocks)


def fodt_empty_block_count(file_path):
    """Return count of blocks with no text content."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for b in doc.get("blocks", []) if len(_fodt_block_text(b).strip()) == 0)


def fodt_has_multiple_block_types(file_path):
    """Return True if document has more than one distinct block type."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    types = set(b.get("type") for b in doc.get("blocks", []))
    return len(types) > 1


def fodt_punctuation_density(file_path):
    """Return ratio of punctuation characters to unique (stripped) word count. 0.0 if no words."""
    import string
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    block_texts = [_fodt_block_text(b) for b in doc.get("blocks", [])]
    text = " ".join(block_texts)
    words = text.split()
    if not words:
        return 0.0
    punct = set(string.punctuation)
    punct_count = sum(1 for ch in text if ch in punct)
    unique_stripped = set(w.lower().strip(string.punctuation) for w in words)
    return punct_count / len(unique_stripped) if unique_stripped else 0.0


def fodt_total_character_count(file_path):
    """Return total character count across all run texts."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(_fodt_all_text(doc))


def fodt_avg_word_length(file_path):
    """Return average word length in characters. 0.0 if no words."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    all_words = []
    for block in doc.get("blocks", []):
        for run in block.get("runs", []):
            all_words.extend(run.get("text", "").split())
    if not all_words:
        return 0.0
    return sum(len(w) for w in all_words) / len(all_words)


def fodt_block_type_count(file_path):
    """Return count of distinct block types in the document."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(set(b.get("type", "unknown") for b in doc.get("blocks", [])))


def fodt_nonempty_block_count(file_path):
    """Return count of blocks with at least one word of text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for b in doc.get("blocks", []) if len(_fodt_block_text(b).split()) > 0)


def fodt_is_text_only(file_path):
    """Return True if document has no tables and no lists."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("tables", [])) == 0 and len(doc.get("lists", [])) == 0


def fodt_total_content_blocks(file_path):
    """Return total count of blocks, tables, and lists in the document."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(doc.get("blocks", [])) + len(doc.get("tables", [])) + len(doc.get("lists", []))


def fodt_avg_word_count_per_paragraph(file_path):
    """Return total word count across all blocks divided by paragraph block count. 0.0 if no paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    para_count = sum(1 for b in blocks if b.get("type") == "paragraph")
    if para_count == 0:
        return 0.0
    total_words = sum(len(_fodt_block_text(b).split()) for b in blocks)
    return total_words / para_count


def fodt_word_density(file_path):
    """Return ratio of total words to paragraph character count. 0.0 if no paragraph characters."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    total_words = sum(len(_fodt_block_text(b).split()) for b in blocks)
    para_chars = sum(len(_fodt_block_text(b)) for b in blocks if b.get("type") == "paragraph")
    return total_words / para_chars if para_chars > 0 else 0.0


def fodt_avg_paragraph_length(file_path):
    """Return average character length of paragraph-type blocks. 0.0 if no paragraphs."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    paras = [b for b in doc.get("blocks", []) if b.get("type") == "paragraph"]
    if not paras:
        return 0.0
    return sum(len(_fodt_block_text(p)) for p in paras) / len(paras)


def fodt_unique_block_type_count(file_path):
    """Return count of distinct block types in the document."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return len(set(b.get("type", "unknown") for b in doc.get("blocks", [])))


def fodt_section_depth_max(file_path):
    """Return max nesting depth of text sections. 0 for typical documents without text:section elements."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    # text:section elements are tracked separately in sections key if available
    sections = doc.get("sections", [])
    if not sections:
        return 0
    return max((s.get("depth", 0) for s in sections), default=0)


def fodt_text_block_ratio(file_path):
    """Return ratio of text blocks (paragraph + heading) to total blocks. 1.0 if all blocks are text."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    if not blocks:
        return 0.0
    text_types = {"paragraph", "heading"}
    text_count = sum(1 for b in blocks if b.get("type") in text_types)
    return text_count / len(blocks)


def fodt_word_count_total(file_path: "str | os.PathLike[str]") -> int:
    """Return total word count across all text blocks in a FODT file."""
    from .parser import parse_fodt_strict
    import re as _re
    doc = parse_fodt_strict(file_path)
    total = 0
    for block in doc.get("blocks", []):
        text = block.get("text", "")
        total += len(_re.findall(r"\b\w+\b", text))
    return total


def fodt_paragraph_count_total(file_path: "str | os.PathLike[str]") -> int:
    """Return total count of paragraph blocks in a FODT file."""
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return sum(1 for b in doc.get("blocks", []) if b.get("type") == "paragraph")


def fodt_has_content(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if any block has non-empty text content.

    Spec: FODT text:p element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return any(b.get("text", "").strip() for b in doc.get("blocks", []))


def fodt_first_block_type(file_path: "str | os.PathLike[str]") -> str:
    """Return the type of the first block ('heading' or 'paragraph'). '' if no blocks.

    Spec: FODT text:h / text:p element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    return blocks[0].get("type", "") if blocks else ""


def fodt_first_block_text(file_path: "str | os.PathLike[str]") -> str:
    """Return the text of the first block. Empty string if no blocks.

    Spec: FODT text:p element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    return blocks[0].get("text", "") if blocks else ""


def fodt_heading_texts(file_path: "str | os.PathLike[str]") -> list:
    """Return list of text strings from all heading blocks in order.

    Spec: FODT text:h element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return [b.get("text", "") for b in doc.get("blocks", []) if b.get("type") == "heading"]


def fodt_paragraph_texts(file_path: "str | os.PathLike[str]") -> list:
    """Return list of text strings from all paragraph blocks in order.

    Spec: FODT text:p element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    return [b.get("text", "") for b in doc.get("blocks", []) if b.get("type") == "paragraph"]


def fodt_all_blocks_have_text(file_path: "str | os.PathLike[str]") -> bool:
    """Return True if every block has non-empty text. True vacuously if no blocks.

    Spec: FODT text:p / text:h element (FACT-FODT-001)
    """
    from .parser import parse_fodt_strict
    doc = parse_fodt_strict(file_path)
    blocks = doc.get("blocks", [])
    return all(b.get("text", "").strip() for b in blocks)

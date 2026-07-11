"""ABW word statistics and text query functions.

Derived analytics and query operations on ABW neutral model dicts.
These functions operate on already-parsed model data and perform no I/O.

spec_concept: AbiWord document paragraph/word statistics
"""
from __future__ import annotations


def word_frequency(model: dict) -> dict:
    """Return a dict mapping each word (lowercased) to its count."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    freq: dict = {}
    for para in model.get("paragraphs", []):
        for word in para.lower().split():
            freq[word] = freq.get(word, 0) + 1
    return freq


def get_unique_words(model: dict) -> list:
    """Return sorted list of unique lowercased words across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    words: set = set()
    for para in model.get("paragraphs", []):
        for word in para.lower().split():
            words.add(word)
    return sorted(words)


def get_char_count(model: dict) -> int:
    """Return total character count across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sum(len(p) for p in model.get("paragraphs", []))


def paragraph_lengths(model: dict) -> list:
    """Return a list of character lengths for each paragraph."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return [len(p) for p in model.get("paragraphs", [])]


def count_words(model: dict) -> int:
    """Return total word count across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sum(len(p.split()) for p in model.get("paragraphs", []))


def text_stats(model: dict) -> dict:
    """Return text statistics for the document model.

    Returns a dict with:
        paragraph_count (int): Number of paragraphs.
        word_count (int): Total words across all paragraphs.
        char_count (int): Total characters across all paragraphs.
        avg_words_per_paragraph (float): Average words per paragraph (0.0 if none).

    Args:
        model: ABW neutral model dict (must have 'paragraphs' key).

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    paragraph_count = len(paragraphs)
    word_count = sum(len(p.split()) for p in paragraphs)
    char_count = sum(len(p) for p in paragraphs)
    avg_words = word_count / paragraph_count if paragraph_count else 0.0
    return {
        "paragraph_count": paragraph_count,
        "word_count": word_count,
        "char_count": char_count,
        "avg_words_per_paragraph": avg_words,
    }


def search_text(model: dict, query: str) -> list[int]:
    """Return list of paragraph indices where query string appears.

    Case-sensitive search over all paragraphs in the model.

    Args:
        model: ABW neutral model dict (must have 'paragraphs' key).
        query: String to search for (case-sensitive).

    Returns:
        Sorted list of zero-based paragraph indices containing query.
        Empty list if query is empty or no matches found.
    """
    if not isinstance(model, dict):
        return []
    if not query:
        return []
    paragraphs = model.get("paragraphs", [])
    return [i for i, p in enumerate(paragraphs) if query in p]


def get_words(model: dict, para_idx: int) -> list[str]:
    """Return the whitespace-tokenized words from a specific paragraph.

    Args:
        model: ABW neutral model dict (must have 'paragraphs' key).
        para_idx: Zero-based paragraph index.

    Returns:
        List of word strings from the paragraph. Returns [] for invalid index,
        non-dict model, or empty paragraph.
    """
    if not isinstance(model, dict):
        return []
    paragraphs = model.get("paragraphs", [])
    if para_idx < 0 or para_idx >= len(paragraphs):
        return []
    text = paragraphs[para_idx]
    if not text or not text.strip():
        return []
    return text.split()


def longest_paragraph(model: dict) -> str:
    """Return the longest paragraph text from the ABW model.

    Args:
        model: ABW neutral model dict (from load or parse_abw).

    Returns:
        The paragraph with the greatest character length. Returns empty string
        if the model has no paragraphs.
    """
    if not isinstance(model, dict):
        return ""
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return ""
    texts = [p if isinstance(p, str) else str(p) for p in paragraphs]
    return max(texts, key=len)


def is_empty(model: dict) -> bool:
    """Return True if the ABW model has no content (no paragraphs or all empty).

    Args:
        model: ABW neutral model dict.

    Returns:
        True if model has no paragraphs or all paragraphs are empty/whitespace.
        False if any paragraph contains non-whitespace content.
    """
    if not isinstance(model, dict):
        return True
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return True
    return all(not (p.strip() if isinstance(p, str) else str(p).strip()) for p in paragraphs)


def average_paragraph_length(model: dict) -> float:
    """Return the average character length of paragraphs in the ABW model.

    Args:
        model: ABW neutral model dict.

    Returns:
        Average paragraph length in characters. Returns 0.0 for empty models.
    """
    if not isinstance(model, dict):
        return 0.0
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return 0.0
    lengths = [len(p) if isinstance(p, str) else len(str(p)) for p in paragraphs]
    return sum(lengths) / len(lengths)


def shortest_paragraph(model: dict) -> str:
    """Return the shortest paragraph text from the ABW model.

    If multiple paragraphs have the same minimum length, returns the first one.

    Args:
        model: ABW neutral model dict.

    Returns:
        The shortest paragraph string, or '' for empty models.
    """
    if not isinstance(model, dict):
        return ""
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return ""
    texts = [p if isinstance(p, str) else str(p) for p in paragraphs]
    return min(texts, key=len)


def contains_text(model: dict, text: str, case_sensitive: bool = True) -> bool:
    """Return True if any paragraph contains text as a substring.

    Unlike has_paragraph (exact match), this performs substring search.

    Args:
        model: ABW neutral model dict.
        text: The substring to search for.
        case_sensitive: If False, search is case-insensitive. Default True.

    Returns:
        True if any paragraph contains text, False otherwise.
    """
    if not isinstance(model, dict):
        return False
    search = text if case_sensitive else text.lower()
    for para in model.get("paragraphs", []):
        para_str = para if isinstance(para, str) else str(para)
        haystack = para_str if case_sensitive else para_str.lower()
        if search in haystack:
            return True
    return False


def count_paragraphs_matching(model: dict, pattern: str, case_sensitive: bool = True) -> int:
    """Count how many paragraphs contain pattern as a substring.

    Args:
        model: ABW neutral model dict (from load_abw or parse_abw_bytes).
        pattern: Substring to search for within each paragraph.
        case_sensitive: If False, comparison is case-insensitive. Default True.

    Returns:
        Integer count of paragraphs containing pattern. 0 if model is invalid
        or no paragraphs match.
    """
    if not isinstance(model, dict):
        return 0
    search = pattern if case_sensitive else pattern.lower()
    count = 0
    for para in model.get("paragraphs", []):
        para_str = para if isinstance(para, str) else str(para)
        haystack = para_str if case_sensitive else para_str.lower()
        if search in haystack:
            count += 1
    return count


def has_paragraphs(model: dict) -> bool:
    """Return True if the model contains at least one paragraph.

    Args:
        model: ABW neutral model dict.

    Returns:
        bool — True if paragraph_count > 0.
    """
    if not isinstance(model, dict):
        return False
    return len(model.get("paragraphs", [])) > 0


def first_paragraph(model: dict) -> str:
    """Return the first paragraph text, or empty string if none.

    Args:
        model: ABW neutral model dict.

    Returns:
        str — first paragraph text, or ''.
    """
    if not isinstance(model, dict):
        return ""
    paras = model.get("paragraphs", [])
    return paras[0] if paras else ""


def last_paragraph(model: dict) -> str:
    """Return the last paragraph text, or empty string if none.

    Args:
        model: ABW neutral model dict.

    Returns:
        str — last paragraph text, or ''.
    """
    if not isinstance(model, dict):
        return ""
    paras = model.get("paragraphs", [])
    return paras[-1] if paras else ""


def unique_word_count(model: dict) -> int:
    """Return count of distinct lowercased words across all paragraphs.

    Args:
        model: ABW neutral model dict.

    Returns:
        int — number of unique words.
    """
    if not isinstance(model, dict):
        return 0
    words: set = set()
    for para in model.get("paragraphs", []):
        for word in para.lower().split():
            words.add(word)
    return len(words)


def all_paragraphs_nonempty(model: dict) -> bool:
    """Return True if every paragraph is non-empty (non-whitespace).

    True vacuously when there are no paragraphs.

    Args:
        model: ABW neutral model dict.

    Returns:
        bool — True if all paragraphs have non-whitespace content.
    """
    if not isinstance(model, dict):
        return True
    return all(p.strip() for p in model.get("paragraphs", []))


def total_sentence_count(model: dict) -> int:
    """Return approximate total sentence count across all paragraphs.

    Counts sentence-ending punctuation (., !, ?) as sentence boundaries.
    May overcount for abbreviations or undercount for missing punctuation.

    Args:
        model: ABW neutral model dict.

    Returns:
        int — estimated sentence count. 0 if no paragraphs or no sentences.
    """
    if not isinstance(model, dict):
        return 0
    count = 0
    for para in model.get("paragraphs", []):
        count += para.count(".") + para.count("!") + para.count("?")
    return count

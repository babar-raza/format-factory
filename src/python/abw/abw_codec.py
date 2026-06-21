"""
ABW codec — minimal AbiWord document API.

AbiWord (.abw) — plain XML AWML 1.0 format.
Uses xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false

Security note: DOCTYPE declarations are stripped before parsing.
The DTD at http://www.abisource.com/awml.dtd is unreachable (server down),
and ElementTree does not resolve external DTDs anyway (XXE-safe).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ABW_ROOT_TAG = "abiword"
ABW_MIME = "application/x-abiword"

# Maximum file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024


class AbwError(Exception):
    """Base exception for ABW codec errors."""


class AbwParseError(AbwError):
    """Raised when ABW parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse an ABW document.

    The returned model contains:
        is_abw (bool): True if valid AbiWord document.
        section_count (int): Number of <section> elements.
        paragraph_count (int): Number of <p> elements.
        paragraphs (list[str]): Text content of each paragraph.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Parsed document model dict.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    xml_bytes = _read_source(source)
    clean = _strip_doctype(xml_bytes)
    root = _parse_xml(clean)
    return _build_model(root)


def get_section_count(source: str | bytes | Path) -> int:
    """Return number of sections."""
    return load(source)["section_count"]


def get_paragraph_count(source: str | bytes | Path) -> int:
    """Return total paragraph count."""
    return load(source)["paragraph_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all non-empty paragraph texts."""
    model = load(source)
    return [p for p in model.get("paragraphs", []) if p]


def create_abw(paragraphs: list[str]) -> dict[str, Any]:
    """Create a minimal ABW document model from a list of paragraph strings.

    Args:
        paragraphs: List of paragraph text strings (may be empty).

    Returns:
        Document model dict compatible with write_abw().
    """
    return {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": len(paragraphs),
        "paragraphs": list(paragraphs),
    }


def write_abw(model: dict[str, Any], dest: str | Path) -> None:
    """Serialize an ABW document model to an .abw file.

    Writes a well-formed AWML 1.0 XML file.  The DOCTYPE declaration is
    intentionally omitted (the DTD server at abisource.com is unreachable).

    Args:
        model: Document model dict as returned by load() or create_abw().
        dest:  Destination file path.

    Raises:
        AbwError: If model is invalid or dest cannot be written.
    """
    if not isinstance(model, dict) or not model.get("is_abw"):
        raise AbwError("model must be a valid ABW document dict (is_abw=True)")

    dest = Path(dest)
    paragraphs = model.get("paragraphs", [])

    root = ET.Element(
        ABW_ROOT_TAG,
        attrib={
            "template": "false",
            "styles": "unlocked",
            "version": "1.0",
            "fileformat": "1.0",
        },
    )
    section = ET.SubElement(root, "section")
    for text in paragraphs:
        p = ET.SubElement(section, "p")
        p.text = str(text)

    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n"

    try:
        dest.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise AbwError(f"Cannot write {dest}: {exc}") from exc


def export_to_txt(source: str | bytes | Path) -> str:
    """Export an ABW document to plain text.

    Extracts all paragraph texts and joins them with newlines.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Plain text string with paragraphs joined by newlines.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    model = load(source)
    paragraphs = model.get("paragraphs", [])
    return "\n".join(paragraphs)


def export_to_html(source: str | bytes | Path) -> str:
    """Export an ABW document to a minimal HTML string.

    Wraps each paragraph in an HTML ``<p>`` element.  Returns a complete
    ``<html><body>`` document suitable for display or downstream processing.
    Special characters (<, >, &, ") are escaped.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        HTML string with one ``<p>`` per paragraph.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    _HTML_ESCAPE = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})
    model = load(source)
    paragraphs = model.get("paragraphs", [])
    lines = ["<!DOCTYPE html>", "<html>", "<body>"]
    for para in paragraphs:
        lines.append(f"<p>{para.translate(_HTML_ESCAPE)}</p>")
    lines += ["</body>", "</html>"]
    return "\n".join(lines)


def get_metadata(source: str | bytes | Path) -> dict[str, Any]:
    """Extract document metadata from an ABW file.

    Reads ``<meta>`` elements inside the ``<metadata>`` block (if present).
    Common keys include ``dc.title``, ``dc.creator``, ``dc.description``,
    and ``abiword.date_last_changed``.

    Returns an empty dict when no metadata block is present (e.g. documents
    created by :func:`create_abw`).

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Dict mapping meta key strings to value strings.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    xml_bytes = _read_source(source)
    clean = _strip_doctype(xml_bytes)
    root = _parse_xml(clean)
    meta: dict[str, str] = {}
    for meta_block in root.iter("metadata"):
        for m in meta_block:
            key = m.get("key") or m.tag
            value = m.get("value") or (m.text or "")
            if key:
                meta[key] = value
    return meta


def probe_abw(source) -> bool:
    """Probe whether source is a valid ABW (AbiWord) document.

    Checks for the abiword root element without full parsing.
    Does not raise on malformed input - returns False instead.

    Args:
        source: Path to a file, bytes, or XML string to probe.

    Returns:
        True if source appears to be an ABW document, False otherwise.
    """
    try:
        raw = _read_source(source)
        snippet = raw[:4096].decode("utf-8", errors="replace")
        snippet_stripped = _strip_doctype(snippet.encode())
        # ABW files start with optional XML declaration, then <abiword ...>
        return "<abiword" in snippet_stripped
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_source(source: str | bytes | Path) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str) and not source.strip().startswith("<") and not source.strip().startswith("<?"):
        path = Path(source)
        _check_size(path)
        return path.read_bytes()
    elif isinstance(source, str):
        return source.encode("utf-8")
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise AbwError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise AbwError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise AbwParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise AbwError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _strip_doctype(xml_bytes: bytes) -> str:
    """Strip DOCTYPE declaration to avoid DTD resolution attempts."""
    xml_str = xml_bytes.decode("utf-8", errors="replace")
    lines = xml_str.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("<!DOCTYPE")]
    return "\n".join(filtered)


def _parse_xml(xml_str: str) -> ET.Element:
    """Parse XML string safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_str)
    except ET.ParseError as exc:
        raise AbwParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a document model from the parsed XML root."""
    if root.tag != ABW_ROOT_TAG:
        raise AbwParseError(
            f"Root element must be 'abiword', got {root.tag!r}"
        )

    sections = list(root.iter("section"))
    paragraphs = []
    for p in root.iter("p"):
        text = "".join(p.itertext()).strip()
        paragraphs.append(text)

    return {
        "is_abw": True,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }


# ---------------------------------------------------------------------------
# Sprint 2 additions (R130)
# ---------------------------------------------------------------------------

def search_paragraph(model: dict, query: str, *, case_sensitive: bool = True) -> list:
    """Return indices of paragraphs containing query string."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(query, str):
        raise TypeError("query must be a str")
    paragraphs = model.get("paragraphs", [])
    if case_sensitive:
        return [i for i, p in enumerate(paragraphs) if query in p]
    q = query.lower()
    return [i for i, p in enumerate(paragraphs) if q in p.lower()]


def get_word_count(model: dict) -> int:
    """Return total word count across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sum(len(p.split()) for p in model.get("paragraphs", []))


def search_replace_paragraph(
    model: dict, old: str, new: str, *, case_sensitive: bool = True
) -> dict:
    """Replace all occurrences of old with new in all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(old, str):
        raise TypeError("old must be a str")
    if not isinstance(new, str):
        raise TypeError("new must be a str")
    if not old:
        return {**model, "paragraphs": list(model.get("paragraphs", []))}
    paragraphs = model.get("paragraphs", [])
    if case_sensitive:
        new_paras = [p.replace(old, new) for p in paragraphs]
    else:
        import re
        new_paras = [re.sub(re.escape(old), new, p, flags=re.IGNORECASE) for p in paragraphs]
    return {**model, "paragraphs": new_paras, "paragraph_count": len(new_paras)}


def get_paragraph(model: dict, index: int) -> str:
    """Return paragraph at index. Raises IndexError if out of range."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    if index < 0 or index >= len(paragraphs):
        raise IndexError(f"paragraph index {index} out of range")
    return paragraphs[index]


# ---------------------------------------------------------------------------
# Sprint 3 additions (R135) — export_to_json, edit_paragraph, export_to_csv
# ---------------------------------------------------------------------------

def export_to_json(source) -> str:
    """Export an ABW document to a JSON string.

    Loads the document from source and returns a JSON object with the model fields.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        JSON string representation of the document model.
    """
    import json as _json
    model = load(source)
    return _json.dumps(
        {
            "is_abw": model.get("is_abw", True),
            "section_count": model.get("section_count", 0),
            "paragraph_count": model.get("paragraph_count", 0),
            "paragraphs": model.get("paragraphs", []),
        },
        ensure_ascii=True,
        indent=2,
    )


def edit_paragraph(model: dict, index: int, text: str) -> dict:
    """Return a new model with the paragraph at index replaced by text.

    Args:
        model: ABW document model dict.
        index: Zero-based paragraph index.
        text:  Replacement text.

    Raises:
        IndexError: If index is out of range.
        TypeError:  If model is not a dict or text is not a str.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    paragraphs = model.get("paragraphs", [])
    if index < 0 or index >= len(paragraphs):
        raise IndexError(f"paragraph index {index} out of range")
    new_paras = list(paragraphs)
    new_paras[index] = text
    return {**model, "paragraphs": new_paras, "paragraph_count": len(new_paras)}


def export_to_csv(source) -> str:
    """Export an ABW document to a CSV string.

    Each paragraph is a row with a single 'text' column.

    Args:
        source: Path, bytes, or XML string.

    Returns:
        CSV string with header 'text' and one row per paragraph.
    """
    model = load(source)
    paragraphs = model.get("paragraphs", [])
    lines = ["text"]
    for para in paragraphs:
        escaped = para.replace('"', '""')
        if "," in escaped or '"' in para or "\n" in para or "\r" in para:
            lines.append(f'"{escaped}"')
        else:
            lines.append(escaped)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Sprint 4 additions (R136-R137)
# ---------------------------------------------------------------------------

def merge_abw(a: dict, b: dict) -> dict:
    """Merge two ABW document models by concatenating their paragraphs."""
    if not isinstance(a, dict):
        raise TypeError("a must be a dict")
    if not isinstance(b, dict):
        raise TypeError("b must be a dict")
    combined = list(a.get("paragraphs", [])) + list(b.get("paragraphs", []))
    return {**a, "paragraphs": combined, "paragraph_count": len(combined)}


def word_frequency(model: dict) -> dict:
    """Return a dict mapping each word (lowercased) to its count."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    freq: dict = {}
    for para in model.get("paragraphs", []):
        for word in para.lower().split():
            freq[word] = freq.get(word, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# Sprint 5 additions (R138)
# ---------------------------------------------------------------------------

def truncate_paragraphs(model: dict, n: int) -> dict:
    """Return a new model with at most n paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if n < 0:
        raise ValueError("n must be >= 0")
    paragraphs = list(model.get("paragraphs", []))[:n]
    return {**model, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


def get_unique_words(model: dict) -> list:
    """Return sorted list of unique lowercased words across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    words: set = set()
    for para in model.get("paragraphs", []):
        for word in para.lower().split():
            words.add(word)
    return sorted(words)


# ---------------------------------------------------------------------------
# Sprint 6 additions (R140)
# ---------------------------------------------------------------------------

def append_paragraph(model: dict, text: str) -> dict:
    """Return a new model with text appended as a new paragraph."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    paragraphs = list(model.get("paragraphs", [])) + [text]
    return {**model, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


def split_paragraphs(model: dict, chunk_size: int) -> list:
    """Split the model into sub-models of chunk_size paragraphs each."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    paragraphs = model.get("paragraphs", [])
    if not paragraphs:
        return [{**model, "paragraphs": [], "paragraph_count": 0}]
    chunks = []
    for i in range(0, len(paragraphs), chunk_size):
        chunk = list(paragraphs[i : i + chunk_size])
        chunks.append({**model, "paragraphs": chunk, "paragraph_count": len(chunk)})
    return chunks


# ---------------------------------------------------------------------------
# Sprint 7 additions (R142)
# ---------------------------------------------------------------------------

def get_char_count(model: dict) -> int:
    """Return total character count across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sum(len(p) for p in model.get("paragraphs", []))


def join_paragraphs(model: dict, sep: str = "\n") -> str:
    """Join all paragraphs with sep and return as a single string."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sep.join(model.get("paragraphs", []))


def replace_in_paragraphs(model: dict, old: str, new: str) -> dict:
    """Return a new model with all occurrences of old replaced by new."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    if not isinstance(old, str):
        raise TypeError("old must be a str")
    if not isinstance(new, str):
        raise TypeError("new must be a str")
    paragraphs = [p.replace(old, new) for p in model.get("paragraphs", [])]
    return {**model, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


# ---------------------------------------------------------------------------
# Sprint 8 additions (R144)
# ---------------------------------------------------------------------------

def export_to_markdown(model: dict) -> str:
    """Export document paragraphs as Markdown text (paragraphs separated by blank lines)."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return "\n\n".join(model.get("paragraphs", []))


def get_paragraph_at(model: dict, index: int) -> str:
    """Return paragraph at index. Does NOT accept negative indices.

    Raises IndexError if index is out of range or negative.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    if index < 0 or index >= len(paragraphs):
        raise IndexError(f"paragraph index {index} out of range")
    return paragraphs[index]


# ---------------------------------------------------------------------------
# Sprint 9 additions (R146)
# ---------------------------------------------------------------------------

def paragraph_lengths(model: dict) -> list:
    """Return a list of character lengths for each paragraph."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return [len(p) for p in model.get("paragraphs", [])]


def reverse_paragraphs(model: dict) -> dict:
    """Return a new model with paragraphs in reversed order."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = list(reversed(model.get("paragraphs", [])))
    return {**model, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


# ---------------------------------------------------------------------------
# Sprint 10 additions (R148)
# ---------------------------------------------------------------------------

def word_wrap(model: dict, width: int) -> dict:
    """Wrap long paragraphs at word boundaries to fit within width characters.

    Each paragraph that exceeds width is split into multiple shorter paragraphs.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    import textwrap
    result_paras: list = []
    for para in model.get("paragraphs", []):
        if len(para) <= width:
            result_paras.append(para)
        else:
            wrapped = textwrap.wrap(para, width)
            result_paras.extend(wrapped if wrapped else [para])
    return {**model, "paragraphs": result_paras, "paragraph_count": len(result_paras)}


def has_paragraph(model: dict, text: str) -> bool:
    """Return True if any paragraph exactly matches text."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return text in model.get("paragraphs", [])


# ---------------------------------------------------------------------------
# Sprint 11 additions (R150)
# ---------------------------------------------------------------------------

def first_paragraph(model: dict) -> str:
    """Return the first paragraph, or '' if the document is empty."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    return paragraphs[0] if paragraphs else ""


def last_paragraph(model: dict) -> str:
    """Return the last paragraph, or '' if the document is empty."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    return paragraphs[-1] if paragraphs else ""


# ---------------------------------------------------------------------------
# Sprint 12 additions (R152)
# ---------------------------------------------------------------------------

def count_words(model: dict) -> int:
    """Return total word count across all paragraphs."""
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    return sum(len(p.split()) for p in model.get("paragraphs", []))


def paragraph_at(model: dict, index: int) -> str:
    """Return paragraph at index. Supports negative indices.

    Raises IndexError if index is out of range.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    if not paragraphs or index >= len(paragraphs) or index < -len(paragraphs):
        raise IndexError(f"paragraph index {index} out of range")
    return paragraphs[index]


# pfgi-rnext — text_stats
# FORMAT_FACTORY_EXECUTION: taskcard=PFGI-TC-005; method=MANUAL_GOVERNED_BY_SKILL; skill=add-python-api; idempotency=dccee3ccbb0b816812baaa43930a298729c24fbad552eec09f21873a74a12a3b; evidence=.local/evidences/product-first-governed-implementation-rnext/evidence-declaration.yaml
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


# pige-rnext — export_to_plain_text
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-005; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=634e6b842d83c862f52513443a3f2830944efa8c2e0676c8e751900edb6045a9; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def export_to_plain_text(model: dict) -> str:
    """Export all paragraphs as a single plain-text string.

    Paragraphs are joined with double newlines.

    Args:
        model: ABW neutral model dict (must have 'paragraphs' key).

    Returns:
        Plain text string with paragraphs separated by blank lines.

    Raises:
        TypeError: If model is not a dict.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    paragraphs = model.get("paragraphs", [])
    return "\n\n".join(paragraphs)


# FORMAT_FACTORY_EXECUTION: taskcard=SHQ-L2-001; method=QUEUE_DISPATCHED_EXECUTION; queue_item=anl-q-001; sprint_id=FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
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


# FORMAT_FACTORY_EXECUTION: taskcard=PD-Q-003; method=QUEUE_DISPATCHED_EXECUTION; queue_item=pdrnext-q-003
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


# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-004

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

    Performs substring search across all paragraphs in the ABW neutral model.

    Args:
        model: ABW neutral model dict (from load_abw or parse_abw_bytes).
        pattern: Substring to search for within each paragraph.
        case_sensitive: If False, comparison is case-insensitive. Default True.

    Returns:
        Integer count of paragraphs containing pattern. 0 if model is invalid
        or no paragraphs match.

    Sprint: FORMAT-FACTORY-PRODUCT-ADVANCE-GOVERNANCE-DURABILITY-001
    Authority: QUEUE_DISPATCHED_EXECUTION
    spec_fact_refs: ABW-FOSS-LOAD-001
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


# Analytics functions are in abw_analytics.py to keep this file within policy limits.
try:
    from .abw_analytics import *  # noqa: F401, F403
except ImportError:
    pass


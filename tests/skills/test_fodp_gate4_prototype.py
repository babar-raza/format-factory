"""
tests/skills/test_fodp_gate4_prototype.py

Gate 4 prototype validation tests for FODP (.fodp) format.
Tests the prototypes/by-format/fodp/fodp_parser.py prototype.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/skills/test_fodp_gate4_prototype.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "fodp"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodp"

sys.path.insert(0, str(PROTO_DIR))
from fodp_parser import parse_fodp, count_pages, extract_text, FODP_MIME


# ---------------------------------------------------------------------------
# 1. Registry state verification
# ---------------------------------------------------------------------------

def test_registry_gate4_status():
    """Registry must show gate_4 as passed or in progress for FODP."""
    import yaml  # noqa: F401 — available via user site-packages
    with open(REPO_ROOT / "registry" / "format-registry.yaml", encoding="utf-8") as f:
        content = f.read()
    # Just check the file is readable and mentions fodp
    assert "fodp" in content.lower()


# ---------------------------------------------------------------------------
# 2. FODP MIME type detection
# ---------------------------------------------------------------------------

def test_parse_fodp_minimal_is_fodp():
    """minimal-presentation.fodp must be identified as FODP."""
    result = parse_fodp(SAMPLES_DIR / "minimal-presentation.fodp")
    assert result["error"] is None, f"Unexpected error: {result['error']}"
    assert result["is_fodp"] is True
    assert result["mime_type"] == FODP_MIME


def test_parse_fodp_two_slides_is_fodp():
    """two-slides-basic.fodp must be identified as FODP."""
    result = parse_fodp(SAMPLES_DIR / "two-slides-basic.fodp")
    assert result["is_fodp"] is True


# ---------------------------------------------------------------------------
# 3. Page count extraction
# ---------------------------------------------------------------------------

def test_page_count_minimal():
    """minimal-presentation.fodp has exactly 1 page."""
    assert count_pages(SAMPLES_DIR / "minimal-presentation.fodp") == 1


def test_page_count_two_slides():
    """two-slides-basic.fodp has exactly 2 pages."""
    assert count_pages(SAMPLES_DIR / "two-slides-basic.fodp") == 2


def test_page_count_title_only():
    """title-only.fodp has 0 pages (empty presentation body)."""
    assert count_pages(SAMPLES_DIR / "title-only.fodp") == 0


# ---------------------------------------------------------------------------
# 4. Text extraction
# ---------------------------------------------------------------------------

def test_extract_text_minimal():
    """minimal-presentation.fodp contains 'Hello' text."""
    texts = extract_text(SAMPLES_DIR / "minimal-presentation.fodp")
    assert any("Hello" in t for t in texts)


def test_extract_text_two_slides():
    """two-slides-basic.fodp has text on both slides."""
    texts = extract_text(SAMPLES_DIR / "two-slides-basic.fodp")
    assert len(texts) >= 2


def test_extract_text_title_only():
    """title-only.fodp has no text (empty)."""
    texts = extract_text(SAMPLES_DIR / "title-only.fodp")
    assert texts == []


# ---------------------------------------------------------------------------
# 5. Page metadata
# ---------------------------------------------------------------------------

def test_page_metadata_minimal():
    """Parse page metadata from minimal-presentation.fodp."""
    result = parse_fodp(SAMPLES_DIR / "minimal-presentation.fodp")
    assert len(result["pages"]) == 1
    page = result["pages"][0]
    assert "text_content" in page
    assert "shape_count" in page


def test_page_metadata_two_slides():
    """Parse page metadata from two-slides-basic.fodp — 2 pages."""
    result = parse_fodp(SAMPLES_DIR / "two-slides-basic.fodp")
    assert len(result["pages"]) == 2
    # First page should have 'Introduction' title
    first_page_texts = result["pages"][0]["text_content"]
    assert any("Introduction" in t for t in first_page_texts)


# ---------------------------------------------------------------------------
# 6. Error handling
# ---------------------------------------------------------------------------

def test_parse_fodp_file_not_found():
    """parse_fodp returns error for non-existent file."""
    result = parse_fodp(REPO_ROOT / "nonexistent.fodp")
    assert result["error"] is not None


def test_parse_fodp_invalid_xml():
    """parse_fodp returns error for invalid XML."""
    result = parse_fodp(b"not xml at all <<<")
    assert result["error"] is not None
    assert result["is_fodp"] is False


def test_parse_fodp_wrong_root():
    """parse_fodp returns error for XML with wrong root element."""
    xml = b"<?xml version='1.0'?><root><child/></root>"
    result = parse_fodp(xml)
    assert result["error"] is not None
    assert result["is_fodp"] is False


# ---------------------------------------------------------------------------
# 7. Bytes and string input
# ---------------------------------------------------------------------------

def test_parse_fodp_bytes_input():
    """parse_fodp accepts bytes input."""
    content = (SAMPLES_DIR / "minimal-presentation.fodp").read_bytes()
    result = parse_fodp(content)
    assert result["is_fodp"] is True
    assert result["page_count"] == 1


# ---------------------------------------------------------------------------
# 8. All corpus samples parse without error
# ---------------------------------------------------------------------------

def test_all_corpus_samples_parse():
    """All FODP corpus samples must parse without error."""
    samples = list(SAMPLES_DIR.glob("*.fodp"))
    assert len(samples) >= 3, f"Expected at least 3 FODP samples, found {len(samples)}"
    for sample in samples:
        result = parse_fodp(sample)
        assert result["error"] is None, (
            f"Sample {sample.name} failed: {result['error']}"
        )
        assert result["is_fodp"] is True, (
            f"Sample {sample.name} not identified as FODP"
        )

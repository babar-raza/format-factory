"""
Tests for src/python/fodp/fodp_codec.py

FODP FOSS track. No external dependencies required.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/fodp/ -v
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodp"

from fodp.fodp_codec import (
    FodpError,
    FodpParseError,
    FODP_MIME,
    load,
    get_page_count,
    extract_text,
    get_page_metadata,
)


# ---------------------------------------------------------------------------
# 1. load() — basic
# ---------------------------------------------------------------------------

def test_load_minimal_returns_model():
    """load() returns a model dict for minimal-presentation.fodp."""
    model = load(SAMPLES_DIR / "minimal-presentation.fodp")
    assert isinstance(model, dict)
    assert model["is_fodp"] is True
    assert model["page_count"] == 1


def test_load_two_slides():
    """load() returns 2 pages for two-slides-basic.fodp."""
    model = load(SAMPLES_DIR / "two-slides-basic.fodp")
    assert model["page_count"] == 2


def test_load_title_only():
    """title-only.fodp has 0 pages."""
    model = load(SAMPLES_DIR / "title-only.fodp")
    assert model["page_count"] == 0


def test_load_accepts_bytes():
    """load() accepts bytes input."""
    data = (SAMPLES_DIR / "minimal-presentation.fodp").read_bytes()
    model = load(data)
    assert model["is_fodp"] is True


def test_load_all_corpus_samples():
    """All FODP corpus samples load without error."""
    for path in sorted(SAMPLES_DIR.glob("*.fodp")):
        model = load(path)
        assert model["is_fodp"] is True, f"{path.name} not FODP"
        assert "pages" in model


# ---------------------------------------------------------------------------
# 2. load() — errors
# ---------------------------------------------------------------------------

def test_load_missing_file_raises():
    """load() raises FodpParseError for missing file."""
    with pytest.raises(FodpParseError):
        load(REPO_ROOT / "nonexistent.fodp")


def test_load_invalid_xml_raises():
    """load() raises FodpParseError for invalid XML."""
    with pytest.raises(FodpParseError):
        load(b"<not valid xml <<<<<")


def test_load_wrong_root_raises():
    """load() raises FodpParseError for XML with wrong root."""
    with pytest.raises(FodpParseError):
        load(b"<?xml version='1.0'?><root/>")


# ---------------------------------------------------------------------------
# 3. get_page_count()
# ---------------------------------------------------------------------------

def test_get_page_count_minimal():
    assert get_page_count(SAMPLES_DIR / "minimal-presentation.fodp") == 1


def test_get_page_count_two_slides():
    assert get_page_count(SAMPLES_DIR / "two-slides-basic.fodp") == 2


def test_get_page_count_empty():
    assert get_page_count(SAMPLES_DIR / "title-only.fodp") == 0


# ---------------------------------------------------------------------------
# 4. extract_text()
# ---------------------------------------------------------------------------

def test_extract_text_minimal():
    """extract_text returns 'Hello' from minimal presentation."""
    texts = extract_text(SAMPLES_DIR / "minimal-presentation.fodp")
    assert any("Hello" in t for t in texts)


def test_extract_text_two_slides():
    """extract_text returns text from both slides."""
    texts = extract_text(SAMPLES_DIR / "two-slides-basic.fodp")
    assert len(texts) >= 2


def test_extract_text_empty():
    """extract_text returns empty list for empty presentation."""
    texts = extract_text(SAMPLES_DIR / "title-only.fodp")
    assert texts == []


# ---------------------------------------------------------------------------
# 5. get_page_metadata()
# ---------------------------------------------------------------------------

def test_get_page_metadata_structure():
    """get_page_metadata returns list with expected keys."""
    pages = get_page_metadata(SAMPLES_DIR / "minimal-presentation.fodp")
    assert len(pages) == 1
    page = pages[0]
    assert "name" in page
    assert "text_content" in page
    assert "shape_count" in page
    assert "title" in page


def test_get_page_metadata_two_slides_titles():
    """First slide of two-slides-basic.fodp has 'Introduction' in text."""
    pages = get_page_metadata(SAMPLES_DIR / "two-slides-basic.fodp")
    assert len(pages) == 2
    first_texts = pages[0]["text_content"]
    assert any("Introduction" in t for t in first_texts)

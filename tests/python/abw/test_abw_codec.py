"""
Tests for src/python/abw/abw_codec.py

ABW FOSS track. No external dependencies required.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/abw/ -v
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "abw"

from abw.abw_codec import (
    AbwError,
    AbwParseError,
    ABW_MIME,
    load,
    get_section_count,
    get_paragraph_count,
    extract_text,
)


# ---------------------------------------------------------------------------
# 1. load() — basic
# ---------------------------------------------------------------------------

def test_load_minimal_returns_model():
    """load() returns a model dict for minimal-document.abw."""
    model = load(SAMPLES_DIR / "minimal-document.abw")
    assert isinstance(model, dict)
    assert model["is_abw"] is True
    assert model["paragraph_count"] == 1


def test_load_two_paragraphs():
    """load() returns 2 paragraphs for two-paragraphs.abw."""
    model = load(SAMPLES_DIR / "two-paragraphs.abw")
    assert model["paragraph_count"] == 2


def test_load_empty_section():
    """empty-section.abw has 1 section and 0 paragraphs."""
    model = load(SAMPLES_DIR / "empty-section.abw")
    assert model["section_count"] == 1
    assert model["paragraph_count"] == 0


def test_load_accepts_bytes():
    """load() accepts bytes input."""
    data = (SAMPLES_DIR / "minimal-document.abw").read_bytes()
    model = load(data)
    assert model["is_abw"] is True


def test_load_all_corpus_samples():
    """All ABW corpus samples load without error."""
    for path in sorted(SAMPLES_DIR.glob("*.abw")):
        model = load(path)
        assert model["is_abw"] is True, f"{path.name} not ABW"
        assert "paragraphs" in model


# ---------------------------------------------------------------------------
# 2. load() — errors
# ---------------------------------------------------------------------------

def test_load_missing_file_raises():
    """load() raises AbwParseError for missing file."""
    with pytest.raises(AbwParseError):
        load(REPO_ROOT / "nonexistent.abw")


def test_load_invalid_xml_raises():
    """load() raises AbwParseError for invalid XML."""
    with pytest.raises(AbwParseError):
        load(b"<not valid xml <<<<<")


def test_load_wrong_root_raises():
    """load() raises AbwParseError for XML with wrong root."""
    with pytest.raises(AbwParseError):
        load(b"<?xml version='1.0'?><root/>")


# ---------------------------------------------------------------------------
# 3. get_section_count()
# ---------------------------------------------------------------------------

def test_get_section_count_minimal():
    assert get_section_count(SAMPLES_DIR / "minimal-document.abw") == 1


def test_get_section_count_empty():
    assert get_section_count(SAMPLES_DIR / "empty-section.abw") == 1


# ---------------------------------------------------------------------------
# 4. get_paragraph_count()
# ---------------------------------------------------------------------------

def test_get_paragraph_count_minimal():
    assert get_paragraph_count(SAMPLES_DIR / "minimal-document.abw") == 1


def test_get_paragraph_count_two():
    assert get_paragraph_count(SAMPLES_DIR / "two-paragraphs.abw") == 2


def test_get_paragraph_count_empty():
    assert get_paragraph_count(SAMPLES_DIR / "empty-section.abw") == 0


# ---------------------------------------------------------------------------
# 5. extract_text()
# ---------------------------------------------------------------------------

def test_extract_text_minimal():
    """minimal-document.abw contains 'Hello' text."""
    texts = extract_text(SAMPLES_DIR / "minimal-document.abw")
    assert any("Hello" in t for t in texts)


def test_extract_text_two_paragraphs():
    """two-paragraphs.abw returns text from both paragraphs."""
    texts = extract_text(SAMPLES_DIR / "two-paragraphs.abw")
    assert len(texts) >= 2


def test_extract_text_empty():
    """empty-section.abw returns empty list."""
    texts = extract_text(SAMPLES_DIR / "empty-section.abw")
    assert texts == []


# ---------------------------------------------------------------------------
# 6. MIME type constant
# ---------------------------------------------------------------------------

def test_mime_type_constant():
    assert ABW_MIME == "application/x-abiword"

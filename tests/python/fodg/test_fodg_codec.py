"""
Tests for src/python/fodg/fodg_codec.py

FODG FOSS track. No external dependencies required.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/fodg/ -v
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodg"

from fodg.fodg_codec import (
    FodgError,
    FodgParseError,
    FODG_MIME,
    load,
    get_page_count,
    get_shape_count,
    extract_text,
    get_page_metadata,
)


# ---------------------------------------------------------------------------
# 1. load() — basic
# ---------------------------------------------------------------------------

def test_load_minimal_returns_model():
    """load() returns a model dict for minimal-drawing.fodg."""
    model = load(SAMPLES_DIR / "minimal-drawing.fodg")
    assert isinstance(model, dict)
    assert model["is_fodg"] is True
    assert model["page_count"] == 1


def test_load_shapes_basic():
    """load() returns 1 page for shapes-basic.fodg."""
    model = load(SAMPLES_DIR / "shapes-basic.fodg")
    assert model["page_count"] == 1


def test_load_empty_page():
    """empty-page.fodg has 1 page with 0 shapes."""
    model = load(SAMPLES_DIR / "empty-page.fodg")
    assert model["page_count"] == 1
    assert model["shapes_total"] == 0


def test_load_accepts_bytes():
    """load() accepts bytes input."""
    data = (SAMPLES_DIR / "minimal-drawing.fodg").read_bytes()
    model = load(data)
    assert model["is_fodg"] is True


def test_load_all_corpus_samples():
    """All FODG corpus samples load without error."""
    for path in sorted(SAMPLES_DIR.glob("*.fodg")):
        model = load(path)
        assert model["is_fodg"] is True, f"{path.name} not FODG"
        assert "pages" in model


# ---------------------------------------------------------------------------
# 2. load() — errors
# ---------------------------------------------------------------------------

def test_load_missing_file_raises():
    """load() raises FodgParseError for missing file."""
    with pytest.raises(FodgParseError):
        load(REPO_ROOT / "nonexistent.fodg")


def test_load_invalid_xml_raises():
    """load() raises FodgParseError for invalid XML."""
    with pytest.raises(FodgParseError):
        load(b"<not valid xml <<<<<")


def test_load_wrong_root_raises():
    """load() raises FodgParseError for XML with wrong root."""
    with pytest.raises(FodgParseError):
        load(b"<?xml version='1.0'?><root/>")


# ---------------------------------------------------------------------------
# 3. get_page_count()
# ---------------------------------------------------------------------------

def test_get_page_count_minimal():
    model = load(SAMPLES_DIR / "minimal-drawing.fodg")
    assert get_page_count(model) == 1


def test_get_page_count_shapes_basic():
    model = load(SAMPLES_DIR / "shapes-basic.fodg")
    assert get_page_count(model) == 1


def test_get_page_count_empty():
    model = load(SAMPLES_DIR / "empty-page.fodg")
    assert get_page_count(model) == 1


# ---------------------------------------------------------------------------
# 4. get_shape_count()
# ---------------------------------------------------------------------------

def test_get_shape_count_minimal():
    """minimal-drawing.fodg has 1 shape."""
    assert get_shape_count(SAMPLES_DIR / "minimal-drawing.fodg") == 1


def test_get_shape_count_shapes_basic():
    """shapes-basic.fodg has 3 shapes (rect, ellipse, line)."""
    assert get_shape_count(SAMPLES_DIR / "shapes-basic.fodg") == 3


def test_get_shape_count_empty():
    """empty-page.fodg has 0 shapes."""
    assert get_shape_count(SAMPLES_DIR / "empty-page.fodg") == 0


# ---------------------------------------------------------------------------
# 5. extract_text()
# ---------------------------------------------------------------------------

def test_extract_text_empty():
    """extract_text returns empty list for empty drawing."""
    texts = extract_text(SAMPLES_DIR / "empty-page.fodg")
    assert texts == []


# ---------------------------------------------------------------------------
# 6. get_page_metadata()
# ---------------------------------------------------------------------------

def test_get_page_metadata_structure():
    """get_page_metadata returns list with expected keys."""
    pages = get_page_metadata(SAMPLES_DIR / "minimal-drawing.fodg")
    assert len(pages) == 1
    page = pages[0]
    assert "name" in page
    assert "text_content" in page
    assert "shape_count" in page


def test_get_page_metadata_shapes_basic():
    """shapes-basic.fodg has 1 page with 3 shapes."""
    pages = get_page_metadata(SAMPLES_DIR / "shapes-basic.fodg")
    assert len(pages) == 1
    assert pages[0]["shape_count"] == 3


# ---------------------------------------------------------------------------
# 7. MIME type
# ---------------------------------------------------------------------------

def test_mime_type_constant():
    assert FODG_MIME == "application/vnd.oasis.opendocument.graphics-flat-xml"


def test_load_mime_type():
    model = load(SAMPLES_DIR / "minimal-drawing.fodg")
    assert model["mime_type"] == FODG_MIME

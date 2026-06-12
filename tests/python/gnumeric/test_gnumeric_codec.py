"""
Tests for src/python/gnumeric/gnumeric_codec.py

Gnumeric FOSS track. No external dependencies required.

Run from repo root:
    PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages \
        python -m pytest tests/python/gnumeric/ -v
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    GnumericParseError,
    load,
    get_sheet_count,
    get_cell_count,
    extract_values,
    get_sheet_metadata,
)


# ---------------------------------------------------------------------------
# 1. load() — basic
# ---------------------------------------------------------------------------

def test_load_minimal_returns_model():
    """load() returns a model dict for minimal-spreadsheet.gnumeric."""
    model = load(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert isinstance(model, dict)
    assert model["is_gnumeric"] is True
    assert model["sheet_count"] == 1


def test_load_multi_cell():
    """load() returns 1 sheet for multi-cell-basic.gnumeric."""
    model = load(SAMPLES_DIR / "multi-cell-basic.gnumeric")
    assert model["sheet_count"] == 1
    assert model["cell_count"] == 4


def test_load_empty_sheet():
    """empty-sheet.gnumeric has 1 sheet with 0 cells."""
    model = load(SAMPLES_DIR / "empty-sheet.gnumeric")
    assert model["sheet_count"] == 1
    assert model["cell_count"] == 0


def test_load_all_corpus_samples():
    """All Gnumeric corpus samples load without error."""
    for path in sorted(SAMPLES_DIR.glob("*.gnumeric")):
        model = load(path)
        assert model["is_gnumeric"] is True, f"{path.name} not Gnumeric"
        assert "sheets" in model


# ---------------------------------------------------------------------------
# 2. load() — errors
# ---------------------------------------------------------------------------

def test_load_missing_file_raises():
    """load() raises GnumericParseError for missing file."""
    with pytest.raises(GnumericParseError):
        load(REPO_ROOT / "nonexistent.gnumeric")


def test_load_invalid_bytes_raises():
    """load() raises GnumericParseError for invalid bytes."""
    with pytest.raises(GnumericParseError):
        load(b"not gzip and not xml <<<<<")


def test_load_wrong_root_raises():
    """load() raises GnumericParseError for XML with wrong root."""
    with pytest.raises(GnumericParseError):
        load(b"<?xml version='1.0'?><root/>")


# ---------------------------------------------------------------------------
# 3. get_sheet_count()
# ---------------------------------------------------------------------------

def test_get_sheet_count_minimal():
    assert get_sheet_count(SAMPLES_DIR / "minimal-spreadsheet.gnumeric") == 1


def test_get_sheet_count_empty():
    assert get_sheet_count(SAMPLES_DIR / "empty-sheet.gnumeric") == 1


# ---------------------------------------------------------------------------
# 4. get_cell_count()
# ---------------------------------------------------------------------------

def test_get_cell_count_minimal():
    assert get_cell_count(SAMPLES_DIR / "minimal-spreadsheet.gnumeric") == 1


def test_get_cell_count_multi_cell():
    assert get_cell_count(SAMPLES_DIR / "multi-cell-basic.gnumeric") == 4


def test_get_cell_count_empty():
    assert get_cell_count(SAMPLES_DIR / "empty-sheet.gnumeric") == 0


# ---------------------------------------------------------------------------
# 5. extract_values()
# ---------------------------------------------------------------------------

def test_extract_values_minimal():
    """minimal-spreadsheet.gnumeric has 'Hello' cell value."""
    values = extract_values(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert any("Hello" in v for v in values)


def test_extract_values_empty():
    """empty-sheet.gnumeric has no cell values."""
    values = extract_values(SAMPLES_DIR / "empty-sheet.gnumeric")
    assert values == []


# ---------------------------------------------------------------------------
# 6. get_sheet_metadata()
# ---------------------------------------------------------------------------

def test_get_sheet_metadata_structure():
    """get_sheet_metadata returns list with expected keys."""
    sheets = get_sheet_metadata(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert len(sheets) == 1
    sheet = sheets[0]
    assert "name" in sheet
    assert "cell_count" in sheet
    assert "cell_values" in sheet


def test_get_sheet_metadata_name():
    """Sheet name is extracted correctly."""
    sheets = get_sheet_metadata(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert sheets[0]["name"] == "Sheet1"

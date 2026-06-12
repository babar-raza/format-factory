"""
tests/skills/test_gnumeric_gate4_prototype.py

Gate 4 prototype validation tests for Gnumeric (.gnumeric) format.
Tests the prototypes/by-format/gnumeric/gnumeric_parser.py prototype.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTO_DIR = REPO_ROOT / "prototypes" / "by-format" / "gnumeric"
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "gnumeric"

sys.path.insert(0, str(PROTO_DIR))
from gnumeric_parser import parse_gnumeric, count_sheets, get_cell_count, extract_values


def test_parse_gnumeric_minimal_is_gnumeric():
    """minimal-spreadsheet.gnumeric must be identified as Gnumeric."""
    result = parse_gnumeric(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert result["error"] is None, f"Unexpected error: {result['error']}"
    assert result["is_gnumeric"] is True


def test_sheet_count_minimal():
    """minimal-spreadsheet.gnumeric has 1 sheet."""
    assert count_sheets(SAMPLES_DIR / "minimal-spreadsheet.gnumeric") == 1


def test_sheet_count_empty():
    """empty-sheet.gnumeric has 1 sheet."""
    assert count_sheets(SAMPLES_DIR / "empty-sheet.gnumeric") == 1


def test_cell_count_minimal():
    """minimal-spreadsheet.gnumeric has 1 cell."""
    assert get_cell_count(SAMPLES_DIR / "minimal-spreadsheet.gnumeric") == 1


def test_cell_count_multi_cell():
    """multi-cell-basic.gnumeric has 4 cells."""
    assert get_cell_count(SAMPLES_DIR / "multi-cell-basic.gnumeric") == 4


def test_cell_count_empty():
    """empty-sheet.gnumeric has 0 cells."""
    assert get_cell_count(SAMPLES_DIR / "empty-sheet.gnumeric") == 0


def test_extract_values_minimal():
    """minimal-spreadsheet.gnumeric has 'Hello' cell value."""
    values = extract_values(SAMPLES_DIR / "minimal-spreadsheet.gnumeric")
    assert any("Hello" in v for v in values)


def test_extract_values_multi_cell():
    """multi-cell-basic.gnumeric has Name/Score/Alice/42 values."""
    values = extract_values(SAMPLES_DIR / "multi-cell-basic.gnumeric")
    assert len(values) >= 3
    all_text = " ".join(values)
    assert "Name" in all_text or "Alice" in all_text


def test_extract_values_empty():
    """empty-sheet.gnumeric has no cell values."""
    values = extract_values(SAMPLES_DIR / "empty-sheet.gnumeric")
    assert values == []


def test_parse_gnumeric_file_not_found():
    result = parse_gnumeric(REPO_ROOT / "nonexistent.gnumeric")
    assert result["error"] is not None


def test_parse_gnumeric_invalid_bytes():
    result = parse_gnumeric(b"not gzip and not xml <<<<<")
    assert result["error"] is not None
    assert result["is_gnumeric"] is False


def test_parse_gnumeric_wrong_root():
    result = parse_gnumeric(b"<?xml version='1.0'?><root/>")
    assert result["error"] is not None


def test_all_corpus_samples_parse():
    """All Gnumeric corpus samples parse without error."""
    samples = list(SAMPLES_DIR.glob("*.gnumeric"))
    assert len(samples) >= 3
    for sample in samples:
        result = parse_gnumeric(sample)
        assert result["error"] is None, f"{sample.name}: {result['error']}"
        assert result["is_gnumeric"] is True

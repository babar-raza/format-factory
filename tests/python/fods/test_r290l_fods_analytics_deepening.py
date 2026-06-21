"""Tests for FODS analytics deepening (R290L): avg_cell_text_length, sheet_cell_variance, total_string_cell_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import (
    fods_avg_cell_text_length,
    fods_sheet_cell_variance,
    fods_total_string_cell_count,
)
from fods.parser import parse_fods_strict

SAMPLES = _REPO / "samples" / "by-format" / "fods"


def _load(name: str) -> dict:
    return parse_fods_strict(SAMPLES / name)


def test_avg_cell_text_length_returns_float():
    wb = _load("minimal-spreadsheet.fods")
    result = fods_avg_cell_text_length(wb)
    assert isinstance(result, float)
    assert result >= 0.0


def test_avg_cell_text_length_multi_sheet():
    wb = _load("multi-sheet-basic.fods")
    result = fods_avg_cell_text_length(wb)
    assert isinstance(result, float)


def test_sheet_cell_variance_single_sheet():
    wb = _load("minimal-spreadsheet.fods")
    result = fods_sheet_cell_variance(wb)
    assert result == 0.0  # single sheet has no variance


def test_sheet_cell_variance_multi_sheet():
    wb = _load("multi-sheet-basic.fods")
    result = fods_sheet_cell_variance(wb)
    assert isinstance(result, float)
    assert result >= 0.0


def test_total_string_cell_count_returns_int():
    wb = _load("typed-values-basic.fods")
    result = fods_total_string_cell_count(wb)
    assert isinstance(result, int)
    assert result >= 0


def test_total_string_cell_count_minimal():
    wb = _load("minimal-spreadsheet.fods")
    result = fods_total_string_cell_count(wb)
    assert isinstance(result, int)

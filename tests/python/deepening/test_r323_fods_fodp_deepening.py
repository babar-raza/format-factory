"""Tests for fods_empty_cell_percentage, fods_string_cell_percentage,
fodp_text_density, fodp_unique_word_ratio (Sprint 113, R323).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_empty_cell_percentage, fods_string_cell_percentage
from src.python.fods import parse_fods_strict
from src.python.fodp.fodp_codec import fodp_text_density, fodp_unique_word_ratio

FODS = _REPO / "samples" / "by-format" / "fods"
FODP = _REPO / "samples" / "by-format" / "fodp"


def _wb(name):
    return parse_fods_strict(FODS / name)


def test_fods_empty_pct_minimal():
    assert abs(fods_empty_cell_percentage(_wb("minimal-spreadsheet.fods")) - 0.0) < 0.1


def test_fods_empty_pct_multi():
    assert abs(fods_empty_cell_percentage(_wb("multi-sheet-basic.fods")) - 0.0) < 0.1


def test_fods_empty_pct_typed():
    assert abs(fods_empty_cell_percentage(_wb("typed-values-basic.fods")) - 0.0) < 0.1


def test_fods_empty_pct_returns_float():
    assert isinstance(fods_empty_cell_percentage(_wb("minimal-spreadsheet.fods")), float)


def test_fods_empty_pct_nonnegative():
    assert fods_empty_cell_percentage(_wb("minimal-spreadsheet.fods")) >= 0.0


def test_fods_string_pct_minimal():
    assert abs(fods_string_cell_percentage(_wb("minimal-spreadsheet.fods")) - 100.0) < 0.1


def test_fods_string_pct_multi():
    assert abs(fods_string_cell_percentage(_wb("multi-sheet-basic.fods")) - 100.0) < 0.1


def test_fods_string_pct_typed():
    assert abs(fods_string_cell_percentage(_wb("typed-values-basic.fods")) - 75.0) < 0.1


def test_fods_string_pct_returns_float():
    assert isinstance(fods_string_cell_percentage(_wb("minimal-spreadsheet.fods")), float)


def test_fods_string_pct_nonnegative():
    assert fods_string_cell_percentage(_wb("minimal-spreadsheet.fods")) >= 0.0


def test_fodp_text_density_minimal():
    assert abs(fodp_text_density(FODP / "minimal-presentation.fodp") - 5.0) < 0.01


def test_fodp_text_density_two():
    assert abs(fodp_text_density(FODP / "two-slides-basic.fodp") - 21.5) < 0.01


def test_fodp_text_density_title():
    assert abs(fodp_text_density(FODP / "title-only.fodp") - 0.0) < 0.01


def test_fodp_text_density_returns_float():
    assert isinstance(fodp_text_density(FODP / "minimal-presentation.fodp"), float)


def test_fodp_text_density_nonnegative():
    assert fodp_text_density(FODP / "minimal-presentation.fodp") >= 0.0


def test_fodp_unique_ratio_minimal():
    assert abs(fodp_unique_word_ratio(FODP / "minimal-presentation.fodp") - 1.0) < 0.01


def test_fodp_unique_ratio_two():
    assert abs(fodp_unique_word_ratio(FODP / "two-slides-basic.fodp") - 1.0) < 0.01


def test_fodp_unique_ratio_title():
    assert abs(fodp_unique_word_ratio(FODP / "title-only.fodp") - 0.0) < 0.01


def test_fodp_unique_ratio_returns_float():
    assert isinstance(fodp_unique_word_ratio(FODP / "minimal-presentation.fodp"), float)


def test_fodp_unique_ratio_bounded():
    val = fodp_unique_word_ratio(FODP / "minimal-presentation.fodp")
    assert 0.0 <= val <= 1.0

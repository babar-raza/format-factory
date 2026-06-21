"""Sprint 129 deepening – FODS nonempty_cell_percentage/is_empty_spreadsheet, FODP words_per_slide/is_empty_presentation."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_nonempty_cell_percentage, fods_is_empty_spreadsheet
from src.python.fodp.fodp_codec import fodp_words_per_slide, fodp_is_empty_presentation

FODS = _REPO / "samples" / "by-format" / "fods"
FODP = _REPO / "samples" / "by-format" / "fodp"


# --- fods_nonempty_cell_percentage ---

class TestFodsNonemptyCellPercentage:
    def test_minimal(self):
        assert abs(fods_nonempty_cell_percentage(FODS / "minimal-spreadsheet.fods") - 100.0) < 0.01

    def test_multi(self):
        assert abs(fods_nonempty_cell_percentage(FODS / "multi-sheet-basic.fods") - 100.0) < 0.01

    def test_typed(self):
        assert abs(fods_nonempty_cell_percentage(FODS / "typed-values-basic.fods") - 100.0) < 0.01

    def test_returns_float(self):
        assert isinstance(fods_nonempty_cell_percentage(FODS / "minimal-spreadsheet.fods"), float)

    def test_range(self):
        v = fods_nonempty_cell_percentage(FODS / "minimal-spreadsheet.fods")
        assert 0.0 <= v <= 100.0


# --- fods_is_empty_spreadsheet ---

class TestFodsIsEmptySpreadsheet:
    def test_minimal_not_empty(self):
        assert fods_is_empty_spreadsheet(FODS / "minimal-spreadsheet.fods") is False

    def test_multi_not_empty(self):
        assert fods_is_empty_spreadsheet(FODS / "multi-sheet-basic.fods") is False

    def test_typed_not_empty(self):
        assert fods_is_empty_spreadsheet(FODS / "typed-values-basic.fods") is False

    def test_returns_bool(self):
        assert isinstance(fods_is_empty_spreadsheet(FODS / "minimal-spreadsheet.fods"), bool)

    def test_consistency(self):
        empty = fods_is_empty_spreadsheet(FODS / "minimal-spreadsheet.fods")
        pct = fods_nonempty_cell_percentage(FODS / "minimal-spreadsheet.fods")
        if empty:
            assert pct == 0.0


# --- fodp_words_per_slide ---

class TestFodpWordsPerSlide:
    def test_minimal(self):
        assert abs(fodp_words_per_slide(FODP / "minimal-presentation.fodp") - 1.0) < 0.01

    def test_two(self):
        assert abs(fodp_words_per_slide(FODP / "two-slides-basic.fodp") - 2.5) < 0.01

    def test_title_zero(self):
        assert fodp_words_per_slide(FODP / "title-only.fodp") == 0.0

    def test_returns_float(self):
        assert isinstance(fodp_words_per_slide(FODP / "minimal-presentation.fodp"), float)

    def test_non_negative(self):
        assert fodp_words_per_slide(FODP / "minimal-presentation.fodp") >= 0


# --- fodp_is_empty_presentation ---

class TestFodpIsEmptyPresentation:
    def test_minimal_not_empty(self):
        assert fodp_is_empty_presentation(FODP / "minimal-presentation.fodp") is False

    def test_two_not_empty(self):
        assert fodp_is_empty_presentation(FODP / "two-slides-basic.fodp") is False

    def test_title_empty(self):
        assert fodp_is_empty_presentation(FODP / "title-only.fodp") is True

    def test_returns_bool(self):
        assert isinstance(fodp_is_empty_presentation(FODP / "minimal-presentation.fodp"), bool)

    def test_consistency(self):
        empty = fodp_is_empty_presentation(FODP / "title-only.fodp")
        wps = fodp_words_per_slide(FODP / "title-only.fodp")
        if empty:
            assert wps == 0.0

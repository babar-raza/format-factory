"""Tests for 6 new analytics: FODS/FODT/Gnumeric deepening sprint R420."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import (
    fods_sheet_count_squared,
    fods_total_cells_plus_sheet_count,
    fods_sheet_count,
    fods_total_cell_count,
)
from src.python.fods import parse_fods_strict

from src.python.fodt.neutral_model import (
    fodt_block_count_squared,
    fodt_word_count_plus_block_count,
    fodt_block_count,
    fodt_word_count,
)

from src.python.gnumeric.gnumeric_codec import (
    gnumeric_sheet_count_squared,
    gnumeric_total_cells_plus_sheet_count,
    gnumeric_sheet_count,
    gnumeric_total_cell_count,
)

_FODS_SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_GNUMERIC_SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


class TestFodsSheetCountSquared:
    def test_returns_int(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        assert isinstance(fods_sheet_count_squared(wb), int)

    def test_matches_formula(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        sc = fods_sheet_count(wb)
        assert fods_sheet_count_squared(wb) == sc * sc

    def test_positive(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        assert fods_sheet_count_squared(wb) >= 1


class TestFodsTotalCellsPlusSheetCount:
    def test_returns_int(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        assert isinstance(fods_total_cells_plus_sheet_count(wb), int)

    def test_matches_sum(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        assert fods_total_cells_plus_sheet_count(wb) == fods_total_cell_count(wb) + fods_sheet_count(wb)

    def test_positive(self):
        wb = parse_fods_strict(_FODS_SAMPLE)
        assert fods_total_cells_plus_sheet_count(wb) >= 1


class TestFodtBlockCountSquared:
    def test_returns_int(self):
        assert isinstance(fodt_block_count_squared(_FODT_SAMPLE), int)

    def test_matches_formula(self):
        bc = fodt_block_count(_FODT_SAMPLE)
        assert fodt_block_count_squared(_FODT_SAMPLE) == bc * bc

    def test_nonnegative(self):
        assert fodt_block_count_squared(_FODT_SAMPLE) >= 0


class TestFodtWordCountPlusBlockCount:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_plus_block_count(_FODT_SAMPLE), int)

    def test_matches_sum(self):
        wc = fodt_word_count(_FODT_SAMPLE)
        bc = fodt_block_count(_FODT_SAMPLE)
        assert fodt_word_count_plus_block_count(_FODT_SAMPLE) == wc + bc

    def test_nonnegative(self):
        assert fodt_word_count_plus_block_count(_FODT_SAMPLE) >= 0


class TestGnumericSheetCountSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_sheet_count_squared(_GNUMERIC_SAMPLE), int)

    def test_matches_formula(self):
        sc = gnumeric_sheet_count(_GNUMERIC_SAMPLE)
        assert gnumeric_sheet_count_squared(_GNUMERIC_SAMPLE) == sc * sc

    def test_positive(self):
        assert gnumeric_sheet_count_squared(_GNUMERIC_SAMPLE) >= 1


class TestGnumericTotalCellsPlusSheetCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_cells_plus_sheet_count(_GNUMERIC_SAMPLE), int)

    def test_matches_sum(self):
        tc = gnumeric_total_cell_count(_GNUMERIC_SAMPLE)
        sc = gnumeric_sheet_count(_GNUMERIC_SAMPLE)
        assert gnumeric_total_cells_plus_sheet_count(_GNUMERIC_SAMPLE) == tc + sc

    def test_positive(self):
        assert gnumeric_total_cells_plus_sheet_count(_GNUMERIC_SAMPLE) >= 1

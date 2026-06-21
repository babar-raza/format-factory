"""Sprint R437 — FODS/FODT/ODS/ODT/FODP deepening round 5.

Functions under test (10 total, 2 per format):
  FODS: fods_sheet_count_times_two, fods_total_cells_times_two
  FODT: fodt_block_count_times_two, fodt_paragraph_count_times_two
  ODS:  ods_sheet_count_times_two, ods_row_count_times_two
  ODT:  odt_heading_count_times_two, odt_file_size_times_two
  FODP: fodp_shape_count_times_two, fodp_total_text_chars_times_two
"""
import pathlib, sys, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- sample paths ---
_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "title-only.fodp"

# ── FODS ─────────────────────────────────────────────────────────────
from src.python.fods import parse_fods_strict
from src.python.fods.neutral_model import (
    fods_sheet_count,
    fods_total_cell_count,
    fods_sheet_count_times_two,
    fods_total_cells_times_two,
)

def _wb():
    return parse_fods_strict(_FODS)

class TestFodsSheetCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_two(_wb()), int)
    def test_double_of_base(self):
        wb = _wb()
        assert fods_sheet_count_times_two(wb) == fods_sheet_count(wb) * 2
    def test_positive(self):
        assert fods_sheet_count_times_two(_wb()) > 0

class TestFodsTotalCellsTimesTwo:
    def test_returns_int(self):
        assert isinstance(fods_total_cells_times_two(_wb()), int)
    def test_double_of_base(self):
        wb = _wb()
        assert fods_total_cells_times_two(wb) == fods_total_cell_count(wb) * 2
    def test_non_negative(self):
        assert fods_total_cells_times_two(_wb()) >= 0

# ── FODT ─────────────────────────────────────────────────────────────
from src.python.fodt.neutral_model import (
    fodt_block_count,
    fodt_paragraph_count,
    fodt_block_count_times_two,
    fodt_paragraph_count_times_two,
)

class TestFodtBlockCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodt_block_count_times_two(_FODT), int)
    def test_double_of_base(self):
        assert fodt_block_count_times_two(_FODT) == fodt_block_count(_FODT) * 2
    def test_non_negative(self):
        assert fodt_block_count_times_two(_FODT) >= 0

class TestFodtParagraphCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_two(_FODT), int)
    def test_double_of_base(self):
        assert fodt_paragraph_count_times_two(_FODT) == fodt_paragraph_count(_FODT) * 2
    def test_non_negative(self):
        assert fodt_paragraph_count_times_two(_FODT) >= 0

# ── ODS ──────────────────────────────────────────────────────────────
from src.python.ods.ods_parser import (
    ods_sheet_count,
    ods_sheet_count_times_two,
    ods_row_count_times_two,
)

class TestOdsSheetCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_two(_ODS), int)
    def test_double_of_base(self):
        assert ods_sheet_count_times_two(_ODS) == ods_sheet_count(_ODS) * 2
    def test_positive(self):
        assert ods_sheet_count_times_two(_ODS) > 0

class TestOdsRowCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(ods_row_count_times_two(_ODS), int)
    def test_non_negative(self):
        assert ods_row_count_times_two(_ODS) >= 0
    def test_even(self):
        assert ods_row_count_times_two(_ODS) % 2 == 0

# ── ODT ──────────────────────────────────────────────────────────────
from src.python.odt.odt_parser import (
    odt_heading_count,
    odt_file_size_bytes,
    odt_heading_count_times_two,
    odt_file_size_times_two,
)

class TestOdtHeadingCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(odt_heading_count_times_two(_ODT), int)
    def test_double_of_base(self):
        assert odt_heading_count_times_two(_ODT) == odt_heading_count(_ODT) * 2
    def test_non_negative(self):
        assert odt_heading_count_times_two(_ODT) >= 0

class TestOdtFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(odt_file_size_times_two(_ODT), int)
    def test_double_of_base(self):
        assert odt_file_size_times_two(_ODT) == odt_file_size_bytes(_ODT) * 2
    def test_positive(self):
        assert odt_file_size_times_two(_ODT) > 0

# ── FODP ─────────────────────────────────────────────────────────────
from src.python.fodp.fodp_codec import (
    fodp_total_shape_count,
    fodp_total_text_chars,
    fodp_shape_count_times_two,
    fodp_total_text_chars_times_two,
)

class TestFodpShapeCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodp_shape_count_times_two(_FODP), int)
    def test_double_of_base(self):
        assert fodp_shape_count_times_two(_FODP) == fodp_total_shape_count(_FODP) * 2
    def test_non_negative(self):
        assert fodp_shape_count_times_two(_FODP) >= 0

class TestFodpTotalTextCharsTimesTwo:
    def test_returns_int(self):
        assert isinstance(fodp_total_text_chars_times_two(_FODP), int)
    def test_double_of_base(self):
        assert fodp_total_text_chars_times_two(_FODP) == fodp_total_text_chars(_FODP) * 2
    def test_non_negative(self):
        assert fodp_total_text_chars_times_two(_FODP) >= 0

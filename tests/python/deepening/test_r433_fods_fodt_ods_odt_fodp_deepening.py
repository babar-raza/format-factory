"""Sprint R433 — product deepening round 3 for FODS/FODT/ODS/ODT/FODP.

New analytics:
  FODS: fods_numeric_cell_count_squared, fods_string_cell_count_squared
  FODT: fodt_char_count_squared, fodt_heading_count_squared
  ODS:  ods_row_count_squared, ods_cell_count_times_two
  ODT:  odt_char_count_squared, odt_total_word_count_squared
  FODP: fodp_slide_count_times_two, fodp_shape_count_squared
"""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── FODS ─────────────────────────────────────────────────────────────
from src.python.fods.neutral_model import (
    fods_numeric_cell_count_squared,
    fods_string_cell_count_squared,
    fods_numeric_cell_count,
    fods_string_cell_count,
)
from src.python.fods.parser import parse_fods_strict

_FODS = _REPO / "samples" / "by-format" / "fods"


class TestFodsNumericCellCountSquared:
    def test_minimal(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        nc = fods_numeric_cell_count(wb)
        assert fods_numeric_cell_count_squared(wb) == nc * nc

    def test_type(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_numeric_cell_count_squared(wb), int)

    def test_nonneg(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        assert fods_numeric_cell_count_squared(wb) >= 0


class TestFodsStringCellCountSquared:
    def test_minimal(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        sc = fods_string_cell_count(wb)
        assert fods_string_cell_count_squared(wb) == sc * sc

    def test_type(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_string_cell_count_squared(wb), int)

    def test_nonneg(self):
        wb = parse_fods_strict(_FODS / "minimal-spreadsheet.fods")
        assert fods_string_cell_count_squared(wb) >= 0


# ── FODT ─────────────────────────────────────────────────────────────
from src.python.fodt.neutral_model import (
    fodt_char_count_squared,
    fodt_heading_count_squared,
    fodt_total_char_count,
    fodt_heading_count,
)

_FODT = _REPO / "samples" / "by-format" / "fodt"


class TestFodtCharCountSquared:
    def test_minimal(self):
        p = _FODT / "minimal-document.fodt"
        cc = fodt_total_char_count(p)
        assert fodt_char_count_squared(p) == cc * cc

    def test_type(self):
        p = _FODT / "minimal-document.fodt"
        assert isinstance(fodt_char_count_squared(p), int)

    def test_nonneg(self):
        p = _FODT / "minimal-document.fodt"
        assert fodt_char_count_squared(p) >= 0


class TestFodtHeadingCountSquared:
    def test_minimal(self):
        p = _FODT / "minimal-document.fodt"
        hc = fodt_heading_count(p)
        assert fodt_heading_count_squared(p) == hc * hc

    def test_type(self):
        p = _FODT / "minimal-document.fodt"
        assert isinstance(fodt_heading_count_squared(p), int)

    def test_nonneg(self):
        p = _FODT / "minimal-document.fodt"
        assert fodt_heading_count_squared(p) >= 0


# ── ODS ──────────────────────────────────────────────────────────────
from src.python.ods.ods_parser import (
    ods_row_count_squared,
    ods_cell_count_times_two,
    ods_total_row_count,
    ods_total_cells,
)

_ODS = _REPO / "samples" / "by-format" / "ods"


class TestOdsRowCountSquared:
    def test_minimal(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        rc = ods_total_row_count(p)
        assert ods_row_count_squared(p) == rc * rc

    def test_type(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        assert isinstance(ods_row_count_squared(p), int)

    def test_nonneg(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        assert ods_row_count_squared(p) >= 0


class TestOdsCellCountTimesTwo:
    def test_minimal(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        tc = ods_total_cells(p)
        assert ods_cell_count_times_two(p) == tc * 2

    def test_type(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        assert isinstance(ods_cell_count_times_two(p), int)

    def test_nonneg(self):
        p = _ODS / "valid" / "minimal-spreadsheet.ods"
        assert ods_cell_count_times_two(p) >= 0


# ── ODT ──────────────────────────────────────────────────────────────
from src.python.odt.odt_parser import (
    odt_char_count_squared,
    odt_total_word_count_squared,
    odt_total_char_count,
    odt_total_word_count,
)

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtCharCountSquared:
    def test_minimal(self):
        p = _ODT / "minimal-document.odt"
        cc = odt_total_char_count(p)
        assert odt_char_count_squared(p) == cc * cc

    def test_type(self):
        p = _ODT / "minimal-document.odt"
        assert isinstance(odt_char_count_squared(p), int)

    def test_nonneg(self):
        p = _ODT / "minimal-document.odt"
        assert odt_char_count_squared(p) >= 0


class TestOdtTotalWordCountSquared:
    def test_minimal(self):
        p = _ODT / "minimal-document.odt"
        wc = odt_total_word_count(p)
        assert odt_total_word_count_squared(p) == wc * wc

    def test_type(self):
        p = _ODT / "minimal-document.odt"
        assert isinstance(odt_total_word_count_squared(p), int)

    def test_nonneg(self):
        p = _ODT / "minimal-document.odt"
        assert odt_total_word_count_squared(p) >= 0


# ── FODP ─────────────────────────────────────────────────────────────
from src.python.fodp.fodp_codec import (
    fodp_slide_count_times_two,
    fodp_shape_count_squared,
    fodp_slide_count,
    fodp_total_shape_count,
)

_FODP = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideCountTimesTwo:
    def test_minimal(self):
        p = _FODP / "title-only.fodp"
        sc = fodp_slide_count(p)
        assert fodp_slide_count_times_two(p) == sc * 2

    def test_type(self):
        p = _FODP / "title-only.fodp"
        assert isinstance(fodp_slide_count_times_two(p), int)

    def test_nonneg(self):
        p = _FODP / "title-only.fodp"
        assert fodp_slide_count_times_two(p) >= 0


class TestFodpShapeCountSquared:
    def test_minimal(self):
        p = _FODP / "title-only.fodp"
        tc = fodp_total_shape_count(p)
        assert fodp_shape_count_squared(p) == tc * tc

    def test_type(self):
        p = _FODP / "title-only.fodp"
        assert isinstance(fodp_shape_count_squared(p), int)

    def test_nonneg(self):
        p = _FODP / "title-only.fodp"
        assert fodp_shape_count_squared(p) >= 0

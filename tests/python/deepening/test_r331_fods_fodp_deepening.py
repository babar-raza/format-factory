"""Sprint 121 — FODS (fods_bytes_per_cell, fods_bytes_per_sheet)
and FODP (fodp_bytes_per_slide, fodp_chars_per_word).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_bytes_per_cell, fods_bytes_per_sheet
from src.python.fodp.fodp_codec import fodp_bytes_per_slide, fodp_chars_per_word

FODS = _REPO / "samples" / "by-format" / "fods"
FODP = _REPO / "samples" / "by-format" / "fodp"


# ---------- fods_bytes_per_cell ----------

class TestFodsBytesPerCell:
    def test_minimal_value(self):
        assert abs(fods_bytes_per_cell(FODS / "minimal-spreadsheet.fods") - 1421.0) < 0.1

    def test_multi_value(self):
        assert abs(fods_bytes_per_cell(FODS / "multi-sheet-basic.fods") - 401.6) < 0.1

    def test_typed_value(self):
        assert abs(fods_bytes_per_cell(FODS / "typed-values-basic.fods") - 304.375) < 0.1

    def test_returns_float(self):
        assert isinstance(fods_bytes_per_cell(FODS / "minimal-spreadsheet.fods"), float)

    def test_positive(self):
        assert fods_bytes_per_cell(FODS / "minimal-spreadsheet.fods") > 0.0


# ---------- fods_bytes_per_sheet ----------

class TestFodsBytesPerSheet:
    def test_minimal_value(self):
        assert abs(fods_bytes_per_sheet(FODS / "minimal-spreadsheet.fods") - 1421.0) < 0.1

    def test_multi_value(self):
        assert abs(fods_bytes_per_sheet(FODS / "multi-sheet-basic.fods") - 1004.0) < 0.1

    def test_typed_value(self):
        assert abs(fods_bytes_per_sheet(FODS / "typed-values-basic.fods") - 2435.0) < 0.1

    def test_returns_float(self):
        assert isinstance(fods_bytes_per_sheet(FODS / "minimal-spreadsheet.fods"), float)

    def test_positive(self):
        assert fods_bytes_per_sheet(FODS / "multi-sheet-basic.fods") > 0.0


# ---------- fodp_bytes_per_slide ----------

class TestFodpBytesPerSlide:
    def test_minimal_value(self):
        assert abs(fodp_bytes_per_slide(FODP / "minimal-presentation.fodp") - 1713.0) < 0.1

    def test_two_slides_value(self):
        assert abs(fodp_bytes_per_slide(FODP / "two-slides-basic.fodp") - 1120.0) < 0.1

    def test_title_only_value(self):
        assert abs(fodp_bytes_per_slide(FODP / "title-only.fodp") - 0.0) < 0.1

    def test_returns_float(self):
        assert isinstance(fodp_bytes_per_slide(FODP / "minimal-presentation.fodp"), float)

    def test_non_negative(self):
        assert fodp_bytes_per_slide(FODP / "two-slides-basic.fodp") >= 0.0


# ---------- fodp_chars_per_word ----------

class TestFodpCharsPerWord:
    def test_minimal_value(self):
        assert abs(fodp_chars_per_word(FODP / "minimal-presentation.fodp") - 5.0) < 0.01

    def test_two_slides_value(self):
        assert abs(fodp_chars_per_word(FODP / "two-slides-basic.fodp") - 8.6) < 0.01

    def test_title_only_value(self):
        assert abs(fodp_chars_per_word(FODP / "title-only.fodp") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(fodp_chars_per_word(FODP / "minimal-presentation.fodp"), float)

    def test_non_negative(self):
        assert fodp_chars_per_word(FODP / "two-slides-basic.fodp") >= 0.0

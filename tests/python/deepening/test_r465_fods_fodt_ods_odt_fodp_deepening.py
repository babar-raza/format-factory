"""Sprint R465 — FODS/FODT/ODS/ODT/FODP round 13 deepening (_times_five)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.fods import parse_fods_strict, fods_sheet_count_times_five, fods_total_cell_count_times_five
from src.python.fodt import fodt_paragraph_count_times_five, fodt_word_count_times_five
from src.python.ods import ods_sheet_count_times_five, ods_total_cell_count_times_five
from src.python.odt import odt_word_count_times_five, odt_paragraph_count_times_five
from src.python.fodp import fodp_slide_count_times_five, fodp_word_count_times_five


# --- FODS ---
class TestFodsSheetCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert isinstance(fods_sheet_count_times_five(wb), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_sheet_count_times_five(wb) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_sheet_count_times_five(wb) % 5 == 0


class TestFodsTotalCellCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert isinstance(fods_total_cell_count_times_five(wb), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_cell_count_times_five(wb) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_cell_count_times_five(wb) % 5 == 0


# --- FODT ---
class TestFodtParagraphCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_paragraph_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_five(p) % 5 == 0


class TestFodtWordCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_word_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_five(p) % 5 == 0


# --- ODS ---
class TestOdsSheetCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_sheet_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_five(p) % 5 == 0


class TestOdsTotalCellCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_total_cell_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_five(p) % 5 == 0


# --- ODT ---
class TestOdtWordCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_word_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_five(p) % 5 == 0


class TestOdtParagraphCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_paragraph_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_five(p) % 5 == 0


# --- FODP ---
class TestFodpSlideCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_slide_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_five(p) % 5 == 0


class TestFodpWordCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_word_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_five(p) % 5 == 0

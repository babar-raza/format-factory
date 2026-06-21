"""Sprint R469 — FODS/FODT/ODS/ODT/FODP round 14 deepening (_times_six)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.fods import parse_fods_strict, fods_sheet_count_times_six, fods_total_cell_count_times_six
from src.python.fodt import fodt_paragraph_count_times_six, fodt_word_count_times_six
from src.python.ods import ods_sheet_count_times_six, ods_total_cell_count_times_six
from src.python.odt import odt_word_count_times_six, odt_paragraph_count_times_six
from src.python.fodp import fodp_slide_count_times_six, fodp_word_count_times_six


# --- FODS ---
class TestFodsSheetCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert isinstance(fods_sheet_count_times_six(wb), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_sheet_count_times_six(wb) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_sheet_count_times_six(wb) % 6 == 0


class TestFodsTotalCellCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert isinstance(fods_total_cell_count_times_six(wb), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_cell_count_times_six(wb) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
        wb = parse_fods_strict(p)
        assert fods_total_cell_count_times_six(wb) % 6 == 0


# --- FODT ---
class TestFodtParagraphCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_paragraph_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_six(p) % 6 == 0


class TestFodtWordCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_word_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_six(p) % 6 == 0


# --- ODS ---
class TestOdsSheetCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_sheet_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_six(p) % 6 == 0


class TestOdsTotalCellCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_total_cell_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_six(p) % 6 == 0


# --- ODT ---
class TestOdtWordCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_word_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_six(p) % 6 == 0


class TestOdtParagraphCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_paragraph_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_six(p) % 6 == 0


# --- FODP ---
class TestFodpSlideCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_slide_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_six(p) % 6 == 0


class TestFodpWordCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_word_count_times_six(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_six(p) >= 0

    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_six(p) % 6 == 0

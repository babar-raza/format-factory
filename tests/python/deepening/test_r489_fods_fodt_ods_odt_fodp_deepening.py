"""Sprint R489 — FODS/FODT/ODS/ODT/FODP _times_eleven composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_sheet_count_times_eleven, fods_total_cell_count_times_eleven
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eleven, fodt_word_count_times_eleven
from src.python.ods.ods_parser import ods_sheet_count_times_eleven, ods_total_cell_count_times_eleven
from src.python.odt.odt_parser import odt_word_count_times_eleven, odt_paragraph_count_times_eleven
from src.python.fodp.fodp_codec import fodp_slide_count_times_eleven, fodp_word_count_times_eleven

SAMPLES = _REPO / "samples" / "by-format"
_FODS = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

_wb = parse_fods_strict(_FODS)


class TestFodsSheetCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_eleven(_wb), int)

    def test_non_negative(self):
        assert fods_sheet_count_times_eleven(_wb) >= 0

    def test_divisible(self):
        assert fods_sheet_count_times_eleven(_wb) % 11 == 0


class TestFodsTotalCellCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_eleven(_wb), int)

    def test_non_negative(self):
        assert fods_total_cell_count_times_eleven(_wb) >= 0

    def test_divisible(self):
        assert fods_total_cell_count_times_eleven(_wb) % 11 == 0


class TestFodtParagraphCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_eleven(_FODT), int)

    def test_non_negative(self):
        assert fodt_paragraph_count_times_eleven(_FODT) >= 0

    def test_divisible(self):
        assert fodt_paragraph_count_times_eleven(_FODT) % 11 == 0


class TestFodtWordCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_eleven(_FODT), int)

    def test_non_negative(self):
        assert fodt_word_count_times_eleven(_FODT) >= 0

    def test_divisible(self):
        assert fodt_word_count_times_eleven(_FODT) % 11 == 0


class TestOdsSheetCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_eleven(_ODS), int)

    def test_non_negative(self):
        assert ods_sheet_count_times_eleven(_ODS) >= 0

    def test_divisible(self):
        assert ods_sheet_count_times_eleven(_ODS) % 11 == 0


class TestOdsTotalCellCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_eleven(_ODS), int)

    def test_non_negative(self):
        assert ods_total_cell_count_times_eleven(_ODS) >= 0

    def test_divisible(self):
        assert ods_total_cell_count_times_eleven(_ODS) % 11 == 0


class TestOdtWordCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_eleven(_ODT), int)

    def test_non_negative(self):
        assert odt_word_count_times_eleven(_ODT) >= 0

    def test_divisible(self):
        assert odt_word_count_times_eleven(_ODT) % 11 == 0


class TestOdtParagraphCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_eleven(_ODT), int)

    def test_non_negative(self):
        assert odt_paragraph_count_times_eleven(_ODT) >= 0

    def test_divisible(self):
        assert odt_paragraph_count_times_eleven(_ODT) % 11 == 0


class TestFodpSlideCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_eleven(_FODP), int)

    def test_non_negative(self):
        assert fodp_slide_count_times_eleven(_FODP) >= 0

    def test_divisible(self):
        assert fodp_slide_count_times_eleven(_FODP) % 11 == 0


class TestFodpWordCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_eleven(_FODP), int)

    def test_non_negative(self):
        assert fodp_word_count_times_eleven(_FODP) >= 0

    def test_divisible(self):
        assert fodp_word_count_times_eleven(_FODP) % 11 == 0

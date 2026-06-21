"""Sprint R493 — FODS/FODT/ODS/ODT/FODP _times_twelve composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_sheet_count_times_twelve, fods_total_cell_count_times_twelve
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_twelve, fodt_word_count_times_twelve
from src.python.ods.ods_parser import ods_sheet_count_times_twelve, ods_total_cell_count_times_twelve
from src.python.odt.odt_parser import odt_word_count_times_twelve, odt_paragraph_count_times_twelve
from src.python.fodp.fodp_codec import fodp_slide_count_times_twelve, fodp_word_count_times_twelve

SAMPLES = _REPO / "samples" / "by-format"
_FODS = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

_wb = parse_fods_strict(_FODS)


class TestFodsSheetCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_twelve(_wb), int)

    def test_non_negative(self):
        assert fods_sheet_count_times_twelve(_wb) >= 0

    def test_divisible(self):
        assert fods_sheet_count_times_twelve(_wb) % 12 == 0


class TestFodsTotalCellCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_twelve(_wb), int)

    def test_non_negative(self):
        assert fods_total_cell_count_times_twelve(_wb) >= 0

    def test_divisible(self):
        assert fods_total_cell_count_times_twelve(_wb) % 12 == 0


class TestFodtParagraphCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_twelve(_FODT), int)

    def test_non_negative(self):
        assert fodt_paragraph_count_times_twelve(_FODT) >= 0

    def test_divisible(self):
        assert fodt_paragraph_count_times_twelve(_FODT) % 12 == 0


class TestFodtWordCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_twelve(_FODT), int)

    def test_non_negative(self):
        assert fodt_word_count_times_twelve(_FODT) >= 0

    def test_divisible(self):
        assert fodt_word_count_times_twelve(_FODT) % 12 == 0


class TestOdsSheetCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_twelve(_ODS), int)

    def test_non_negative(self):
        assert ods_sheet_count_times_twelve(_ODS) >= 0

    def test_divisible(self):
        assert ods_sheet_count_times_twelve(_ODS) % 12 == 0


class TestOdsTotalCellCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_twelve(_ODS), int)

    def test_non_negative(self):
        assert ods_total_cell_count_times_twelve(_ODS) >= 0

    def test_divisible(self):
        assert ods_total_cell_count_times_twelve(_ODS) % 12 == 0


class TestOdtWordCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_twelve(_ODT), int)

    def test_non_negative(self):
        assert odt_word_count_times_twelve(_ODT) >= 0

    def test_divisible(self):
        assert odt_word_count_times_twelve(_ODT) % 12 == 0


class TestOdtParagraphCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_twelve(_ODT), int)

    def test_non_negative(self):
        assert odt_paragraph_count_times_twelve(_ODT) >= 0

    def test_divisible(self):
        assert odt_paragraph_count_times_twelve(_ODT) % 12 == 0


class TestFodpSlideCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_twelve(_FODP), int)

    def test_non_negative(self):
        assert fodp_slide_count_times_twelve(_FODP) >= 0

    def test_divisible(self):
        assert fodp_slide_count_times_twelve(_FODP) % 12 == 0


class TestFodpWordCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_twelve(_FODP), int)

    def test_non_negative(self):
        assert fodp_word_count_times_twelve(_FODP) >= 0

    def test_divisible(self):
        assert fodp_word_count_times_twelve(_FODP) % 12 == 0

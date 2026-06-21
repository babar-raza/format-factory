"""Sprint R497 — FODS/FODT/ODS/ODT/FODP _times_thirteen composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_sheet_count_times_thirteen, fods_total_cell_count_times_thirteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_thirteen, fodt_word_count_times_thirteen
from src.python.ods.ods_parser import ods_sheet_count_times_thirteen, ods_total_cell_count_times_thirteen
from src.python.odt.odt_parser import odt_word_count_times_thirteen, odt_paragraph_count_times_thirteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_thirteen, fodp_word_count_times_thirteen

SAMPLES = _REPO / "samples" / "by-format"
_FODS = str(SAMPLES / "fods" / "minimal-spreadsheet.fods")
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

_wb = parse_fods_strict(_FODS)


class TestFodsSheetCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_thirteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_thirteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_thirteen(_wb) % 13 == 0

class TestFodsTotalCellCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_thirteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_thirteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_thirteen(_wb) % 13 == 0

class TestFodtParagraphCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_thirteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_thirteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_thirteen(_FODT) % 13 == 0

class TestFodtWordCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_thirteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_thirteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_thirteen(_FODT) % 13 == 0

class TestOdsSheetCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_thirteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_thirteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_thirteen(_ODS) % 13 == 0

class TestOdsTotalCellCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_thirteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_thirteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_thirteen(_ODS) % 13 == 0

class TestOdtWordCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_thirteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_thirteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_thirteen(_ODT) % 13 == 0

class TestOdtParagraphCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_thirteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_thirteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_thirteen(_ODT) % 13 == 0

class TestFodpSlideCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_thirteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_thirteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_thirteen(_FODP) % 13 == 0

class TestFodpWordCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_thirteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_thirteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_thirteen(_FODP) % 13 == 0

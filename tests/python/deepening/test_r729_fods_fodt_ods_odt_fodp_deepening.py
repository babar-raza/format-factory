"""Sprint R729 — FODS/FODT/ODS/ODT/FODP _times_seventy_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_seventy_one, fods_total_cell_count_times_seventy_one
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_seventy_one, fodt_word_count_times_seventy_one
from src.python.ods.ods_parser import ods_sheet_count_times_seventy_one, ods_total_cell_count_times_seventy_one
from src.python.odt.odt_parser import odt_word_count_times_seventy_one, odt_paragraph_count_times_seventy_one
from src.python.fodp.fodp_codec import fodp_slide_count_times_seventy_one, fodp_word_count_times_seventy_one
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_seventy_one(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_seventy_one(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_seventy_one(_wb) % 71 == 0
class TestFodsTotalCellCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_seventy_one(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_seventy_one(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_seventy_one(_wb) % 71 == 0
class TestFodtParagraphCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_seventy_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_seventy_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_seventy_one(_FODT) % 71 == 0
class TestFodtWordCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_seventy_one(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_seventy_one(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_seventy_one(_FODT) % 71 == 0
class TestOdsSheetCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_seventy_one(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_seventy_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_seventy_one(_ODS) % 71 == 0
class TestOdsTotalCellCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_seventy_one(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_seventy_one(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_seventy_one(_ODS) % 71 == 0
class TestOdtWordCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_seventy_one(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_seventy_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_seventy_one(_ODT) % 71 == 0
class TestOdtParagraphCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_seventy_one(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_seventy_one(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_seventy_one(_ODT) % 71 == 0
class TestFodpSlideCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_seventy_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_seventy_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_seventy_one(_FODP) % 71 == 0
class TestFodpWordCountTimesSeventyOne:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_seventy_one(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_seventy_one(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_seventy_one(_FODP) % 71 == 0

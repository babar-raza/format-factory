"""Sprint R593 — FODS/FODT/ODS/ODT/FODP _times_thirty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_thirty_seven, fods_total_cell_count_times_thirty_seven
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_thirty_seven, fodt_word_count_times_thirty_seven
from src.python.ods.ods_parser import ods_sheet_count_times_thirty_seven, ods_total_cell_count_times_thirty_seven
from src.python.odt.odt_parser import odt_word_count_times_thirty_seven, odt_paragraph_count_times_thirty_seven
from src.python.fodp.fodp_codec import fodp_slide_count_times_thirty_seven, fodp_word_count_times_thirty_seven
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_thirty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_thirty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_thirty_seven(_wb) % 37 == 0
class TestFodsTotalCellCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_thirty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_thirty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_thirty_seven(_wb) % 37 == 0
class TestFodtParagraphCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_thirty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_thirty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_thirty_seven(_FODT) % 37 == 0
class TestFodtWordCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_thirty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_thirty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_thirty_seven(_FODT) % 37 == 0
class TestOdsSheetCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_thirty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_thirty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_thirty_seven(_ODS) % 37 == 0
class TestOdsTotalCellCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_thirty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_thirty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_thirty_seven(_ODS) % 37 == 0
class TestOdtWordCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_thirty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_thirty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_thirty_seven(_ODT) % 37 == 0
class TestOdtParagraphCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_thirty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_thirty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_thirty_seven(_ODT) % 37 == 0
class TestFodpSlideCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_thirty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_thirty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_thirty_seven(_FODP) % 37 == 0
class TestFodpWordCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_thirty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_thirty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_thirty_seven(_FODP) % 37 == 0

"""Sprint R673 — FODS/FODT/ODS/ODT/FODP _times_fifty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_fifty_seven, fods_total_cell_count_times_fifty_seven
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_fifty_seven, fodt_word_count_times_fifty_seven
from src.python.ods.ods_parser import ods_sheet_count_times_fifty_seven, ods_total_cell_count_times_fifty_seven
from src.python.odt.odt_parser import odt_word_count_times_fifty_seven, odt_paragraph_count_times_fifty_seven
from src.python.fodp.fodp_codec import fodp_slide_count_times_fifty_seven, fodp_word_count_times_fifty_seven
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_fifty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_fifty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_fifty_seven(_wb) % 57 == 0
class TestFodsTotalCellCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_fifty_seven(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_fifty_seven(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_fifty_seven(_wb) % 57 == 0
class TestFodtParagraphCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_fifty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_fifty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_fifty_seven(_FODT) % 57 == 0
class TestFodtWordCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_fifty_seven(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_fifty_seven(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_fifty_seven(_FODT) % 57 == 0
class TestOdsSheetCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_fifty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_fifty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_fifty_seven(_ODS) % 57 == 0
class TestOdsTotalCellCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_fifty_seven(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_fifty_seven(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_fifty_seven(_ODS) % 57 == 0
class TestOdtWordCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_fifty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_fifty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_fifty_seven(_ODT) % 57 == 0
class TestOdtParagraphCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_fifty_seven(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_fifty_seven(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_fifty_seven(_ODT) % 57 == 0
class TestFodpSlideCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_fifty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_fifty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_fifty_seven(_FODP) % 57 == 0
class TestFodpWordCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_fifty_seven(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_fifty_seven(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_fifty_seven(_FODP) % 57 == 0

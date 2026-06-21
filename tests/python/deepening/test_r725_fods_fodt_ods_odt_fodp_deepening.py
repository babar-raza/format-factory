"""Sprint R725 — FODS/FODT/ODS/ODT/FODP _times_seventy composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_seventy, fods_total_cell_count_times_seventy
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_seventy, fodt_word_count_times_seventy
from src.python.ods.ods_parser import ods_sheet_count_times_seventy, ods_total_cell_count_times_seventy
from src.python.odt.odt_parser import odt_word_count_times_seventy, odt_paragraph_count_times_seventy
from src.python.fodp.fodp_codec import fodp_slide_count_times_seventy, fodp_word_count_times_seventy
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_seventy(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_seventy(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_seventy(_wb) % 70 == 0
class TestFodsTotalCellCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_seventy(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_seventy(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_seventy(_wb) % 70 == 0
class TestFodtParagraphCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_seventy(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_seventy(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_seventy(_FODT) % 70 == 0
class TestFodtWordCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_seventy(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_seventy(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_seventy(_FODT) % 70 == 0
class TestOdsSheetCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_seventy(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_seventy(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_seventy(_ODS) % 70 == 0
class TestOdsTotalCellCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_seventy(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_seventy(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_seventy(_ODS) % 70 == 0
class TestOdtWordCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_seventy(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_seventy(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_seventy(_ODT) % 70 == 0
class TestOdtParagraphCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_seventy(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_seventy(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_seventy(_ODT) % 70 == 0
class TestFodpSlideCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_seventy(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_seventy(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_seventy(_FODP) % 70 == 0
class TestFodpWordCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_seventy(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_seventy(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_seventy(_FODP) % 70 == 0

"""Sprint R785 — FODS/FODT/ODS/ODT/FODP _times_eighty_five composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_eighty_five, fods_total_cell_count_times_eighty_five
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eighty_five, fodt_word_count_times_eighty_five
from src.python.ods.ods_parser import ods_sheet_count_times_eighty_five, ods_total_cell_count_times_eighty_five
from src.python.odt.odt_parser import odt_word_count_times_eighty_five, odt_paragraph_count_times_eighty_five
from src.python.fodp.fodp_codec import fodp_slide_count_times_eighty_five, fodp_word_count_times_eighty_five
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_eighty_five(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_eighty_five(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_eighty_five(_wb) % 85 == 0
class TestFodsTotalCellCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_eighty_five(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_eighty_five(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_eighty_five(_wb) % 85 == 0
class TestFodtParagraphCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_eighty_five(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_eighty_five(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_eighty_five(_FODT) % 85 == 0
class TestFodtWordCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_eighty_five(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_eighty_five(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_eighty_five(_FODT) % 85 == 0
class TestOdsSheetCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_eighty_five(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_eighty_five(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_eighty_five(_ODS) % 85 == 0
class TestOdsTotalCellCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_eighty_five(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_eighty_five(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_eighty_five(_ODS) % 85 == 0
class TestOdtWordCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_eighty_five(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_eighty_five(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_eighty_five(_ODT) % 85 == 0
class TestOdtParagraphCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_eighty_five(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_eighty_five(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_eighty_five(_ODT) % 85 == 0
class TestFodpSlideCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_eighty_five(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_eighty_five(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_eighty_five(_FODP) % 85 == 0
class TestFodpWordCountTimesEightyFive:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_eighty_five(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_eighty_five(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_eighty_five(_FODP) % 85 == 0

"""Sprint R765 — FODS/FODT/ODS/ODT/FODP _times_eighty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_eighty, fods_total_cell_count_times_eighty
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eighty, fodt_word_count_times_eighty
from src.python.ods.ods_parser import ods_sheet_count_times_eighty, ods_total_cell_count_times_eighty
from src.python.odt.odt_parser import odt_word_count_times_eighty, odt_paragraph_count_times_eighty
from src.python.fodp.fodp_codec import fodp_slide_count_times_eighty, fodp_word_count_times_eighty
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_eighty(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_eighty(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_eighty(_wb) % 80 == 0
class TestFodsTotalCellCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_eighty(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_eighty(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_eighty(_wb) % 80 == 0
class TestFodtParagraphCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_eighty(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_eighty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_eighty(_FODT) % 80 == 0
class TestFodtWordCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_eighty(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_eighty(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_eighty(_FODT) % 80 == 0
class TestOdsSheetCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_eighty(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_eighty(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_eighty(_ODS) % 80 == 0
class TestOdsTotalCellCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_eighty(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_eighty(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_eighty(_ODS) % 80 == 0
class TestOdtWordCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_eighty(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_eighty(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_eighty(_ODT) % 80 == 0
class TestOdtParagraphCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_eighty(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_eighty(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_eighty(_ODT) % 80 == 0
class TestFodpSlideCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_eighty(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_eighty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_eighty(_FODP) % 80 == 0
class TestFodpWordCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_eighty(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_eighty(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_eighty(_FODP) % 80 == 0

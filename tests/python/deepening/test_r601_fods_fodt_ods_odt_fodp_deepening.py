"""Sprint R601 — FODS/FODT/ODS/ODT/FODP _times_thirty_nine composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_thirty_nine, fods_total_cell_count_times_thirty_nine
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_thirty_nine, fodt_word_count_times_thirty_nine
from src.python.ods.ods_parser import ods_sheet_count_times_thirty_nine, ods_total_cell_count_times_thirty_nine
from src.python.odt.odt_parser import odt_word_count_times_thirty_nine, odt_paragraph_count_times_thirty_nine
from src.python.fodp.fodp_codec import fodp_slide_count_times_thirty_nine, fodp_word_count_times_thirty_nine
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_thirty_nine(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_thirty_nine(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_thirty_nine(_wb) % 39 == 0
class TestFodsTotalCellCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_thirty_nine(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_thirty_nine(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_thirty_nine(_wb) % 39 == 0
class TestFodtParagraphCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_thirty_nine(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_thirty_nine(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_thirty_nine(_FODT) % 39 == 0
class TestFodtWordCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_thirty_nine(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_thirty_nine(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_thirty_nine(_FODT) % 39 == 0
class TestOdsSheetCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_thirty_nine(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_thirty_nine(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_thirty_nine(_ODS) % 39 == 0
class TestOdsTotalCellCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_thirty_nine(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_thirty_nine(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_thirty_nine(_ODS) % 39 == 0
class TestOdtWordCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_thirty_nine(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_thirty_nine(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_thirty_nine(_ODT) % 39 == 0
class TestOdtParagraphCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_thirty_nine(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_thirty_nine(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_thirty_nine(_ODT) % 39 == 0
class TestFodpSlideCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_thirty_nine(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_thirty_nine(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_thirty_nine(_FODP) % 39 == 0
class TestFodpWordCountTimesThirtyNine:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_thirty_nine(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_thirty_nine(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_thirty_nine(_FODP) % 39 == 0

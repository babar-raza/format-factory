"""Sprint R573 — FODS/FODT/ODS/ODT/FODP _times_thirty_two composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_thirty_two, fods_total_cell_count_times_thirty_two
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_thirty_two, fodt_word_count_times_thirty_two
from src.python.ods.ods_parser import ods_sheet_count_times_thirty_two, ods_total_cell_count_times_thirty_two
from src.python.odt.odt_parser import odt_word_count_times_thirty_two, odt_paragraph_count_times_thirty_two
from src.python.fodp.fodp_codec import fodp_slide_count_times_thirty_two, fodp_word_count_times_thirty_two
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_thirty_two(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_thirty_two(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_thirty_two(_wb) % 32 == 0
class TestFodsTotalCellCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_thirty_two(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_thirty_two(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_thirty_two(_wb) % 32 == 0
class TestFodtParagraphCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_thirty_two(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_thirty_two(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_thirty_two(_FODT) % 32 == 0
class TestFodtWordCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_thirty_two(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_thirty_two(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_thirty_two(_FODT) % 32 == 0
class TestOdsSheetCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_thirty_two(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_thirty_two(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_thirty_two(_ODS) % 32 == 0
class TestOdsTotalCellCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_thirty_two(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_thirty_two(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_thirty_two(_ODS) % 32 == 0
class TestOdtWordCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_thirty_two(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_thirty_two(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_thirty_two(_ODT) % 32 == 0
class TestOdtParagraphCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_thirty_two(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_thirty_two(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_thirty_two(_ODT) % 32 == 0
class TestFodpSlideCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_thirty_two(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_thirty_two(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_thirty_two(_FODP) % 32 == 0
class TestFodpWordCountTimesThirtyTwo:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_thirty_two(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_thirty_two(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_thirty_two(_FODP) % 32 == 0

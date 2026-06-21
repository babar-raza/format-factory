"""Sprint R749 — FODS/FODT/ODS/ODT/FODP _times_seventy_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_seventy_six, fods_total_cell_count_times_seventy_six
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_seventy_six, fodt_word_count_times_seventy_six
from src.python.ods.ods_parser import ods_sheet_count_times_seventy_six, ods_total_cell_count_times_seventy_six
from src.python.odt.odt_parser import odt_word_count_times_seventy_six, odt_paragraph_count_times_seventy_six
from src.python.fodp.fodp_codec import fodp_slide_count_times_seventy_six, fodp_word_count_times_seventy_six
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_seventy_six(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_seventy_six(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_seventy_six(_wb) % 76 == 0
class TestFodsTotalCellCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_seventy_six(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_seventy_six(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_seventy_six(_wb) % 76 == 0
class TestFodtParagraphCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_seventy_six(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_seventy_six(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_seventy_six(_FODT) % 76 == 0
class TestFodtWordCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_seventy_six(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_seventy_six(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_seventy_six(_FODT) % 76 == 0
class TestOdsSheetCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_seventy_six(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_seventy_six(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_seventy_six(_ODS) % 76 == 0
class TestOdsTotalCellCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_seventy_six(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_seventy_six(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_seventy_six(_ODS) % 76 == 0
class TestOdtWordCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_seventy_six(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_seventy_six(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_seventy_six(_ODT) % 76 == 0
class TestOdtParagraphCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_seventy_six(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_seventy_six(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_seventy_six(_ODT) % 76 == 0
class TestFodpSlideCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_seventy_six(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_seventy_six(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_seventy_six(_FODP) % 76 == 0
class TestFodpWordCountTimesSeventySix:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_seventy_six(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_seventy_six(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_seventy_six(_FODP) % 76 == 0

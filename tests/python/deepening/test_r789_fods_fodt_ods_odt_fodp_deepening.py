"""Sprint R789 — FODS/FODT/ODS/ODT/FODP _times_eighty_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_eighty_six, fods_total_cell_count_times_eighty_six
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eighty_six, fodt_word_count_times_eighty_six
from src.python.ods.ods_parser import ods_sheet_count_times_eighty_six, ods_total_cell_count_times_eighty_six
from src.python.odt.odt_parser import odt_word_count_times_eighty_six, odt_paragraph_count_times_eighty_six
from src.python.fodp.fodp_codec import fodp_slide_count_times_eighty_six, fodp_word_count_times_eighty_six
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_eighty_six(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_eighty_six(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_eighty_six(_wb) % 86 == 0
class TestFodsTotalCellCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_eighty_six(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_eighty_six(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_eighty_six(_wb) % 86 == 0
class TestFodtParagraphCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_eighty_six(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_eighty_six(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_eighty_six(_FODT) % 86 == 0
class TestFodtWordCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_eighty_six(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_eighty_six(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_eighty_six(_FODT) % 86 == 0
class TestOdsSheetCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_eighty_six(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_eighty_six(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_eighty_six(_ODS) % 86 == 0
class TestOdsTotalCellCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_eighty_six(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_eighty_six(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_eighty_six(_ODS) % 86 == 0
class TestOdtWordCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_eighty_six(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_eighty_six(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_eighty_six(_ODT) % 86 == 0
class TestOdtParagraphCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_eighty_six(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_eighty_six(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_eighty_six(_ODT) % 86 == 0
class TestFodpSlideCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_eighty_six(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_eighty_six(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_eighty_six(_FODP) % 86 == 0
class TestFodpWordCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_eighty_six(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_eighty_six(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_eighty_six(_FODP) % 86 == 0

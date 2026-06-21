"""Sprint R517 — FODS/FODT/ODS/ODT/FODP _times_eighteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_eighteen, fods_total_cell_count_times_eighteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_eighteen, fodt_word_count_times_eighteen
from src.python.ods.ods_parser import ods_sheet_count_times_eighteen, ods_total_cell_count_times_eighteen
from src.python.odt.odt_parser import odt_word_count_times_eighteen, odt_paragraph_count_times_eighteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_eighteen, fodp_word_count_times_eighteen
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_eighteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_eighteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_eighteen(_wb) % 18 == 0
class TestFodsTotalCellCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_eighteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_eighteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_eighteen(_wb) % 18 == 0
class TestFodtParagraphCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_eighteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_eighteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_eighteen(_FODT) % 18 == 0
class TestFodtWordCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_eighteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_eighteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_eighteen(_FODT) % 18 == 0
class TestOdsSheetCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_eighteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_eighteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_eighteen(_ODS) % 18 == 0
class TestOdsTotalCellCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_eighteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_eighteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_eighteen(_ODS) % 18 == 0
class TestOdtWordCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_eighteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_eighteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_eighteen(_ODT) % 18 == 0
class TestOdtParagraphCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_eighteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_eighteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_eighteen(_ODT) % 18 == 0
class TestFodpSlideCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_eighteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_eighteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_eighteen(_FODP) % 18 == 0
class TestFodpWordCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_eighteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_eighteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_eighteen(_FODP) % 18 == 0

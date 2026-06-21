"""Sprint R557 — FODS/FODT/ODS/ODT/FODP _times_twenty_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_twenty_eight, fods_total_cell_count_times_twenty_eight
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_twenty_eight, fodt_word_count_times_twenty_eight
from src.python.ods.ods_parser import ods_sheet_count_times_twenty_eight, ods_total_cell_count_times_twenty_eight
from src.python.odt.odt_parser import odt_word_count_times_twenty_eight, odt_paragraph_count_times_twenty_eight
from src.python.fodp.fodp_codec import fodp_slide_count_times_twenty_eight, fodp_word_count_times_twenty_eight
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_twenty_eight(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_twenty_eight(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_twenty_eight(_wb) % 28 == 0
class TestFodsTotalCellCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_twenty_eight(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_twenty_eight(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_twenty_eight(_wb) % 28 == 0
class TestFodtParagraphCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_twenty_eight(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_twenty_eight(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_twenty_eight(_FODT) % 28 == 0
class TestFodtWordCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_twenty_eight(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_twenty_eight(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_twenty_eight(_FODT) % 28 == 0
class TestOdsSheetCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_twenty_eight(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_twenty_eight(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_twenty_eight(_ODS) % 28 == 0
class TestOdsTotalCellCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_twenty_eight(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_twenty_eight(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_twenty_eight(_ODS) % 28 == 0
class TestOdtWordCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_twenty_eight(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_twenty_eight(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_twenty_eight(_ODT) % 28 == 0
class TestOdtParagraphCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_twenty_eight(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_twenty_eight(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_twenty_eight(_ODT) % 28 == 0
class TestFodpSlideCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_twenty_eight(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_twenty_eight(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_twenty_eight(_FODP) % 28 == 0
class TestFodpWordCountTimesTwentyEight:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_twenty_eight(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_twenty_eight(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_twenty_eight(_FODP) % 28 == 0

"""Sprint R637 — FODS/FODT/ODS/ODT/FODP _times_forty_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_forty_eight, fods_total_cell_count_times_forty_eight
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_forty_eight, fodt_word_count_times_forty_eight
from src.python.ods.ods_parser import ods_sheet_count_times_forty_eight, ods_total_cell_count_times_forty_eight
from src.python.odt.odt_parser import odt_word_count_times_forty_eight, odt_paragraph_count_times_forty_eight
from src.python.fodp.fodp_codec import fodp_slide_count_times_forty_eight, fodp_word_count_times_forty_eight
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_forty_eight(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_forty_eight(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_forty_eight(_wb) % 48 == 0
class TestFodsTotalCellCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_forty_eight(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_forty_eight(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_forty_eight(_wb) % 48 == 0
class TestFodtParagraphCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_forty_eight(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_forty_eight(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_forty_eight(_FODT) % 48 == 0
class TestFodtWordCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_forty_eight(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_forty_eight(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_forty_eight(_FODT) % 48 == 0
class TestOdsSheetCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_forty_eight(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_forty_eight(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_forty_eight(_ODS) % 48 == 0
class TestOdsTotalCellCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_forty_eight(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_forty_eight(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_forty_eight(_ODS) % 48 == 0
class TestOdtWordCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_forty_eight(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_forty_eight(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_forty_eight(_ODT) % 48 == 0
class TestOdtParagraphCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_forty_eight(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_forty_eight(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_forty_eight(_ODT) % 48 == 0
class TestFodpSlideCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_forty_eight(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_forty_eight(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_forty_eight(_FODP) % 48 == 0
class TestFodpWordCountTimesFortyEight:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_forty_eight(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_forty_eight(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_forty_eight(_FODP) % 48 == 0

"""Sprint R509 — FODS/FODT/ODS/ODT/FODP _times_sixteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fods.neutral_model import fods_sheet_count_times_sixteen, fods_total_cell_count_times_sixteen
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_sixteen, fodt_word_count_times_sixteen
from src.python.ods.ods_parser import ods_sheet_count_times_sixteen, ods_total_cell_count_times_sixteen
from src.python.odt.odt_parser import odt_word_count_times_sixteen, odt_paragraph_count_times_sixteen
from src.python.fodp.fodp_codec import fodp_slide_count_times_sixteen, fodp_word_count_times_sixteen
SAMPLES = _REPO / "samples" / "by-format"
_wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
_FODT = str(SAMPLES / "fodt" / "minimal-document.fodt")
_ODS = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
_ODT = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
_FODP = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodsSheetCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_sixteen(_wb), int)
    def test_non_negative(self):
        assert fods_sheet_count_times_sixteen(_wb) >= 0
    def test_divisible(self):
        assert fods_sheet_count_times_sixteen(_wb) % 16 == 0
class TestFodsTotalCellCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_sixteen(_wb), int)
    def test_non_negative(self):
        assert fods_total_cell_count_times_sixteen(_wb) >= 0
    def test_divisible(self):
        assert fods_total_cell_count_times_sixteen(_wb) % 16 == 0
class TestFodtParagraphCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_sixteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_sixteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_sixteen(_FODT) % 16 == 0
class TestFodtWordCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_sixteen(_FODT), int)
    def test_non_negative(self):
        assert fodt_word_count_times_sixteen(_FODT) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_sixteen(_FODT) % 16 == 0
class TestOdsSheetCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_sixteen(_ODS), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_sixteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_sixteen(_ODS) % 16 == 0
class TestOdsTotalCellCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_sixteen(_ODS), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_sixteen(_ODS) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_sixteen(_ODS) % 16 == 0
class TestOdtWordCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_sixteen(_ODT), int)
    def test_non_negative(self):
        assert odt_word_count_times_sixteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_word_count_times_sixteen(_ODT) % 16 == 0
class TestOdtParagraphCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_sixteen(_ODT), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_sixteen(_ODT) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_sixteen(_ODT) % 16 == 0
class TestFodpSlideCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_sixteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_sixteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_sixteen(_FODP) % 16 == 0
class TestFodpWordCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_sixteen(_FODP), int)
    def test_non_negative(self):
        assert fodp_word_count_times_sixteen(_FODP) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_sixteen(_FODP) % 16 == 0

"""Sprint R485 — FODS/FODT/ODS/ODT/FODP _times_ten composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_sheet_count_times_ten, fods_total_cell_count_times_ten
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_ten, fodt_word_count_times_ten
from src.python.ods.ods_parser import ods_sheet_count_times_ten, ods_total_cell_count_times_ten
from src.python.odt.odt_parser import odt_word_count_times_ten, odt_paragraph_count_times_ten
from src.python.fodp.fodp_codec import fodp_slide_count_times_ten, fodp_word_count_times_ten

SAMPLES = _REPO / "samples" / "by-format"

class TestFodsSheetCountTimesTen:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_sheet_count_times_ten(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_ten(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_ten(wb) % 10 == 0

class TestFodsTotalCellCountTimesTen:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_total_cell_count_times_ten(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_ten(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_ten(wb) % 10 == 0

class TestFodtParagraphCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")) % 10 == 0

class TestFodtWordCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")), int)
    def test_non_negative(self):
        assert fodt_word_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_ten(str(SAMPLES / "fodt" / "minimal-document.fodt")) % 10 == 0

class TestOdsSheetCountTimesTen:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) % 10 == 0

class TestOdsTotalCellCountTimesTen:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_ten(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) % 10 == 0

class TestOdtWordCountTimesTen:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")), int)
    def test_non_negative(self):
        assert odt_word_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) >= 0
    def test_divisible(self):
        assert odt_word_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) % 10 == 0

class TestOdtParagraphCountTimesTen:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_ten(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) % 10 == 0

class TestFodpSlideCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")) % 10 == 0

class TestFodpWordCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")), int)
    def test_non_negative(self):
        assert fodp_word_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_ten(str(SAMPLES / "fodp" / "title-only.fodp")) % 10 == 0

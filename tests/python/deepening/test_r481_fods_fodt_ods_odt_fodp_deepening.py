"""Sprint R481 — FODS/FODT/ODS/ODT/FODP _times_nine composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_sheet_count_times_nine, fods_total_cell_count_times_nine
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_times_nine, fodt_word_count_times_nine
from src.python.ods.ods_parser import ods_sheet_count_times_nine, ods_total_cell_count_times_nine
from src.python.odt.odt_parser import odt_word_count_times_nine, odt_paragraph_count_times_nine
from src.python.fodp.fodp_codec import fodp_slide_count_times_nine, fodp_word_count_times_nine

SAMPLES = _REPO / "samples" / "by-format"

# --- FODS ---
class TestFodsSheetCountTimesNine:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_sheet_count_times_nine(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_nine(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_nine(wb) % 9 == 0

class TestFodsTotalCellCountTimesNine:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_total_cell_count_times_nine(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_nine(wb) >= 0
    def test_divisible(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_nine(wb) % 9 == 0

# --- FODT ---
class TestFodtParagraphCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")), int)
    def test_non_negative(self):
        assert fodt_paragraph_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")) >= 0
    def test_divisible(self):
        assert fodt_paragraph_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")) % 9 == 0

class TestFodtWordCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")), int)
    def test_non_negative(self):
        assert fodt_word_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")) >= 0
    def test_divisible(self):
        assert fodt_word_count_times_nine(str(SAMPLES / "fodt" / "minimal-document.fodt")) % 9 == 0

# --- ODS ---
class TestOdsSheetCountTimesNine:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")), int)
    def test_non_negative(self):
        assert ods_sheet_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) >= 0
    def test_divisible(self):
        assert ods_sheet_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) % 9 == 0

class TestOdsTotalCellCountTimesNine:
    def test_returns_int(self):
        assert isinstance(ods_total_cell_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")), int)
    def test_non_negative(self):
        assert ods_total_cell_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) >= 0
    def test_divisible(self):
        assert ods_total_cell_count_times_nine(str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")) % 9 == 0

# --- ODT ---
class TestOdtWordCountTimesNine:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")), int)
    def test_non_negative(self):
        assert odt_word_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) >= 0
    def test_divisible(self):
        assert odt_word_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) % 9 == 0

class TestOdtParagraphCountTimesNine:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")), int)
    def test_non_negative(self):
        assert odt_paragraph_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) >= 0
    def test_divisible(self):
        assert odt_paragraph_count_times_nine(str(SAMPLES / "odt" / "valid" / "minimal-document.odt")) % 9 == 0

# --- FODP ---
class TestFodpSlideCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")), int)
    def test_non_negative(self):
        assert fodp_slide_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")) >= 0
    def test_divisible(self):
        assert fodp_slide_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")) % 9 == 0

class TestFodpWordCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")), int)
    def test_non_negative(self):
        assert fodp_word_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")) >= 0
    def test_divisible(self):
        assert fodp_word_count_times_nine(str(SAMPLES / "fodp" / "title-only.fodp")) % 9 == 0

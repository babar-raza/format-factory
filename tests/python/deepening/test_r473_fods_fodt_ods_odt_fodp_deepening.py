"""Sprint R473 — FODS/FODT/ODS/ODT/FODP _times_seven composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.fods.neutral_model import fods_sheet_count_times_seven, fods_total_cell_count_times_seven
from src.python.fodt.neutral_model import fodt_paragraph_count_times_seven, fodt_word_count_times_seven
from src.python.ods.ods_parser import ods_sheet_count_times_seven, ods_total_cell_count_times_seven
from src.python.odt.odt_parser import odt_word_count_times_seven, odt_paragraph_count_times_seven
from src.python.fodp.fodp_codec import fodp_slide_count_times_seven, fodp_word_count_times_seven
from src.python.fods import parse_fods_strict

# --- FODS (workbook-based) ---
class TestFodsSheetCountTimesSeven:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_sheet_count_times_seven(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_seven(wb) >= 0
    def test_divisible_by_seven(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_sheet_count_times_seven(wb) % 7 == 0

class TestFodsTotalCellCountTimesSeven:
    def test_returns_int(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert isinstance(fods_total_cell_count_times_seven(wb), int)
    def test_non_negative(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_seven(wb) >= 0
    def test_divisible_by_seven(self):
        wb = parse_fods_strict(str(SAMPLES / "fods" / "minimal-spreadsheet.fods"))
        assert fods_total_cell_count_times_seven(wb) % 7 == 0

# --- FODT (path-based) ---
class TestFodtParagraphCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_paragraph_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_paragraph_count_times_seven(p) % 7 == 0

class TestFodtWordCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert isinstance(fodt_word_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodt" / "minimal-document.fodt")
        assert fodt_word_count_times_seven(p) % 7 == 0

# --- ODS ---
class TestOdsSheetCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_sheet_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_sheet_count_times_seven(p) % 7 == 0

class TestOdsTotalCellCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(ods_total_cell_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")
        assert ods_total_cell_count_times_seven(p) % 7 == 0

# --- ODT ---
class TestOdtWordCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_word_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_word_count_times_seven(p) % 7 == 0

class TestOdtParagraphCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert isinstance(odt_paragraph_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")
        assert odt_paragraph_count_times_seven(p) % 7 == 0

# --- FODP ---
class TestFodpSlideCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_slide_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_slide_count_times_seven(p) % 7 == 0

class TestFodpWordCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert isinstance(fodp_word_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodp" / "title-only.fodp")
        assert fodp_word_count_times_seven(p) % 7 == 0

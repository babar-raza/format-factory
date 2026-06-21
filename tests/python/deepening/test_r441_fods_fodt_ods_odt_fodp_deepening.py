"""Sprint R441 — FODS/FODT/ODS/ODT/FODP deepening round 6 (composite analytics)."""
import sys, pathlib, os

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

# ── FODS ──────────────────────────────────────────────────────────────
from src.python.fods import parse_fods_strict
from src.python.fods.neutral_model import (
    fods_total_cells_squared,
    fods_numeric_cells_times_two,
    fods_total_cell_count,
    fods_numeric_cell_count,
)

_fods_wb = parse_fods_strict(SAMPLES / "fods" / "minimal-spreadsheet.fods")

class TestFodsTotalCellsSquared:
    def test_type(self):
        assert isinstance(fods_total_cells_squared(_fods_wb), int)
    def test_value(self):
        tc = fods_total_cell_count(_fods_wb)
        assert fods_total_cells_squared(_fods_wb) == tc * tc
    def test_nonneg(self):
        assert fods_total_cells_squared(_fods_wb) >= 0

class TestFodsNumericCellsTimesTwo:
    def test_type(self):
        assert isinstance(fods_numeric_cells_times_two(_fods_wb), int)
    def test_value(self):
        nc = fods_numeric_cell_count(_fods_wb)
        assert fods_numeric_cells_times_two(_fods_wb) == nc * 2
    def test_nonneg(self):
        assert fods_numeric_cells_times_two(_fods_wb) >= 0

# ── FODT ──────────────────────────────────────────────────────────────
from src.python.fodt.neutral_model import (
    fodt_word_count_times_two,
    fodt_char_count_times_two,
    fodt_word_count,
    fodt_char_count,
)

_fodt_path = str(SAMPLES / "fodt" / "minimal-document.fodt")

class TestFodtWordCountTimesTwo:
    def test_type(self):
        assert isinstance(fodt_word_count_times_two(_fodt_path), int)
    def test_value(self):
        assert fodt_word_count_times_two(_fodt_path) == fodt_word_count(_fodt_path) * 2
    def test_nonneg(self):
        assert fodt_word_count_times_two(_fodt_path) >= 0

class TestFodtCharCountTimesTwo:
    def test_type(self):
        assert isinstance(fodt_char_count_times_two(_fodt_path), int)
    def test_value(self):
        assert fodt_char_count_times_two(_fodt_path) == fodt_char_count(_fodt_path) * 2
    def test_nonneg(self):
        assert fodt_char_count_times_two(_fodt_path) >= 0

# ── ODS ───────────────────────────────────────────────────────────────
from src.python.ods.ods_parser import (
    ods_file_size_squared,
    ods_numeric_cell_count_times_two,
    ods_file_size_bytes,
    ods_numeric_cell_count,
)

_ods_path = str(SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods")

class TestOdsFileSizeSquared:
    def test_type(self):
        assert isinstance(ods_file_size_squared(_ods_path), int)
    def test_value(self):
        fs = ods_file_size_bytes(_ods_path)
        assert ods_file_size_squared(_ods_path) == fs * fs
    def test_positive(self):
        assert ods_file_size_squared(_ods_path) > 0

class TestOdsNumericCellCountTimesTwo:
    def test_type(self):
        assert isinstance(ods_numeric_cell_count_times_two(_ods_path), int)
    def test_value(self):
        nc = ods_numeric_cell_count(_ods_path)
        assert ods_numeric_cell_count_times_two(_ods_path) == nc * 2
    def test_nonneg(self):
        assert ods_numeric_cell_count_times_two(_ods_path) >= 0

# ── ODT ───────────────────────────────────────────────────────────────
from src.python.odt.odt_parser import (
    odt_paragraph_count_times_two,
    odt_word_count_times_two,
    odt_paragraph_count,
    odt_word_count,
)

_odt_path = str(SAMPLES / "odt" / "valid" / "minimal-document.odt")

class TestOdtParagraphCountTimesTwo:
    def test_type(self):
        assert isinstance(odt_paragraph_count_times_two(_odt_path), int)
    def test_value(self):
        assert odt_paragraph_count_times_two(_odt_path) == odt_paragraph_count(_odt_path) * 2
    def test_nonneg(self):
        assert odt_paragraph_count_times_two(_odt_path) >= 0

class TestOdtWordCountTimesTwo:
    def test_type(self):
        assert isinstance(odt_word_count_times_two(_odt_path), int)
    def test_value(self):
        assert odt_word_count_times_two(_odt_path) == odt_word_count(_odt_path) * 2
    def test_nonneg(self):
        assert odt_word_count_times_two(_odt_path) >= 0

# ── FODP ──────────────────────────────────────────────────────────────
from src.python.fodp.fodp_codec import (
    fodp_word_count_times_two,
    fodp_file_size_squared,
    fodp_word_count,
    fodp_file_size_bytes,
)

_fodp_path = str(SAMPLES / "fodp" / "title-only.fodp")

class TestFodpWordCountTimesTwo:
    def test_type(self):
        assert isinstance(fodp_word_count_times_two(_fodp_path), int)
    def test_value(self):
        assert fodp_word_count_times_two(_fodp_path) == fodp_word_count(_fodp_path) * 2
    def test_nonneg(self):
        assert fodp_word_count_times_two(_fodp_path) >= 0

class TestFodpFileSizeSquared:
    def test_type(self):
        assert isinstance(fodp_file_size_squared(_fodp_path), int)
    def test_value(self):
        fs = fodp_file_size_bytes(_fodp_path)
        assert fodp_file_size_squared(_fodp_path) == fs * fs
    def test_positive(self):
        assert fodp_file_size_squared(_fodp_path) > 0

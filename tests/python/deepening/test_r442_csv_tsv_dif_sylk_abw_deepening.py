"""Sprint R442 — CSV/TSV/DIF/SYLK/ABW deepening round 7 (composite analytics)."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

# ── CSV ───────────────────────────────────────────────────────────────
from src.python.csv.csv_parser import (
    csv_field_count_times_two,
    csv_column_count_squared,
    csv_total_field_count,
    csv_column_count,
)

_csv_path = str(SAMPLES / "csv" / "single-cell.csv")

class TestCsvFieldCountTimesTwo:
    def test_type(self):
        assert isinstance(csv_field_count_times_two(_csv_path), int)
    def test_value(self):
        assert csv_field_count_times_two(_csv_path) == csv_total_field_count(_csv_path) * 2
    def test_nonneg(self):
        assert csv_field_count_times_two(_csv_path) >= 0

class TestCsvColumnCountSquared:
    def test_type(self):
        assert isinstance(csv_column_count_squared(_csv_path), int)
    def test_value(self):
        cc = csv_column_count(_csv_path)
        assert csv_column_count_squared(_csv_path) == cc * cc
    def test_nonneg(self):
        assert csv_column_count_squared(_csv_path) >= 0

# ── TSV ───────────────────────────────────────────────────────────────
from src.python.tsv.tsv_parser import (
    tsv_field_count_times_two,
    tsv_column_count_squared,
    tsv_total_field_count,
    tsv_column_count,
)

_tsv_path = str(SAMPLES / "tsv" / "minimal-2x2.tsv")

class TestTsvFieldCountTimesTwo:
    def test_type(self):
        assert isinstance(tsv_field_count_times_two(_tsv_path), int)
    def test_value(self):
        assert tsv_field_count_times_two(_tsv_path) == tsv_total_field_count(_tsv_path) * 2
    def test_nonneg(self):
        assert tsv_field_count_times_two(_tsv_path) >= 0

class TestTsvColumnCountSquared:
    def test_type(self):
        assert isinstance(tsv_column_count_squared(_tsv_path), int)
    def test_value(self):
        cc = tsv_column_count(_tsv_path)
        assert tsv_column_count_squared(_tsv_path) == cc * cc
    def test_nonneg(self):
        assert tsv_column_count_squared(_tsv_path) >= 0

# ── DIF ───────────────────────────────────────────────────────────────
from src.python.dif.dif_parser import (
    dif_cell_count_times_two,
    dif_column_count_squared,
    dif_total_cell_count,
    dif_column_count,
)

_dif_path = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")

class TestDifCellCountTimesTwo:
    def test_type(self):
        assert isinstance(dif_cell_count_times_two(_dif_path), int)
    def test_value(self):
        assert dif_cell_count_times_two(_dif_path) == dif_total_cell_count(_dif_path) * 2
    def test_nonneg(self):
        assert dif_cell_count_times_two(_dif_path) >= 0

class TestDifColumnCountSquared:
    def test_type(self):
        assert isinstance(dif_column_count_squared(_dif_path), int)
    def test_value(self):
        cc = dif_column_count(_dif_path)
        assert dif_column_count_squared(_dif_path) == cc * cc
    def test_nonneg(self):
        assert dif_column_count_squared(_dif_path) >= 0

# ── SYLK ──────────────────────────────────────────────────────────────
from src.python.sylk.sylk_parser import (
    sylk_row_count_times_two,
    sylk_column_count_squared,
    sylk_row_count,
    sylk_column_count,
)

_sylk_path = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")

class TestSylkRowCountTimesTwo:
    def test_type(self):
        assert isinstance(sylk_row_count_times_two(_sylk_path), int)
    def test_value(self):
        assert sylk_row_count_times_two(_sylk_path) == sylk_row_count(_sylk_path) * 2
    def test_nonneg(self):
        assert sylk_row_count_times_two(_sylk_path) >= 0

class TestSylkColumnCountSquared:
    def test_type(self):
        assert isinstance(sylk_column_count_squared(_sylk_path), int)
    def test_value(self):
        cc = sylk_column_count(_sylk_path)
        assert sylk_column_count_squared(_sylk_path) == cc * cc
    def test_nonneg(self):
        assert sylk_column_count_squared(_sylk_path) >= 0

# ── ABW ───────────────────────────────────────────────────────────────
from src.python.abw.abw_codec import (
    abw_paragraph_count_squared,
    abw_char_count_times_two,
    abw_paragraph_count,
    abw_char_count,
)

_abw_path = str(SAMPLES / "abw" / "minimal-document.abw")

class TestAbwParagraphCountSquared:
    def test_type(self):
        assert isinstance(abw_paragraph_count_squared(_abw_path), int)
    def test_value(self):
        pc = abw_paragraph_count(_abw_path)
        assert abw_paragraph_count_squared(_abw_path) == pc * pc
    def test_nonneg(self):
        assert abw_paragraph_count_squared(_abw_path) >= 0

class TestAbwCharCountTimesTwo:
    def test_type(self):
        assert isinstance(abw_char_count_times_two(_abw_path), int)
    def test_value(self):
        assert abw_char_count_times_two(_abw_path) == abw_char_count(_abw_path) * 2
    def test_nonneg(self):
        assert abw_char_count_times_two(_abw_path) >= 0

"""Sprint R438 — CSV/TSV/DIF/SYLK/ABW deepening round 6.

Functions under test (10 total, 2 per format):
  CSV:  csv_row_count_times_two, csv_file_size_squared
  TSV:  tsv_row_count_times_two, tsv_file_size_squared
  DIF:  dif_row_count_times_two, dif_file_size_squared
  SYLK: sylk_cell_count_squared, sylk_file_size_squared
  ABW:  abw_word_count_times_two, abw_file_size_squared
"""
import pathlib, sys, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- sample paths ---
_CSV = _REPO / "samples" / "by-format" / "csv" / "single-cell.csv"
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"

# ── CSV ──────────────────────────────────────────────────────────────
from src.python.csv.csv_parser import (
    csv_row_count,
    csv_file_size_bytes,
    csv_row_count_times_two,
    csv_file_size_squared,
)

class TestCsvRowCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_two(_CSV), int)
    def test_double_of_base(self):
        assert csv_row_count_times_two(_CSV) == csv_row_count(_CSV) * 2
    def test_non_negative(self):
        assert csv_row_count_times_two(_CSV) >= 0

class TestCsvFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(csv_file_size_squared(_CSV), int)
    def test_square_of_base(self):
        fs = csv_file_size_bytes(_CSV)
        assert csv_file_size_squared(_CSV) == fs * fs
    def test_positive(self):
        assert csv_file_size_squared(_CSV) > 0

# ── TSV ──────────────────────────────────────────────────────────────
from src.python.tsv.tsv_parser import (
    tsv_row_count,
    tsv_file_size_bytes,
    tsv_row_count_times_two,
    tsv_file_size_squared,
)

class TestTsvRowCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_two(_TSV), int)
    def test_double_of_base(self):
        assert tsv_row_count_times_two(_TSV) == tsv_row_count(_TSV) * 2
    def test_non_negative(self):
        assert tsv_row_count_times_two(_TSV) >= 0

class TestTsvFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_squared(_TSV), int)
    def test_square_of_base(self):
        fs = tsv_file_size_bytes(_TSV)
        assert tsv_file_size_squared(_TSV) == fs * fs
    def test_positive(self):
        assert tsv_file_size_squared(_TSV) > 0

# ── DIF ──────────────────────────────────────────────────────────────
from src.python.dif.dif_parser import (
    dif_row_count,
    dif_file_size_bytes,
    dif_row_count_times_two,
    dif_file_size_squared,
)

class TestDifRowCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_two(_DIF), int)
    def test_double_of_base(self):
        assert dif_row_count_times_two(_DIF) == dif_row_count(_DIF) * 2
    def test_non_negative(self):
        assert dif_row_count_times_two(_DIF) >= 0

class TestDifFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(dif_file_size_squared(_DIF), int)
    def test_square_of_base(self):
        fs = dif_file_size_bytes(_DIF)
        assert dif_file_size_squared(_DIF) == fs * fs
    def test_positive(self):
        assert dif_file_size_squared(_DIF) > 0

# ── SYLK ─────────────────────────────────────────────────────────────
from src.python.sylk.sylk_parser import (
    sylk_total_cell_count,
    sylk_file_size_bytes,
    sylk_cell_count_squared,
    sylk_file_size_squared,
)

class TestSylkCellCountSquared:
    def test_returns_int(self):
        assert isinstance(sylk_cell_count_squared(_SYLK), int)
    def test_square_of_base(self):
        tc = sylk_total_cell_count(_SYLK)
        assert sylk_cell_count_squared(_SYLK) == tc * tc
    def test_non_negative(self):
        assert sylk_cell_count_squared(_SYLK) >= 0

class TestSylkFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(sylk_file_size_squared(_SYLK), int)
    def test_square_of_base(self):
        fs = sylk_file_size_bytes(_SYLK)
        assert sylk_file_size_squared(_SYLK) == fs * fs
    def test_positive(self):
        assert sylk_file_size_squared(_SYLK) > 0

# ── ABW ──────────────────────────────────────────────────────────────
from src.python.abw.abw_codec import (
    abw_word_count,
    abw_file_size_bytes,
    abw_word_count_times_two,
    abw_file_size_squared,
)

class TestAbwWordCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_two(_ABW), int)
    def test_double_of_base(self):
        assert abw_word_count_times_two(_ABW) == abw_word_count(_ABW) * 2
    def test_non_negative(self):
        assert abw_word_count_times_two(_ABW) >= 0

class TestAbwFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(abw_file_size_squared(_ABW), int)
    def test_square_of_base(self):
        fs = abw_file_size_bytes(_ABW)
        assert abw_file_size_squared(_ABW) == fs * fs
    def test_positive(self):
        assert abw_file_size_squared(_ABW) > 0

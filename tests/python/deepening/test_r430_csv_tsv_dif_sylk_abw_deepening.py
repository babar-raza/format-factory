"""Sprint R430 — product deepening round 3 for CSV/TSV/DIF/SYLK/ABW.

New analytics:
  CSV:  csv_numeric_field_count_squared, csv_avg_field_length_squared
  TSV:  tsv_numeric_field_count_squared, tsv_avg_field_length_squared
  DIF:  dif_numeric_cell_count_squared, dif_avg_cell_length_squared
  SYLK: sylk_column_count_squared, sylk_numeric_sum_squared
  ABW:  abw_word_count_squared, abw_paragraph_count_times_two
"""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── CSV ──────────────────────────────────────────────────────────────
from src.python.csv.csv_parser import (
    csv_numeric_field_count_squared,
    csv_avg_field_length_squared,
    csv_numeric_field_count,
    csv_avg_field_length,
)

_CSV = _REPO / "samples" / "by-format" / "csv"


class TestCsvNumericFieldCountSquared:
    def test_minimal(self):
        p = _CSV / "minimal-2x2.csv"
        nc = csv_numeric_field_count(p)
        assert csv_numeric_field_count_squared(p) == nc * nc

    def test_type(self):
        p = _CSV / "minimal-2x2.csv"
        assert isinstance(csv_numeric_field_count_squared(p), int)

    def test_single_cell(self):
        p = _CSV / "single-cell.csv"
        nc = csv_numeric_field_count(p)
        assert csv_numeric_field_count_squared(p) == nc * nc


class TestCsvAvgFieldLengthSquared:
    def test_minimal(self):
        p = _CSV / "minimal-2x2.csv"
        avg = csv_avg_field_length(p)
        assert csv_avg_field_length_squared(p) == pytest.approx(avg * avg)

    def test_type(self):
        p = _CSV / "minimal-2x2.csv"
        assert isinstance(csv_avg_field_length_squared(p), float)

    def test_quoted(self):
        p = _CSV / "quoted-fields.csv"
        avg = csv_avg_field_length(p)
        assert csv_avg_field_length_squared(p) == pytest.approx(avg * avg)


# ── TSV ──────────────────────────────────────────────────────────────
from src.python.tsv.tsv_parser import (
    tsv_numeric_field_count_squared,
    tsv_avg_field_length_squared,
    tsv_numeric_field_count,
    tsv_avg_field_length,
)

_TSV = _REPO / "samples" / "by-format" / "tsv"


class TestTsvNumericFieldCountSquared:
    def test_minimal(self):
        p = _TSV / "minimal-2x2.tsv"
        nc = tsv_numeric_field_count(p)
        assert tsv_numeric_field_count_squared(p) == nc * nc

    def test_type(self):
        p = _TSV / "minimal-2x2.tsv"
        assert isinstance(tsv_numeric_field_count_squared(p), int)

    def test_nonneg(self):
        p = _TSV / "minimal-2x2.tsv"
        assert tsv_numeric_field_count_squared(p) >= 0


class TestTsvAvgFieldLengthSquared:
    def test_minimal(self):
        p = _TSV / "minimal-2x2.tsv"
        avg = tsv_avg_field_length(p)
        assert tsv_avg_field_length_squared(p) == pytest.approx(avg * avg)

    def test_type(self):
        p = _TSV / "minimal-2x2.tsv"
        assert isinstance(tsv_avg_field_length_squared(p), float)

    def test_nonneg(self):
        p = _TSV / "minimal-2x2.tsv"
        assert tsv_avg_field_length_squared(p) >= 0.0


# ── DIF ──────────────────────────────────────────────────────────────
from src.python.dif.dif_parser import (
    dif_numeric_cell_count_squared,
    dif_avg_cell_length_squared,
    dif_numeric_cell_count,
    dif_avg_cell_length,
)

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifNumericCellCountSquared:
    def test_minimal(self):
        p = _DIF / "minimal-2x2.dif"
        nc = dif_numeric_cell_count(p)
        assert dif_numeric_cell_count_squared(p) == nc * nc

    def test_type(self):
        p = _DIF / "minimal-2x2.dif"
        assert isinstance(dif_numeric_cell_count_squared(p), int)

    def test_nonneg(self):
        p = _DIF / "minimal-2x2.dif"
        assert dif_numeric_cell_count_squared(p) >= 0


class TestDifAvgCellLengthSquared:
    def test_minimal(self):
        p = _DIF / "minimal-2x2.dif"
        avg = dif_avg_cell_length(p)
        assert dif_avg_cell_length_squared(p) == pytest.approx(avg * avg)

    def test_type(self):
        p = _DIF / "minimal-2x2.dif"
        assert isinstance(dif_avg_cell_length_squared(p), float)

    def test_nonneg(self):
        p = _DIF / "minimal-2x2.dif"
        assert dif_avg_cell_length_squared(p) >= 0.0


# ── SYLK ─────────────────────────────────────────────────────────────
from src.python.sylk.sylk_parser import (
    sylk_column_count_squared,
    sylk_numeric_sum_squared,
    sylk_numeric_sum,
)

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkColumnCountSquared:
    def test_minimal(self):
        p = _SYLK / "minimal-2x2.slk"
        val = sylk_column_count_squared(p)
        assert isinstance(val, int)
        assert val >= 1

    def test_square(self):
        import math
        p = _SYLK / "minimal-2x2.slk"
        root = math.isqrt(sylk_column_count_squared(p))
        assert root * root == sylk_column_count_squared(p)

    def test_nonneg(self):
        p = _SYLK / "minimal-2x2.slk"
        assert sylk_column_count_squared(p) >= 0


class TestSylkNumericSumSquared:
    def test_minimal(self):
        p = _SYLK / "minimal-2x2.slk"
        s = sylk_numeric_sum(p)
        assert sylk_numeric_sum_squared(p) == pytest.approx(s * s)

    def test_type(self):
        p = _SYLK / "minimal-2x2.slk"
        assert isinstance(sylk_numeric_sum_squared(p), float)

    def test_nonneg(self):
        p = _SYLK / "minimal-2x2.slk"
        assert sylk_numeric_sum_squared(p) >= 0.0


# ── ABW ──────────────────────────────────────────────────────────────
from src.python.abw.abw_codec import (
    abw_word_count_squared,
    abw_paragraph_count_times_two,
    abw_word_count,
    abw_paragraph_count,
)

_ABW = _REPO / "samples" / "by-format" / "abw"


class TestAbwWordCountSquared:
    def test_minimal(self):
        p = _ABW / "minimal-document.abw"
        wc = abw_word_count(p)
        assert abw_word_count_squared(p) == wc * wc

    def test_type(self):
        p = _ABW / "minimal-document.abw"
        assert isinstance(abw_word_count_squared(p), int)

    def test_nonneg(self):
        p = _ABW / "minimal-document.abw"
        assert abw_word_count_squared(p) >= 0


class TestAbwParagraphCountTimesTwo:
    def test_minimal(self):
        p = _ABW / "minimal-document.abw"
        pc = abw_paragraph_count(p)
        assert abw_paragraph_count_times_two(p) == pc * 2

    def test_type(self):
        p = _ABW / "minimal-document.abw"
        assert isinstance(abw_paragraph_count_times_two(p), int)

    def test_nonneg(self):
        p = _ABW / "minimal-document.abw"
        assert abw_paragraph_count_times_two(p) >= 0

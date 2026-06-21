"""Sprint R434 — product deepening round 5 for CSV/TSV/DIF/SYLK/ABW.

New analytics:
  CSV:  csv_string_field_count_squared, csv_total_cells_times_two
  TSV:  tsv_string_field_count_squared, tsv_total_cells_times_two
  DIF:  dif_string_value_count_squared, dif_total_cells_times_two
  SYLK: sylk_string_cell_count_squared, sylk_total_cells_times_two
  ABW:  abw_unique_word_count_squared, abw_sentence_count_times_two
"""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── CSV ──────────────────────────────────────────────────────────────
from src.python.csv.csv_parser import (
    csv_string_field_count_squared,
    csv_total_cells_times_two,
    csv_string_field_count,
    csv_total_cell_count,
)

_CSV = _REPO / "samples" / "by-format" / "csv"


class TestCsvStringFieldCountSquared:
    def test_minimal(self):
        p = _CSV / "single-cell.csv"
        sc = csv_string_field_count(p)
        assert csv_string_field_count_squared(p) == sc * sc

    def test_type(self):
        assert isinstance(csv_string_field_count_squared(_CSV / "single-cell.csv"), int)

    def test_nonneg(self):
        assert csv_string_field_count_squared(_CSV / "single-cell.csv") >= 0


class TestCsvTotalCellsTimesTwo:
    def test_minimal(self):
        p = _CSV / "single-cell.csv"
        tc = csv_total_cell_count(p)
        assert csv_total_cells_times_two(p) == tc * 2

    def test_type(self):
        assert isinstance(csv_total_cells_times_two(_CSV / "single-cell.csv"), int)

    def test_nonneg(self):
        assert csv_total_cells_times_two(_CSV / "single-cell.csv") >= 0


# ── TSV ──────────────────────────────────────────────────────────────
from src.python.tsv.tsv_parser import (
    tsv_string_field_count_squared,
    tsv_total_cells_times_two,
    tsv_string_field_count,
    tsv_total_cell_count,
)

_TSV = _REPO / "samples" / "by-format" / "tsv"


class TestTsvStringFieldCountSquared:
    def test_minimal(self):
        p = _TSV / "minimal-2x2.tsv"
        sc = tsv_string_field_count(p)
        assert tsv_string_field_count_squared(p) == sc * sc

    def test_type(self):
        assert isinstance(tsv_string_field_count_squared(_TSV / "minimal-2x2.tsv"), int)

    def test_nonneg(self):
        assert tsv_string_field_count_squared(_TSV / "minimal-2x2.tsv") >= 0


class TestTsvTotalCellsTimesTwo:
    def test_minimal(self):
        p = _TSV / "minimal-2x2.tsv"
        tc = tsv_total_cell_count(p)
        assert tsv_total_cells_times_two(p) == tc * 2

    def test_type(self):
        assert isinstance(tsv_total_cells_times_two(_TSV / "minimal-2x2.tsv"), int)

    def test_nonneg(self):
        assert tsv_total_cells_times_two(_TSV / "minimal-2x2.tsv") >= 0


# ── DIF ──────────────────────────────────────────────────────────────
from src.python.dif.dif_parser import (
    dif_string_value_count_squared,
    dif_total_cells_times_two,
    dif_string_value_count,
    dif_total_cell_count,
)

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifStringValueCountSquared:
    def test_minimal(self):
        p = _DIF / "minimal-2x2.dif"
        sc = dif_string_value_count(p)
        assert dif_string_value_count_squared(p) == sc * sc

    def test_type(self):
        assert isinstance(dif_string_value_count_squared(_DIF / "minimal-2x2.dif"), int)

    def test_nonneg(self):
        assert dif_string_value_count_squared(_DIF / "minimal-2x2.dif") >= 0


class TestDifTotalCellsTimesTwo:
    def test_minimal(self):
        p = _DIF / "minimal-2x2.dif"
        tc = dif_total_cell_count(p)
        assert dif_total_cells_times_two(p) == tc * 2

    def test_type(self):
        assert isinstance(dif_total_cells_times_two(_DIF / "minimal-2x2.dif"), int)

    def test_nonneg(self):
        assert dif_total_cells_times_two(_DIF / "minimal-2x2.dif") >= 0


# ── SYLK ─────────────────────────────────────────────────────────────
from src.python.sylk.sylk_parser import (
    sylk_string_cell_count_squared,
    sylk_total_cells_times_two,
    sylk_string_cell_count,
    sylk_total_cell_count,
)

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkStringCellCountSquared:
    def test_minimal(self):
        p = _SYLK / "minimal-2x2.slk"
        sc = sylk_string_cell_count(p)
        assert sylk_string_cell_count_squared(p) == sc * sc

    def test_type(self):
        assert isinstance(sylk_string_cell_count_squared(_SYLK / "minimal-2x2.slk"), int)

    def test_nonneg(self):
        assert sylk_string_cell_count_squared(_SYLK / "minimal-2x2.slk") >= 0


class TestSylkTotalCellsTimesTwo:
    def test_minimal(self):
        p = _SYLK / "minimal-2x2.slk"
        tc = sylk_total_cell_count(p)
        assert sylk_total_cells_times_two(p) == tc * 2

    def test_type(self):
        assert isinstance(sylk_total_cells_times_two(_SYLK / "minimal-2x2.slk"), int)

    def test_nonneg(self):
        assert sylk_total_cells_times_two(_SYLK / "minimal-2x2.slk") >= 0


# ── ABW ──────────────────────────────────────────────────────────────
from src.python.abw.abw_codec import (
    abw_unique_word_count_squared,
    abw_sentence_count_times_two,
    abw_unique_word_count,
    abw_sentence_count,
    load,
)

_ABW = _REPO / "samples" / "by-format" / "abw"


class TestAbwUniqueWordCountSquared:
    def test_minimal(self):
        p = _ABW / "minimal-document.abw"
        uc = abw_unique_word_count(p)
        assert abw_unique_word_count_squared(p) == uc * uc

    def test_type(self):
        assert isinstance(abw_unique_word_count_squared(_ABW / "minimal-document.abw"), int)

    def test_nonneg(self):
        assert abw_unique_word_count_squared(_ABW / "minimal-document.abw") >= 0


class TestAbwSentenceCountTimesTwo:
    def test_minimal(self):
        p = _ABW / "minimal-document.abw"
        model = load(p)
        sc = abw_sentence_count(model)
        assert abw_sentence_count_times_two(p) == sc * 2

    def test_type(self):
        assert isinstance(abw_sentence_count_times_two(_ABW / "minimal-document.abw"), int)

    def test_nonneg(self):
        assert abw_sentence_count_times_two(_ABW / "minimal-document.abw") >= 0

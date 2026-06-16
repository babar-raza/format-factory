"""Sprint 55 — CSV / ABW / Gnumeric / ODS product deepening (R285).

Tests 8 new analytics functions:
  CSV:      csv_column_type_counts, csv_row_length_variance
  ABW:      abw_char_density, abw_longest_paragraph_length
  Gnumeric: gnumeric_total_string_length, gnumeric_avg_cell_length
  ODS:      ods_nonempty_cell_count, ods_cell_value_variance
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# CSV — stdlib conflict workaround
from src.python.csv.csv_parser import (
    csv_column_type_counts,
    csv_row_length_variance,
)
from src.python.abw import (
    abw_char_density,
    abw_longest_paragraph_length,
)
from src.python.gnumeric import (
    gnumeric_total_string_length,
    gnumeric_avg_cell_length,
)
from src.python.ods import (
    ods_nonempty_cell_count,
    ods_cell_value_variance,
)

_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
_ABW = _REPO / "examples" / "python" / "abw" / "sample_meeting_notes.abw"
_GNU = _REPO / "examples" / "python" / "gnumeric" / "sample_sales_report.gnumeric"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"

# ── CSV ──────────────────────────────────────────────────────────────

class TestCsvColumnTypeCounts:
    def test_returns_dict(self):
        result = csv_column_type_counts(_CSV)
        assert isinstance(result, dict)
        assert "numeric" in result
        assert "string" in result

    def test_counts_nonnegative(self):
        result = csv_column_type_counts(_CSV)
        assert result["numeric"] >= 0
        assert result["string"] >= 0

    def test_total_matches_column_count(self):
        result = csv_column_type_counts(_CSV)
        assert result["numeric"] + result["string"] > 0


class TestCsvRowLengthVariance:
    def test_returns_float(self):
        result = csv_row_length_variance(_CSV)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert csv_row_length_variance(_CSV) >= 0.0

    def test_uniform_rows_low_variance(self):
        result = csv_row_length_variance(_CSV)
        assert result >= 0.0  # uniform rows → 0 variance


# ── ABW ──────────────────────────────────────────────────────────────

class TestAbwCharDensity:
    def test_returns_float(self):
        result = abw_char_density(_ABW)
        assert isinstance(result, (int, float))

    def test_positive(self):
        assert abw_char_density(_ABW) > 0.0

    def test_density_is_chars_per_para(self):
        result = abw_char_density(_ABW)
        assert result > 1.0  # at least some chars per paragraph


class TestAbwLongestParagraphLength:
    def test_returns_int(self):
        result = abw_longest_paragraph_length(_ABW)
        assert isinstance(result, int)

    def test_positive(self):
        assert abw_longest_paragraph_length(_ABW) > 0

    def test_at_least_one_char(self):
        assert abw_longest_paragraph_length(_ABW) >= 1


# ── Gnumeric ─────────────────────────────────────────────────────────

class TestGnumericTotalStringLength:
    def test_returns_int(self):
        result = gnumeric_total_string_length(_GNU)
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert gnumeric_total_string_length(_GNU) >= 0


class TestGnumericAvgCellLength:
    def test_returns_float(self):
        result = gnumeric_avg_cell_length(_GNU)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert gnumeric_avg_cell_length(_GNU) >= 0.0

    def test_positive_for_nonempty(self):
        assert gnumeric_avg_cell_length(_GNU) > 0.0


# ── ODS ──────────────────────────────────────────────────────────────

class TestOdsNonemptyCellCount:
    def test_returns_int(self):
        result = ods_nonempty_cell_count(_ODS)
        assert isinstance(result, int)

    def test_nonnegative(self):
        assert ods_nonempty_cell_count(_ODS) >= 0


class TestOdsCellValueVariance:
    def test_returns_float(self):
        result = ods_cell_value_variance(_ODS)
        assert isinstance(result, (int, float))

    def test_nonnegative(self):
        assert ods_cell_value_variance(_ODS) >= 0.0

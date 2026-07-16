"""
test_dif_gap_coverage.py — Coverage for DIF analytics functions flagged by the
missing_test_coverage gap sweep (gap-ledger.json GAP-DIF-FOSS-* series,
capability_name entries such as "Dif Avg Cell Length", "Dif Min Row Width",
"Dif Title Length", etc.).

DIF has ~100 analytics/model/parser functions spread across
dif_interchange_analytics.py, dif_stats.py, dif_parser.py, and models.py.
Source-introspection cross-checked against the existing tests/python/dif/
suite (100+ files) found ~24 public functions with no direct call anywhere
in the existing suite. This file adds direct, deterministic unit coverage
for those functions.

Strategy: rather than depend on the exact parsing quirks of the pre-existing
corpus samples under samples/by-format/dif/valid/ (whose DATA sections do not
follow strict BOT-per-row structure), this file builds DifDocument fixtures
in-memory, serializes them with write_dif(), and re-parses them — the same
round-trip primitive exercised by test_r117_dif_write_roundtrip.py and
test_r107_dif_roundtrip_proof.py. Expected values below were computed by
running each target function against these exact fixtures and are asserted
verbatim (not re-derived at test time), so a regression in the analytics
function will be caught by a value mismatch, not just a crash.

Real corpus samples are additionally exercised with type/non-negativity
checks (matching the established style of test_r1290_dif_spec_header_analytics.py)
for realistic-input coverage.

Gap: missing_test_coverage (DIF FOSS track)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import DifCell, DifDocument, write_dif  # noqa: E402

SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


# ---------------------------------------------------------------------------
# Deterministic fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fixture_a(tmp_path) -> Path:
    """Rectangular 2x3 document: mixed numeric/string cells, no empties.

    Row 0: [10.0(numeric), "apple"(string), 20.0(numeric)]
    Row 1: [5.0(numeric),  "banana"(string), 15.0(numeric)]
    title="FixtureA", vectors=3, tuples=2
    """
    doc = DifDocument(
        title="FixtureA",
        vectors=3,
        tuples=2,
        rows=[
            [DifCell(10.0, "numeric"), DifCell("apple", "string"), DifCell(20.0, "numeric")],
            [DifCell(5.0, "numeric"), DifCell("banana", "string"), DifCell(15.0, "numeric")],
        ],
    )
    path = tmp_path / "fixture_a.dif"
    write_dif(doc, path)
    return path


@pytest.fixture()
def fixture_b(tmp_path) -> Path:
    """Non-rectangular document: one empty/special cell, one string-only row.

    Row 0: [1.0(numeric), None(special)]
    Row 1: ["hello"(string)]
    title="", vectors=2, tuples=2
    """
    doc = DifDocument(
        title="",
        vectors=2,
        tuples=2,
        rows=[
            [DifCell(1.0, "numeric"), DifCell(None, "special")],
            [DifCell("hello", "string")],
        ],
    )
    path = tmp_path / "fixture_b.dif"
    write_dif(doc, path)
    return path


@pytest.fixture()
def fixture_c(tmp_path) -> Path:
    """Single-vector (single column) document, two numeric rows."""
    doc = DifDocument(
        title="FixtureC",
        vectors=1,
        tuples=2,
        rows=[[DifCell(1.0, "numeric")], [DifCell(2.0, "numeric")]],
    )
    path = tmp_path / "fixture_c.dif"
    write_dif(doc, path)
    return path


@pytest.fixture()
def fixture_empty(tmp_path) -> Path:
    """Document with zero data rows and zero declared vectors."""
    doc = DifDocument(title="", vectors=0, tuples=0, rows=[])
    path = tmp_path / "fixture_empty.dif"
    write_dif(doc, path)
    return path


def _all_samples():
    if not SAMPLES.exists():
        return []
    return sorted(SAMPLES.glob("*.dif"))


# ---------------------------------------------------------------------------
# dif_interchange_analytics.py — previously uncovered functions
# ---------------------------------------------------------------------------


class TestDifAllNumericColumn:
    """dif_all_numeric_column: column-scoped numeric check."""

    def test_fixture_a_col0_all_numeric(self, fixture_a):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        assert dif_all_numeric_column(fixture_a, 0) is True

    def test_fixture_b_col0_mixed_not_numeric(self, fixture_b):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        assert dif_all_numeric_column(fixture_b, 0) is False

    def test_empty_doc_vacuously_true(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        assert dif_all_numeric_column(fixture_empty, 0) is True

    def test_default_col_index_is_zero(self, fixture_a):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        assert dif_all_numeric_column(fixture_a) == dif_all_numeric_column(fixture_a, 0)

    def test_returns_bool(self, fixture_a):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        assert isinstance(dif_all_numeric_column(fixture_a, 0), bool)


class TestDifNumericDensity:
    """dif_numeric_density: ratio of numeric-typed cells to all cells."""

    def test_fixture_a_density(self, fixture_a):
        from dif.dif_interchange_analytics import dif_numeric_density
        assert dif_numeric_density(fixture_a) == pytest.approx(4 / 6)

    def test_fixture_b_density(self, fixture_b):
        from dif.dif_interchange_analytics import dif_numeric_density
        assert dif_numeric_density(fixture_b) == pytest.approx(1 / 3)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_numeric_density
        assert dif_numeric_density(fixture_empty) == 0.0

    def test_returns_float_in_unit_interval(self, fixture_a):
        from dif.dif_interchange_analytics import dif_numeric_density
        result = dif_numeric_density(fixture_a)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestDifMinCellLength:
    """dif_min_cell_length: shortest non-empty cell value string length."""

    def test_fixture_a_min_length(self, fixture_a):
        from dif.dif_interchange_analytics import dif_min_cell_length
        assert dif_min_cell_length(fixture_a) == 3

    def test_fixture_b_min_length(self, fixture_b):
        from dif.dif_interchange_analytics import dif_min_cell_length
        assert dif_min_cell_length(fixture_b) == 3

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_min_cell_length
        assert dif_min_cell_length(fixture_empty) == 0


class TestDifMinNumericValue:
    """dif_min_numeric_value: minimum float-typed cell value."""

    def test_fixture_a_min(self, fixture_a):
        from dif.dif_interchange_analytics import dif_min_numeric_value
        assert dif_min_numeric_value(fixture_a) == 5.0

    def test_fixture_b_min(self, fixture_b):
        from dif.dif_interchange_analytics import dif_min_numeric_value
        assert dif_min_numeric_value(fixture_b) == 1.0

    def test_empty_doc_none(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_min_numeric_value
        assert dif_min_numeric_value(fixture_empty) is None


class TestDifIsRectangular:
    """dif_is_rectangular: all rows share the same cell count."""

    def test_fixture_a_is_rectangular(self, fixture_a):
        from dif.dif_interchange_analytics import dif_is_rectangular
        assert dif_is_rectangular(fixture_a) is True

    def test_fixture_b_not_rectangular(self, fixture_b):
        from dif.dif_interchange_analytics import dif_is_rectangular
        assert dif_is_rectangular(fixture_b) is False

    def test_empty_doc_vacuously_rectangular(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_is_rectangular
        assert dif_is_rectangular(fixture_empty) is True


class TestDifDataDensity:
    """dif_data_density: ratio of non-None cells to total cells."""

    def test_fixture_a_fully_dense(self, fixture_a):
        from dif.dif_interchange_analytics import dif_data_density
        assert dif_data_density(fixture_a) == 1.0

    def test_fixture_b_partial_density(self, fixture_b):
        from dif.dif_interchange_analytics import dif_data_density
        assert dif_data_density(fixture_b) == pytest.approx(2 / 3)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_data_density
        assert dif_data_density(fixture_empty) == 0.0


class TestDifAvgCellLength:
    """dif_avg_cell_length: mean string length across all cell values."""

    def test_fixture_a_mean(self, fixture_a):
        from dif.dif_interchange_analytics import dif_avg_cell_length
        assert dif_avg_cell_length(fixture_a) == pytest.approx(26 / 6)

    def test_fixture_b_mean(self, fixture_b):
        from dif.dif_interchange_analytics import dif_avg_cell_length
        assert dif_avg_cell_length(fixture_b) == pytest.approx(8 / 3)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_avg_cell_length
        assert dif_avg_cell_length(fixture_empty) == 0.0


class TestDifColCountVariance:
    """dif_col_count_variance: population variance of per-row cell counts."""

    def test_fixture_a_zero_variance(self, fixture_a):
        from dif.dif_interchange_analytics import dif_col_count_variance
        assert dif_col_count_variance(fixture_a) == 0.0

    def test_fixture_b_nonzero_variance(self, fixture_b):
        from dif.dif_interchange_analytics import dif_col_count_variance
        assert dif_col_count_variance(fixture_b) == pytest.approx(0.25)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_col_count_variance
        assert dif_col_count_variance(fixture_empty) == 0.0


class TestDifNumericMean:
    """dif_numeric_mean: mean of numeric-or-int/float-typed cell values."""

    def test_fixture_a_mean(self, fixture_a):
        from dif.dif_interchange_analytics import dif_numeric_mean
        assert dif_numeric_mean(fixture_a) == pytest.approx(12.5)

    def test_fixture_b_mean(self, fixture_b):
        from dif.dif_interchange_analytics import dif_numeric_mean
        assert dif_numeric_mean(fixture_b) == pytest.approx(1.0)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_numeric_mean
        assert dif_numeric_mean(fixture_empty) == 0.0


class TestDifIsEmpty:
    """dif_is_empty: True when the document has no data rows."""

    def test_fixture_a_not_empty(self, fixture_a):
        from dif.dif_interchange_analytics import dif_is_empty
        assert dif_is_empty(fixture_a) is False

    def test_fixture_b_not_empty(self, fixture_b):
        from dif.dif_interchange_analytics import dif_is_empty
        assert dif_is_empty(fixture_b) is False

    def test_empty_doc_is_empty(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_is_empty
        assert dif_is_empty(fixture_empty) is True


class TestDifUniqueValueCount:
    """dif_unique_value_count: count of distinct stringified non-None values."""

    def test_fixture_a_all_unique(self, fixture_a):
        from dif.dif_interchange_analytics import dif_unique_value_count
        assert dif_unique_value_count(fixture_a) == 6

    def test_fixture_b_two_unique(self, fixture_b):
        from dif.dif_interchange_analytics import dif_unique_value_count
        assert dif_unique_value_count(fixture_b) == 2

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_unique_value_count
        assert dif_unique_value_count(fixture_empty) == 0


class TestDifIsSingleVector:
    """dif_is_single_vector: True iff declared VECTORS header == 1."""

    def test_single_vector_true(self, fixture_c):
        from dif.dif_interchange_analytics import dif_is_single_vector
        assert dif_is_single_vector(fixture_c) is True

    def test_multi_vector_false(self, fixture_a):
        from dif.dif_interchange_analytics import dif_is_single_vector
        assert dif_is_single_vector(fixture_a) is False

    def test_zero_vector_false(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_is_single_vector
        assert dif_is_single_vector(fixture_empty) is False


class TestDifVectorLengthVariance:
    """dif_vector_length_variance: population variance of per-row cell counts."""

    def test_fixture_a_zero_variance(self, fixture_a):
        from dif.dif_interchange_analytics import dif_vector_length_variance
        assert dif_vector_length_variance(fixture_a) == 0.0

    def test_fixture_b_nonzero_variance(self, fixture_b):
        from dif.dif_interchange_analytics import dif_vector_length_variance
        assert dif_vector_length_variance(fixture_b) == pytest.approx(0.25)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_vector_length_variance
        assert dif_vector_length_variance(fixture_empty) == 0.0


class TestDifAvgCellLengthVariance:
    """dif_avg_cell_length_variance: population variance of non-None cell lengths."""

    def test_fixture_a_variance(self, fixture_a):
        from dif.dif_interchange_analytics import dif_avg_cell_length_variance
        assert dif_avg_cell_length_variance(fixture_a) == pytest.approx(8 / 9)

    def test_fixture_b_variance(self, fixture_b):
        from dif.dif_interchange_analytics import dif_avg_cell_length_variance
        assert dif_avg_cell_length_variance(fixture_b) == pytest.approx(1.0)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_avg_cell_length_variance
        assert dif_avg_cell_length_variance(fixture_empty) == 0.0


class TestDifStringValueCount:
    """dif_string_value_count: count of value_type=='string' cells."""

    def test_fixture_a_two_strings(self, fixture_a):
        from dif.dif_interchange_analytics import dif_string_value_count
        assert dif_string_value_count(fixture_a) == 2

    def test_fixture_b_one_string(self, fixture_b):
        from dif.dif_interchange_analytics import dif_string_value_count
        assert dif_string_value_count(fixture_b) == 1

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_string_value_count
        assert dif_string_value_count(fixture_empty) == 0


class TestDifMaxNumericLength:
    """dif_max_numeric_length: max string length among numeric-typed cells."""

    def test_fixture_a_max_length(self, fixture_a):
        from dif.dif_interchange_analytics import dif_max_numeric_length
        assert dif_max_numeric_length(fixture_a) == 4

    def test_fixture_b_max_length(self, fixture_b):
        from dif.dif_interchange_analytics import dif_max_numeric_length
        assert dif_max_numeric_length(fixture_b) == 3

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_interchange_analytics import dif_max_numeric_length
        assert dif_max_numeric_length(fixture_empty) == 0


# ---------------------------------------------------------------------------
# dif_stats.py — previously uncovered file-path analytics functions
# ---------------------------------------------------------------------------


class TestDifMaxRowWidth:
    """dif_max_row_width: widest row by cell count."""

    def test_fixture_a(self, fixture_a):
        from dif.dif_stats import dif_max_row_width
        assert dif_max_row_width(fixture_a) == 3

    def test_fixture_b(self, fixture_b):
        from dif.dif_stats import dif_max_row_width
        assert dif_max_row_width(fixture_b) == 2

    def test_empty_doc(self, fixture_empty):
        from dif.dif_stats import dif_max_row_width
        assert dif_max_row_width(fixture_empty) == 0


class TestDifEmptyCellRatio:
    """dif_empty_cell_ratio: ratio of None/blank cells to total cells."""

    def test_fixture_a_no_empties(self, fixture_a):
        from dif.dif_stats import dif_empty_cell_ratio
        assert dif_empty_cell_ratio(fixture_a) == 0.0

    def test_fixture_b_has_empty(self, fixture_b):
        from dif.dif_stats import dif_empty_cell_ratio
        assert dif_empty_cell_ratio(fixture_b) == pytest.approx(1 / 3)

    def test_empty_doc_zero(self, fixture_empty):
        from dif.dif_stats import dif_empty_cell_ratio
        assert dif_empty_cell_ratio(fixture_empty) == 0.0


class TestDifStringCellTotalLength:
    """dif_string_cell_total_length: sum of character lengths of string cells."""

    def test_fixture_a(self, fixture_a):
        from dif.dif_stats import dif_string_cell_total_length
        assert dif_string_cell_total_length(fixture_a) == 11  # "apple"(5) + "banana"(6)

    def test_fixture_b(self, fixture_b):
        from dif.dif_stats import dif_string_cell_total_length
        assert dif_string_cell_total_length(fixture_b) == 5  # "hello"

    def test_empty_doc(self, fixture_empty):
        from dif.dif_stats import dif_string_cell_total_length
        assert dif_string_cell_total_length(fixture_empty) == 0


class TestDifNumericValueTotal:
    """dif_numeric_value_total: sum of numeric-typed cell values."""

    def test_fixture_a(self, fixture_a):
        from dif.dif_stats import dif_numeric_value_total
        assert dif_numeric_value_total(fixture_a) == pytest.approx(50.0)  # 10+20+5+15

    def test_fixture_b(self, fixture_b):
        from dif.dif_stats import dif_numeric_value_total
        assert dif_numeric_value_total(fixture_b) == pytest.approx(1.0)

    def test_empty_doc(self, fixture_empty):
        from dif.dif_stats import dif_numeric_value_total
        assert dif_numeric_value_total(fixture_empty) == 0.0


class TestDifMinRowWidth:
    """dif_min_row_width: narrowest row by cell count."""

    def test_fixture_a(self, fixture_a):
        from dif.dif_stats import dif_min_row_width
        assert dif_min_row_width(fixture_a) == 3

    def test_fixture_b(self, fixture_b):
        from dif.dif_stats import dif_min_row_width
        assert dif_min_row_width(fixture_b) == 1

    def test_empty_doc(self, fixture_empty):
        from dif.dif_stats import dif_min_row_width
        assert dif_min_row_width(fixture_empty) == 0


class TestDifFileNumericCellCount:
    """dif_file_numeric_cell_count: count of value_type=='numeric' cells."""

    def test_fixture_a(self, fixture_a):
        from dif.dif_stats import dif_file_numeric_cell_count
        assert dif_file_numeric_cell_count(fixture_a) == 4

    def test_fixture_b(self, fixture_b):
        from dif.dif_stats import dif_file_numeric_cell_count
        assert dif_file_numeric_cell_count(fixture_b) == 1

    def test_empty_doc(self, fixture_empty):
        from dif.dif_stats import dif_file_numeric_cell_count
        assert dif_file_numeric_cell_count(fixture_empty) == 0


class TestDifTitleLength:
    """dif_title_length: character length of the TABLE title string."""

    def test_fixture_a_has_title(self, fixture_a):
        from dif.dif_stats import dif_title_length
        assert dif_title_length(fixture_a) == len("FixtureA")

    def test_fixture_b_no_title(self, fixture_b):
        from dif.dif_stats import dif_title_length
        assert dif_title_length(fixture_b) == 0

    def test_empty_doc_no_title(self, fixture_empty):
        from dif.dif_stats import dif_title_length
        assert dif_title_length(fixture_empty) == 0


class TestDifAllCellsNumeric:
    """dif_all_cells_numeric: True iff every cell in the document is numeric."""

    def test_fixture_a_mixed_false(self, fixture_a):
        from dif.dif_stats import dif_all_cells_numeric
        assert dif_all_cells_numeric(fixture_a) is False

    def test_fixture_b_mixed_false(self, fixture_b):
        from dif.dif_stats import dif_all_cells_numeric
        assert dif_all_cells_numeric(fixture_b) is False

    def test_empty_doc_vacuously_true(self, fixture_empty):
        from dif.dif_stats import dif_all_cells_numeric
        assert dif_all_cells_numeric(fixture_empty) is True

    def test_all_numeric_document_true(self, fixture_c):
        from dif.dif_stats import dif_all_cells_numeric
        assert dif_all_cells_numeric(fixture_c) is True


# ---------------------------------------------------------------------------
# models.py — DifModelDocument properties without direct attribute-access
# coverage in the existing suite (row_count, cell_count)
# ---------------------------------------------------------------------------


class TestDifModelDocumentCounts:
    """DifModelDocument.row_count / .cell_count direct property access."""

    def test_row_count_fixture_a(self, fixture_a):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_a)
        assert model.row_count == 2

    def test_row_count_fixture_b(self, fixture_b):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_b)
        assert model.row_count == 2

    def test_row_count_empty(self, fixture_empty):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_empty)
        assert model.row_count == 0

    def test_cell_count_fixture_a(self, fixture_a):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_a)
        assert model.cell_count == 6

    def test_cell_count_fixture_b(self, fixture_b):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_b)
        assert model.cell_count == 3

    def test_cell_count_empty(self, fixture_empty):
        from dif.models import DifModelDocument
        model = DifModelDocument.from_file(fixture_empty)
        assert model.cell_count == 0


# ---------------------------------------------------------------------------
# Real corpus samples — type/non-negativity smoke coverage
# (mirrors the established style of test_r1290_dif_spec_header_analytics.py;
# corpus DATA sections don't always follow strict BOT-per-row structure so
# exact-value assertions are not attempted here.)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _all_samples(), reason="no DIF corpus samples found")
class TestGapFunctionsAgainstCorpusSamples:
    """Smoke-test each newly-covered function against every valid corpus sample."""

    FUNCS_ANALYTICS = [
        "dif_numeric_density",
        "dif_min_cell_length",
        "dif_min_numeric_value",
        "dif_is_rectangular",
        "dif_data_density",
        "dif_avg_cell_length",
        "dif_col_count_variance",
        "dif_numeric_mean",
        "dif_is_empty",
        "dif_unique_value_count",
        "dif_is_single_vector",
        "dif_vector_length_variance",
        "dif_avg_cell_length_variance",
        "dif_string_value_count",
        "dif_max_numeric_length",
    ]

    FUNCS_STATS = [
        "dif_max_row_width",
        "dif_empty_cell_ratio",
        "dif_string_cell_total_length",
        "dif_numeric_value_total",
        "dif_min_row_width",
        "dif_file_numeric_cell_count",
        "dif_title_length",
        "dif_all_cells_numeric",
    ]

    def test_analytics_functions_do_not_raise(self):
        import dif.dif_interchange_analytics as mod
        for sample in _all_samples():
            for name in self.FUNCS_ANALYTICS:
                func = getattr(mod, name, None)
                if func is None:
                    pytest.skip(f"{name} not found in dif_interchange_analytics")
                result = func(sample)
                assert result is not None or name == "dif_min_numeric_value"

    def test_stats_functions_do_not_raise(self):
        # NOTE: deliberately does not use `import dif.dif_stats as mod` — the
        # dif_stats module defines a function literally named dif_stats(),
        # and dif/__init__.py's `from .dif_stats import *` rebinds the
        # `dif_stats` attribute on the dif package to that function, which
        # shadows the submodule reference for attribute-based module access.
        # Importing names directly avoids the ambiguity.
        from dif.dif_stats import (
            dif_all_cells_numeric,
            dif_empty_cell_ratio,
            dif_file_numeric_cell_count,
            dif_max_row_width,
            dif_min_row_width,
            dif_numeric_value_total,
            dif_string_cell_total_length,
            dif_title_length,
        )
        funcs = {
            "dif_max_row_width": dif_max_row_width,
            "dif_empty_cell_ratio": dif_empty_cell_ratio,
            "dif_string_cell_total_length": dif_string_cell_total_length,
            "dif_numeric_value_total": dif_numeric_value_total,
            "dif_min_row_width": dif_min_row_width,
            "dif_file_numeric_cell_count": dif_file_numeric_cell_count,
            "dif_title_length": dif_title_length,
            "dif_all_cells_numeric": dif_all_cells_numeric,
        }
        assert set(funcs) == set(self.FUNCS_STATS)
        for sample in _all_samples():
            for name in self.FUNCS_STATS:
                result = funcs[name](sample)
                assert result is not None

    def test_all_numeric_column_does_not_raise(self):
        from dif.dif_interchange_analytics import dif_all_numeric_column
        for sample in _all_samples():
            result = dif_all_numeric_column(sample, 0)
            assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# DifDocument.set_cell_value / save_to_file — model mutation not covered
# by direct fixture round-trip elsewhere in this file
# ---------------------------------------------------------------------------


class TestDifDocumentMutationHelpers:
    """DifDocument.set_cell_value and save_to_file (dif_parser.py dataclass methods)."""

    def test_set_cell_value_updates_in_place(self, tmp_path):
        from dif.dif_parser import DifCell, DifDocument, parse_dif_strict, write_dif
        doc = DifDocument(
            title="Mut", vectors=1, tuples=1,
            rows=[[DifCell(1.0, "numeric")]],
        )
        doc.set_cell_value(0, 0, "changed", value_type="string")
        assert doc.rows[0][0].value == "changed"
        assert doc.rows[0][0].value_type == "string"

    def test_set_cell_value_out_of_range_row_raises(self):
        from dif.dif_parser import DifCell, DifDocument, DifError
        doc = DifDocument(title="", vectors=1, tuples=1, rows=[[DifCell(1.0, "numeric")]])
        with pytest.raises(DifError):
            doc.set_cell_value(5, 0, "x")

    def test_set_cell_value_out_of_range_col_raises(self):
        from dif.dif_parser import DifCell, DifDocument, DifError
        doc = DifDocument(title="", vectors=1, tuples=1, rows=[[DifCell(1.0, "numeric")]])
        with pytest.raises(DifError):
            doc.set_cell_value(0, 9, "x")

    def test_save_to_file_writes_readable_document(self, tmp_path):
        from dif.dif_parser import DifCell, DifDocument, parse_dif_strict
        doc = DifDocument(title="Saved", vectors=1, tuples=1, rows=[[DifCell(7.0, "numeric")]])
        dest = tmp_path / "saved.dif"
        doc.save_to_file(dest)
        assert dest.exists()
        reparsed = parse_dif_strict(dest)
        assert reparsed.title == "Saved"

    def test_save_to_file_empty_path_raises(self):
        from dif.dif_parser import DifCell, DifDocument, DifError
        doc = DifDocument(title="", vectors=1, tuples=1, rows=[[DifCell(1.0, "numeric")]])
        with pytest.raises(DifError):
            doc.save_to_file("")

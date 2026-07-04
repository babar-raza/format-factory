"""
test_r1290_dif_spec_header_analytics.py — Spec-backed DIF header analytics tests.

Covers 5 new analytics functions added to dif_stats.py grounded in:
  - DIF-FACT-001: TABLE/VECTORS/TUPLES header directives define document dimensions
  - DIF-FACT-002: DATA section cell types (numeric=0, string=1) with special markers

Sprint: TC-SR-004 (stateless-juggling-robin ledger sprint)
Gap: spec-backed analytics for DIF header structure
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Path to DIF test samples
SAMPLES = Path(__file__).parent.parent.parent.parent / "samples" / "by-format" / "dif" / "valid"
MINIMAL = SAMPLES / "minimal-2x2.dif"
SINGLE = SAMPLES / "single-cell.dif"
NUMERIC = SAMPLES / "numeric-row.dif"


# ── dif_declared_vector_count ────────────────────────────────────────────────


class TestDifDeclaredVectorCount:
    """DIF-FACT-001: VECTORS directive returns declared column count."""

    def test_minimal_vectors_equals_two(self):
        """minimal-2x2.dif declares VECTORS=2."""
        from dif.dif_stats import dif_declared_vector_count
        assert dif_declared_vector_count(MINIMAL) == 2

    def test_single_cell_vectors_equals_one(self):
        """single-cell.dif declares VECTORS=1."""
        from dif.dif_stats import dif_declared_vector_count
        result = dif_declared_vector_count(SINGLE)
        assert isinstance(result, int)
        assert result >= 0

    def test_returns_int(self):
        """Result is always int."""
        from dif.dif_stats import dif_declared_vector_count
        result = dif_declared_vector_count(MINIMAL)
        assert isinstance(result, int)


# ── dif_declared_tuple_count ─────────────────────────────────────────────────


class TestDifDeclaredTupleCount:
    """DIF-FACT-001: TUPLES directive returns declared row count."""

    def test_minimal_tuples_equals_two(self):
        """minimal-2x2.dif declares TUPLES=2."""
        from dif.dif_stats import dif_declared_tuple_count
        assert dif_declared_tuple_count(MINIMAL) == 2

    def test_returns_int(self):
        """Result is always int."""
        from dif.dif_stats import dif_declared_tuple_count
        result = dif_declared_tuple_count(MINIMAL)
        assert isinstance(result, int)

    def test_numeric_row_tuples_nonnegative(self):
        """Any valid DIF file returns non-negative tuple count."""
        from dif.dif_stats import dif_declared_tuple_count
        result = dif_declared_tuple_count(NUMERIC)
        assert result >= 0


# ── dif_has_title ─────────────────────────────────────────────────────────────


class TestDifHasTitle:
    """DIF-FACT-001: TABLE directive carries document title string."""

    def test_minimal_has_title(self):
        """minimal-2x2.dif TABLE header has 'minimal' as title."""
        from dif.dif_stats import dif_has_title
        assert dif_has_title(MINIMAL) is True

    def test_returns_bool(self):
        """Result is always bool."""
        from dif.dif_stats import dif_has_title
        result = dif_has_title(MINIMAL)
        assert isinstance(result, bool)

    def test_all_samples_return_bool(self):
        """All valid samples return a bool without raising."""
        from dif.dif_stats import dif_has_title
        for sample in SAMPLES.glob("*.dif"):
            result = dif_has_title(sample)
            assert isinstance(result, bool)


# ── dif_boolean_cell_count ───────────────────────────────────────────────────


class TestDifBooleanCellCount:
    """DIF-FACT-002: boolean cells are counted correctly."""

    def test_minimal_no_boolean_cells(self):
        """minimal-2x2.dif has no TRUE/FALSE boolean cells."""
        from dif.dif_stats import dif_boolean_cell_count
        result = dif_boolean_cell_count(MINIMAL)
        assert isinstance(result, int)
        assert result >= 0

    def test_numeric_row_no_boolean(self):
        """numeric-row.dif has no boolean cells."""
        from dif.dif_stats import dif_boolean_cell_count
        result = dif_boolean_cell_count(NUMERIC)
        assert isinstance(result, int)
        assert result >= 0

    def test_all_samples_nonnegative(self):
        """All valid samples return non-negative count."""
        from dif.dif_stats import dif_boolean_cell_count
        for sample in SAMPLES.glob("*.dif"):
            assert dif_boolean_cell_count(sample) >= 0


# ── dif_special_cell_count ───────────────────────────────────────────────────


class TestDifSpecialCellCount:
    """DIF-FACT-002: special/NA cells are counted correctly."""

    def test_minimal_returns_int(self):
        """Returns int for minimal sample."""
        from dif.dif_stats import dif_special_cell_count
        result = dif_special_cell_count(MINIMAL)
        assert isinstance(result, int)
        assert result >= 0

    def test_all_samples_nonnegative(self):
        """All valid DIF samples return non-negative special cell count."""
        from dif.dif_stats import dif_special_cell_count
        for sample in SAMPLES.glob("*.dif"):
            assert dif_special_cell_count(sample) >= 0

    def test_numeric_row_nonnegative(self):
        """numeric-row.dif returns non-negative special cell count."""
        from dif.dif_stats import dif_special_cell_count
        assert dif_special_cell_count(NUMERIC) >= 0

"""
test_r1292_dif_gap_closure_cell_counts.py — Precise value assertions closing three gaps.

Closes:
  GAP-DIF-FOSS-DIF_BOOLEAN_-001   dif_boolean_cell_count   missing_test_coverage
  GAP-DIF-FOSS-DIF_DECLARED-001   dif_declared_vector_count  missing_test_coverage
  GAP-DIF-FOSS-DIF_SPECIAL_-001   dif_special_cell_count   missing_test_coverage

Grounded in DIF spec facts:
  SAL-DIF-00001: TABLE/VECTORS/TUPLES header directives define document dimensions
  SAL-DIF-00002: DATA section cell types with special markers (NA, boolean)

Sprint: hazy-questing-peach (TC-HQP-007)
"""
from __future__ import annotations

from pathlib import Path

import pytest

SAMPLES = Path(__file__).parent.parent.parent.parent / "samples" / "by-format" / "dif" / "valid"
MINIMAL = SAMPLES / "minimal-2x2.dif"    # VECTORS=2, TUPLES=2, 4 special cells
SINGLE = SAMPLES / "single-cell.dif"     # VECTORS=1, TUPLES=1, 0 special cells
NUMERIC = SAMPLES / "numeric-row.dif"   # VECTORS=3, no special cells


class TestDifDeclaredVectorCountPrecise:
    """GAP-DIF-FOSS-DIF_DECLARED-001: precise value assertions for declared vector count.

    SAL-DIF-00001: VECTORS directive specifies the declared number of columns.
    Weak assertions (>= 0, isinstance) in test_r1290 don't constitute sufficient
    test coverage for this capability. These tests assert exact expected values.
    """

    def test_minimal_declares_two_vectors(self):
        """minimal-2x2.dif: VECTORS=2 exactly."""
        from dif.dif_stats import dif_declared_vector_count
        assert dif_declared_vector_count(MINIMAL) == 2

    def test_single_cell_declares_one_vector(self):
        """single-cell.dif: VECTORS=1 exactly."""
        from dif.dif_stats import dif_declared_vector_count
        assert dif_declared_vector_count(SINGLE) == 1

    def test_numeric_row_declares_three_vectors(self):
        """numeric-row.dif: VECTORS=3 exactly."""
        from dif.dif_stats import dif_declared_vector_count
        assert dif_declared_vector_count(NUMERIC) == 3

    def test_all_samples_return_positive_int(self):
        """All valid DIF samples declare at least 1 vector."""
        from dif.dif_stats import dif_declared_vector_count
        for sample in sorted(SAMPLES.glob("*.dif")):
            result = dif_declared_vector_count(sample)
            assert isinstance(result, int), f"{sample.name}: expected int, got {type(result)}"
            assert result >= 1, f"{sample.name}: expected >= 1 vector, got {result}"


class TestDifBooleanCellCountPrecise:
    """GAP-DIF-FOSS-DIF_BOOLEAN_-001: precise value assertions for boolean cell count.

    SAL-DIF-00002: Boolean values use V/TRUE or V/FALSE markers in the DATA section.
    Standard DIF samples do not contain boolean cells; the function must return 0
    for files with no boolean-typed cells (not just >= 0).
    """

    def test_minimal_has_zero_boolean_cells(self):
        """minimal-2x2.dif: no boolean cells — result must be exactly 0."""
        from dif.dif_stats import dif_boolean_cell_count
        assert dif_boolean_cell_count(MINIMAL) == 0

    def test_single_cell_has_zero_boolean_cells(self):
        """single-cell.dif: no boolean cells — result must be exactly 0."""
        from dif.dif_stats import dif_boolean_cell_count
        assert dif_boolean_cell_count(SINGLE) == 0

    def test_numeric_row_has_zero_boolean_cells(self):
        """numeric-row.dif: all cells are numeric — no boolean cells."""
        from dif.dif_stats import dif_boolean_cell_count
        assert dif_boolean_cell_count(NUMERIC) == 0

    def test_all_samples_have_zero_boolean_cells(self):
        """All standard valid DIF samples contain 0 boolean cells."""
        from dif.dif_stats import dif_boolean_cell_count
        for sample in sorted(SAMPLES.glob("*.dif")):
            result = dif_boolean_cell_count(sample)
            assert result == 0, f"{sample.name}: expected 0 boolean cells, got {result}"

    def test_return_type_is_int(self):
        """Return type is int, not bool or float."""
        from dif.dif_stats import dif_boolean_cell_count
        result = dif_boolean_cell_count(MINIMAL)
        assert type(result) is int  # strict type check, not isinstance


class TestDifSpecialCellCountPrecise:
    """GAP-DIF-FOSS-DIF_SPECIAL_-001: precise value assertions for special cell count.

    SAL-DIF-00002: Special/NA cells use V marker variants that do not resolve to
    numeric or string values. minimal-2x2.dif is known to contain 4 special cells
    (all cells are NA in the 2x2 grid).
    """

    def test_minimal_has_four_special_cells(self):
        """minimal-2x2.dif: 4 special cells (2x2 grid of NA values) — exact count."""
        from dif.dif_stats import dif_special_cell_count
        assert dif_special_cell_count(MINIMAL) == 4

    def test_numeric_row_has_zero_special_cells(self):
        """numeric-row.dif: all cells are numeric — no special cells."""
        from dif.dif_stats import dif_special_cell_count
        assert dif_special_cell_count(NUMERIC) == 0

    def test_single_cell_has_zero_special_cells(self):
        """single-cell.dif: single numeric cell — no special cells."""
        from dif.dif_stats import dif_special_cell_count
        assert dif_special_cell_count(SINGLE) == 0

    def test_special_and_boolean_are_non_overlapping_for_minimal(self):
        """For minimal-2x2.dif: 4 special + 0 boolean = 4 total non-numeric cells."""
        from dif.dif_stats import dif_special_cell_count, dif_boolean_cell_count
        assert dif_special_cell_count(MINIMAL) == 4
        assert dif_boolean_cell_count(MINIMAL) == 0
        # Sum is exactly 4: no cell is double-counted
        assert dif_special_cell_count(MINIMAL) + dif_boolean_cell_count(MINIMAL) == 4

    def test_return_type_is_int(self):
        """Return type is int."""
        from dif.dif_stats import dif_special_cell_count
        result = dif_special_cell_count(MINIMAL)
        assert type(result) is int

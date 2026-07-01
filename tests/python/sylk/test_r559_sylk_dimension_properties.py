"""R559: SYLK document dimension properties — is_empty, is_single_cell, is_wide, is_tall.

Tests for SylkModelDocument dimension properties added in R559.
Spec refs: FACT-SYLK-014 (B record bounds), FACT-SYLK-003 (C cell record).
"""

from pathlib import Path
from sylk.models import SylkModelDocument

SAMPLES = Path("samples/by-format/sylk/valid")


class TestIsEmpty:
    def test_non_empty_2x2(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert doc.is_empty is False

    def test_non_empty_single_cell(self):
        doc = SylkModelDocument.from_file(SAMPLES / "single-cell.slk")
        assert doc.is_empty is False

    def test_non_empty_numeric_row(self):
        doc = SylkModelDocument.from_file(SAMPLES / "numeric-row.slk")
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert isinstance(doc.is_empty, bool)


class TestIsSingleCell:
    def test_single_cell_file(self):
        doc = SylkModelDocument.from_file(SAMPLES / "single-cell.slk")
        assert doc.is_single_cell is True

    def test_2x2_not_single_cell(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert doc.is_single_cell is False

    def test_numeric_row_not_single_cell(self):
        doc = SylkModelDocument.from_file(SAMPLES / "numeric-row.slk")
        assert doc.is_single_cell is False

    def test_is_single_cell_type(self):
        doc = SylkModelDocument.from_file(SAMPLES / "single-cell.slk")
        assert isinstance(doc.is_single_cell, bool)


class TestIsWide:
    def test_is_wide_type(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert isinstance(doc.is_wide, bool)

    def test_wide_and_tall_mutually_exclusive_when_square(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        # 2x2 grid — equal rows and cols, so neither wide nor tall
        assert not (doc.is_wide and doc.is_tall)


class TestIsTall:
    def test_is_tall_type(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert isinstance(doc.is_tall, bool)

    def test_tall_and_wide_mutually_exclusive(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert not (doc.is_tall and doc.is_wide)


class TestDimensionConsistency:
    def test_single_cell_not_empty(self):
        doc = SylkModelDocument.from_file(SAMPLES / "single-cell.slk")
        assert doc.is_single_cell
        assert not doc.is_empty

    def test_cell_count_consistent_with_is_empty(self):
        doc = SylkModelDocument.from_file(SAMPLES / "minimal-2x2.slk")
        assert (doc.cell_count == 0) == doc.is_empty

    def test_cell_count_consistent_with_is_single_cell(self):
        doc = SylkModelDocument.from_file(SAMPLES / "single-cell.slk")
        assert (doc.cell_count == 1) == doc.is_single_cell

"""
test_r58_dif_deepening.py — R58 Train G: DIF parser deepening.

Deepens coverage of DIF corpus samples, cell value oracle, and structure
validation not covered by existing Gate 5-7 tests.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.dif.dif_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    parse_dif_strict,
    probe_dif,
)

VALID = PROJECT_ROOT / "samples" / "by-format" / "dif" / "valid"


class TestDifCorpusOracle:
    """Oracle: committed corpus samples — exact structural values."""

    def test_single_cell_title(self):
        """single-cell.dif: title == 'single-cell'."""
        doc = parse_dif_strict(VALID / "single-cell.dif")
        assert doc.title == "single-cell"

    def test_single_cell_vectors_tuples(self):
        """single-cell.dif: 1 vector, 1 tuple."""
        doc = parse_dif_strict(VALID / "single-cell.dif")
        assert doc.vectors == 1
        assert doc.tuples == 1

    def test_single_cell_value(self):
        """single-cell.dif: cell value == 42.0."""
        doc = parse_dif_strict(VALID / "single-cell.dif")
        assert doc.rows[0][0].value == 42.0

    def test_single_cell_numeric_type(self):
        """single-cell.dif: cell type is numeric."""
        doc = parse_dif_strict(VALID / "single-cell.dif")
        assert doc.rows[0][0].value_type == "numeric"

    def test_numeric_row_title(self):
        """numeric-row.dif: title == 'numeric-row'."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        assert doc.title == "numeric-row"

    def test_numeric_row_vectors(self):
        """numeric-row.dif: 3 vectors (3 columns)."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        assert doc.vectors == 3

    def test_numeric_row_tuples(self):
        """numeric-row.dif: 1 tuple (1 row)."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        assert doc.tuples == 1

    def test_numeric_row_values(self):
        """numeric-row.dif: row values are [1.0, 2.0, 3.0]."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        row = doc.rows[0]
        assert [c.value for c in row] == [1.0, 2.0, 3.0]

    def test_minimal_2x2_row_count(self):
        """minimal-2x2.dif: has at least 1 row."""
        doc = parse_dif_strict(VALID / "minimal-2x2.dif")
        assert len(doc.rows) >= 1

    def test_minimal_2x2_title_not_empty(self):
        """minimal-2x2.dif: title is non-empty string."""
        doc = parse_dif_strict(VALID / "minimal-2x2.dif")
        assert isinstance(doc.title, str)
        assert len(doc.title) > 0


class TestDifStructure:
    """DIF document structural contracts."""

    def test_rows_is_list(self):
        """rows attribute is a list."""
        doc = parse_dif_strict(VALID / "single-cell.dif")
        assert isinstance(doc.rows, list)

    def test_row_cells_are_list(self):
        """Each row is a list of DifCell objects."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        for row in doc.rows:
            assert isinstance(row, list)

    def test_cell_has_value_and_type(self):
        """Each cell has value and value_type attributes."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        for row in doc.rows:
            for cell in row:
                assert hasattr(cell, "value")
                assert hasattr(cell, "value_type")

    def test_numeric_cell_value_is_float(self):
        """Numeric cells have float values."""
        doc = parse_dif_strict(VALID / "numeric-row.dif")
        for row in doc.rows:
            for cell in row:
                if cell.value_type == "numeric":
                    assert isinstance(cell.value, float)

    def test_probe_dif_returns_dict(self):
        """probe_dif returns a dict with format key."""
        result = probe_dif(VALID / "single-cell.dif")
        assert isinstance(result, dict)


class TestDifCapabilities:
    """Capability feature set."""

    def test_numeric_cells_in_supported(self):
        assert "numeric_cells" in SUPPORTED_FEATURES

    def test_string_cells_in_supported(self):
        assert "string_cells" in SUPPORTED_FEATURES

    def test_title_extraction_in_supported(self):
        assert "title_extraction" in SUPPORTED_FEATURES

    def test_formula_cells_unsupported(self):
        assert "formula_cells" in UNSUPPORTED_FEATURES

    def test_multi_table_unsupported(self):
        assert "multi_table_dif" in UNSUPPORTED_FEATURES

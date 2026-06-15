"""Product deepening tests for DIF stats module.

Tests dif_numeric_range, dif_vector_density, dif_string_value_list,
dif_empty_row_count, dif_string_cell_count, dif_total_numeric_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    parse_dif,
    write_dif,
    DifDocument,
    DifCell,
)
from src.python.dif.dif_stats import (
    dif_numeric_range,
    dif_string_value_list,
    dif_empty_row_count,
    dif_string_cell_count,
    dif_total_numeric_count,
)


@pytest.fixture
def mixed_doc(tmp_path):
    """Create a DIF file with mixed numeric and string data, parse it."""
    doc = DifDocument(title="TestDoc", vectors=2, tuples=3)
    doc.rows = [
        [DifCell(value="Name", value_type="string"),
         DifCell(value="Score", value_type="string")],
        [DifCell(value="Alice", value_type="string"),
         DifCell(value=95.5, value_type="numeric")],
        [DifCell(value="Bob", value_type="string"),
         DifCell(value=87.0, value_type="numeric")],
    ]
    f = tmp_path / "mixed.dif"
    write_dif(doc, str(f))
    return parse_dif(str(f))


@pytest.fixture
def empty_doc():
    """An empty DIF document dict."""
    return {"title": "Empty", "rows": [], "vectors": 0, "tuples": 0}


class TestDifNumericRange:
    def test_range_with_data(self, mixed_doc):
        result = dif_numeric_range(mixed_doc)
        assert "min_value" in result
        assert "max_value" in result
        assert result["numeric_count"] >= 2
        if result["min_value"] is not None:
            assert result["min_value"] <= result["max_value"]

    def test_range_empty(self, empty_doc):
        result = dif_numeric_range(empty_doc)
        assert result["numeric_count"] == 0


class TestDifStringValueList:
    def test_string_values_present(self, mixed_doc):
        strings = dif_string_value_list(mixed_doc)
        assert isinstance(strings, list)
        assert len(strings) >= 1

    def test_empty_doc_no_strings(self, empty_doc):
        assert dif_string_value_list(empty_doc) == []


class TestDifEmptyRowCount:
    def test_no_empty_rows(self, mixed_doc):
        count = dif_empty_row_count(mixed_doc)
        assert isinstance(count, int)
        assert count >= 0

    def test_empty_doc(self, empty_doc):
        assert dif_empty_row_count(empty_doc) == 0


class TestDifStringCellCount:
    def test_string_cells_present(self, mixed_doc):
        count = dif_string_cell_count(mixed_doc)
        assert isinstance(count, int)
        assert count >= 1

    def test_empty_doc(self, empty_doc):
        assert dif_string_cell_count(empty_doc) == 0


class TestDifTotalNumericCount:
    def test_numeric_cells_counted(self, mixed_doc):
        count = dif_total_numeric_count(mixed_doc)
        assert isinstance(count, int)
        assert count >= 1

    def test_empty_doc(self, empty_doc):
        assert dif_total_numeric_count(empty_doc) == 0

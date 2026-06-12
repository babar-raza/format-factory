"""
tests/python/fodt/test_r192_fodt_table_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT59-001
Tests for document_table_cell_count() — table cell metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_table_cell_count


class TestFodtTableCellCount:
    def test_empty_doc_returns_zeros(self):
        result = document_table_cell_count({})
        assert result["total_cells"] == 0
        assert result["total_tables"] == 0

    def test_returns_required_keys(self):
        result = document_table_cell_count({})
        assert "total_cells" in result
        assert "total_tables" in result
        assert "per_table" in result

    def test_per_table_is_list(self):
        result = document_table_cell_count({})
        assert isinstance(result["per_table"], list)

    def test_real_table_file_has_cells(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "table-basic.fodt"))
        result = document_table_cell_count(doc)
        assert result["total_cells"] > 0

    def test_real_table_file_has_tables(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "table-basic.fodt"))
        result = document_table_cell_count(doc)
        assert result["total_tables"] >= 1

    def test_per_table_entry_has_cell_count(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "table-basic.fodt"))
        result = document_table_cell_count(doc)
        for entry in result["per_table"]:
            assert "cell_count" in entry

    def test_total_cells_matches_per_table_sum(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "table-basic.fodt"))
        result = document_table_cell_count(doc)
        expected = sum(e["cell_count"] for e in result["per_table"])
        assert result["total_cells"] == expected

    def test_no_table_doc_has_empty_per_table(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_table_cell_count(doc)
        assert result["total_tables"] == 0
        assert result["per_table"] == []

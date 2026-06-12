"""Tests for DIF add_row and delete_row.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT20-001
Covers: row manipulation operations with roundtrip verification
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    DifDocument,
    DifCell,
    add_row,
    delete_row,
    write_dif,
    parse_dif_strict,
)


def _make_doc():
    return DifDocument(
        title="Test",
        vectors=2,
        tuples=2,
        rows=[
            [DifCell(value="Name", value_type="string"), DifCell(value="Score", value_type="string")],
            [DifCell(value="Alice", value_type="string"), DifCell(value=90.0, value_type="numeric")],
        ],
    )


class TestAddRow:
    def test_add_row_increases_count(self):
        doc = _make_doc()
        result = add_row(doc, ["Bob", 85])
        assert result["success"] is True
        assert len(doc.rows) == 3
        assert doc.tuples == 3

    def test_add_row_values(self):
        doc = _make_doc()
        add_row(doc, ["Charlie", 75])
        row = doc.rows[2]
        assert row[0].value == "Charlie"
        assert row[1].value == 75

    def test_add_row_returns_index(self):
        doc = _make_doc()
        result = add_row(doc, ["X"])
        assert result["row_index"] == 3
        assert result["cell_count"] == 1

    def test_add_row_roundtrip(self):
        doc = _make_doc()
        add_row(doc, ["Dave", 60])
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w") as f:
            out = Path(f.name)
        try:
            write_dif(doc, out)
            doc2 = parse_dif_strict(out)
            assert len(doc2.rows) == 3
            assert doc2.rows[2][0].value == "Dave"
        finally:
            out.unlink(missing_ok=True)


class TestDeleteRow:
    def test_delete_row_decreases_count(self):
        doc = _make_doc()
        result = delete_row(doc, 2)
        assert result["success"] is True
        assert len(doc.rows) == 1
        assert doc.tuples == 1

    def test_delete_row_preserves_other(self):
        doc = _make_doc()
        delete_row(doc, 2)
        assert doc.rows[0][0].value == "Name"

    def test_delete_row_returns_count(self):
        doc = _make_doc()
        result = delete_row(doc, 2)
        assert result["deleted_count"] == 2

    def test_delete_row_out_of_range(self):
        doc = _make_doc()
        result = delete_row(doc, 10)
        assert result["success"] is False

    def test_delete_row_roundtrip(self):
        doc = _make_doc()
        delete_row(doc, 2)
        with tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w") as f:
            out = Path(f.name)
        try:
            write_dif(doc, out)
            doc2 = parse_dif_strict(out)
            assert len(doc2.rows) == 1
            assert doc2.rows[0][0].value == "Name"
        finally:
            out.unlink(missing_ok=True)

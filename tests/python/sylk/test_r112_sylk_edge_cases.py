"""R112 FOSS: SYLK write edge cases — special characters, large grids, empty cells."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import parse_sylk, write_sylk, SylkDocument, SylkCell


def _make_doc(rows_data):
    """Build a SylkDocument from a list-of-lists of string values."""
    cells = []
    for r, row in enumerate(rows_data):
        for c, val in enumerate(row):
            if val != "":
                try:
                    numeric_val = float(val)
                    cells.append(SylkCell(row=r + 1, col=c + 1, value=numeric_val, value_type="numeric"))
                except (ValueError, TypeError):
                    cells.append(SylkCell(row=r + 1, col=c + 1, value=str(val), value_type="string"))
    num_rows = len(rows_data)
    num_cols = max((len(row) for row in rows_data), default=0)
    return SylkDocument(cells=cells, rows=num_rows, cols=num_cols)


class TestR112SylkEdgeCases:
    def test_roundtrip_empty_grid(self):
        doc = SylkDocument(cells=[], rows=0, cols=0)
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)

    def test_roundtrip_single_cell(self):
        doc = _make_doc([["hello"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
            assert result["cell_count"] >= 1
        finally:
            os.unlink(path)

    def test_roundtrip_numeric_values(self):
        doc = _make_doc([["1", "2.5", "3"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
            assert result["cell_count"] >= 3
        finally:
            os.unlink(path)

    def test_roundtrip_special_characters(self):
        doc = _make_doc([["hello;world", "a\"b", "c,d"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)

    def test_roundtrip_multirow(self):
        doc = _make_doc([["A", "B"], ["C", "D"], ["E", "F"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
            assert result["cell_count"] >= 6
        finally:
            os.unlink(path)

    def test_roundtrip_empty_cells(self):
        doc = _make_doc([["", "value", ""]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)

    def test_large_grid_10x10(self):
        rows = [[f"R{r}C{c}" for c in range(10)] for r in range(10)]
        doc = _make_doc(rows)
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
            assert result["cell_count"] >= 100
        finally:
            os.unlink(path)

    def test_file_starts_with_id(self):
        doc = _make_doc([["test"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            with open(path, "r") as f:
                first_line = f.readline().strip()
            assert first_line.startswith("ID")
        finally:
            os.unlink(path)

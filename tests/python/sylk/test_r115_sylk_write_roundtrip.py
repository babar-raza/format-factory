"""R115 Train D: SYLK write roundtrip + CSV export deepening.

Tests write_sylk + parse_sylk_strict roundtrip, sylk_to_csv edge cases,
and dogfood pipeline (create → write → parse → CSV).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest

from src.python.sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    parse_sylk_strict,
    write_sylk,
    sylk_to_csv,
    SylkError,
)


def make_doc(*cells) -> SylkDocument:
    """Helper to create a SylkDocument with given (row, col, value, type) tuples."""
    doc = SylkDocument(cells=[
        SylkCell(row=r, col=c, value=v, value_type=t)
        for r, c, v, t in cells
    ])
    return doc


def get_cell(doc: SylkDocument, row: int, col: int):
    """Find a cell by row and column in a SylkDocument."""
    for c in doc.cells:
        if c.row == row and c.col == col:
            return c
    return None


class TestSylkWriteRoundtrip:
    def test_roundtrip_string_cell(self, tmp_path):
        doc = make_doc((1, 1, "Hello", "string"), (1, 2, "World", "string"))
        out = tmp_path / "test.slk"
        write_sylk(doc, out)
        reloaded = parse_sylk_strict(out)
        assert get_cell(reloaded,1, 1).value == "Hello"
        assert get_cell(reloaded,1, 2).value == "World"

    def test_roundtrip_numeric_cell(self, tmp_path):
        doc = make_doc((2, 1, 42, "number"), (2, 2, 3.14, "number"))
        out = tmp_path / "nums.slk"
        write_sylk(doc, out)
        reloaded = parse_sylk_strict(out)
        assert float(get_cell(reloaded,2, 1).value) == pytest.approx(42.0)

    def test_roundtrip_empty_doc(self, tmp_path):
        doc = SylkDocument(cells=[])
        out = tmp_path / "empty.slk"
        write_sylk(doc, out)
        reloaded = parse_sylk_strict(out)
        assert len(reloaded.cells) == 0

    def test_roundtrip_grid_preserved(self, tmp_path):
        cells = [
            (1, 1, "Name", "string"), (1, 2, "Score", "string"),
            (2, 1, "Alice", "string"), (2, 2, 95, "number"),
            (3, 1, "Bob", "string"), (3, 2, 82, "number"),
        ]
        doc = make_doc(*cells)
        out = tmp_path / "grid.slk"
        write_sylk(doc, out)
        reloaded = parse_sylk_strict(out)
        assert get_cell(reloaded,1, 1).value == "Name"
        assert float(get_cell(reloaded,2, 2).value) == pytest.approx(95.0)

    def test_written_file_has_id_header(self, tmp_path):
        doc = make_doc((1, 1, "Test", "string"))
        out = tmp_path / "hdr.slk"
        write_sylk(doc, out)
        content = out.read_bytes().decode("ascii")
        assert content.startswith("ID;P")

    def test_written_file_has_e_footer(self, tmp_path):
        doc = make_doc((1, 1, "x", "string"))
        out = tmp_path / "footer.slk"
        write_sylk(doc, out)
        content = out.read_bytes().decode("ascii")
        assert content.rstrip().endswith("E")

    def test_roundtrip_special_chars_in_string(self, tmp_path):
        doc = make_doc((1, 1, "Hello World", "string"))
        out = tmp_path / "space.slk"
        write_sylk(doc, out)
        reloaded = parse_sylk_strict(out)
        assert get_cell(reloaded,1, 1).value == "Hello World"


class TestSylkToCsvDeepening:
    def test_csv_export_grid(self, tmp_path):
        doc = make_doc(
            (1, 1, "Name", "string"), (1, 2, "Score", "string"),
            (2, 1, "Alice", "string"), (2, 2, 95, "number"),
        )
        out = tmp_path / "data.slk"
        write_sylk(doc, out)
        csv = sylk_to_csv(out)
        assert "Name" in csv
        assert "Alice" in csv
        assert "95" in csv

    def test_csv_has_correct_column_count(self, tmp_path):
        doc = make_doc(
            (1, 1, "A", "string"), (1, 2, "B", "string"), (1, 3, "C", "string"),
        )
        out = tmp_path / "cols.slk"
        write_sylk(doc, out)
        csv = sylk_to_csv(out)
        first_line = csv.split("\r\n")[0].split("\n")[0]
        assert first_line.count(",") == 2  # 3 columns = 2 commas

    def test_dogfood_pipeline(self, tmp_path):
        # Full pipeline: create → write → parse → CSV
        cells = [(1, 1, "Product", "string"), (1, 2, "Revenue", "string"),
                 (2, 1, "Widget", "string"), (2, 2, 12000, "number"),
                 (3, 1, "Gadget", "string"), (3, 2, 8500, "number")]
        doc = make_doc(*cells)
        out = tmp_path / "dogfood.slk"
        write_sylk(doc, out)
        csv = sylk_to_csv(out)
        assert "Product" in csv
        assert "Widget" in csv
        assert "12000" in csv

    def test_write_invalid_path_raises(self, tmp_path):
        doc = make_doc((1, 1, "x", "string"))
        with pytest.raises((SylkError, OSError)):
            write_sylk(doc, tmp_path / "nonexistent" / "deep" / "file.slk")

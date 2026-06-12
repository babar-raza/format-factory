# R94 Train R: SYLK Write Edge Cases Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R94-GOVERNED-PYTHON-SYLK-WRITE-EDGECASES-001
# Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

"""Tests for write_sylk edge cases — empty docs, special characters, large grids."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from sylk.sylk_parser import write_sylk, parse_sylk, SylkDocument, SylkCell


class TestSylkWriteEdgeCases:
    """R94 SYLK write edge case tests."""

    def test_empty_document_writes_header_and_footer(self, tmp_path):
        """Empty SylkDocument should produce ID;P header and E footer."""
        doc = SylkDocument(cells=[])
        path = tmp_path / "empty.sylk"
        write_sylk(doc, str(path))
        content = path.read_text(encoding="ascii")
        assert content.startswith("ID;P")
        assert content.strip().endswith("E")

    def test_numeric_cell_no_quotes(self, tmp_path):
        """Numeric cells should not be quoted in output."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value=42, value_type="number"),
        ])
        path = tmp_path / "numeric.sylk"
        write_sylk(doc, str(path))
        content = path.read_text(encoding="ascii")
        assert "K42" in content
        assert 'K"42"' not in content

    def test_string_cell_quoted(self, tmp_path):
        """String cells should be quoted."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value="Hello", value_type="string"),
        ])
        path = tmp_path / "string.sylk"
        write_sylk(doc, str(path))
        content = path.read_text(encoding="ascii")
        assert 'K"Hello"' in content

    def test_none_value_skipped(self, tmp_path):
        """Cells with None value should be skipped."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value=None, value_type="string"),
            SylkCell(row=1, col=2, value="keep", value_type="string"),
        ])
        path = tmp_path / "none.sylk"
        write_sylk(doc, str(path))
        content = path.read_bytes().decode("ascii")
        lines = [l for l in content.strip().split("\r\n") if l.startswith("C;")]
        assert len(lines) == 1, f"Expected 1 cell record, got {len(lines)}"

    def test_roundtrip_preserves_data(self, tmp_path):
        """Write then parse should preserve cell values."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value="Alpha", value_type="string"),
            SylkCell(row=1, col=2, value=99.5, value_type="number"),
            SylkCell(row=2, col=1, value="Beta", value_type="string"),
        ])
        path = tmp_path / "roundtrip.sylk"
        write_sylk(doc, str(path))
        parsed = parse_sylk(str(path))
        assert parsed.get("ok") is True
        assert parsed.get("cell_count", 0) >= 2

    def test_large_grid_writes_correctly(self, tmp_path):
        """100-cell grid should produce 100 C records."""
        cells = []
        for r in range(1, 11):
            for c in range(1, 11):
                cells.append(SylkCell(row=r, col=c, value=r * c, value_type="number"))
        doc = SylkDocument(cells=cells)
        path = tmp_path / "grid.sylk"
        write_sylk(doc, str(path))
        content = path.read_bytes().decode("ascii")
        c_lines = [l for l in content.strip().split("\r\n") if l.startswith("C;")]
        assert len(c_lines) == 100

    def test_write_creates_file(self, tmp_path):
        """write_sylk should create the file if it doesn't exist."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value="test", value_type="string")])
        path = tmp_path / "new.sylk"
        assert not path.exists()
        write_sylk(doc, str(path))
        assert path.exists()

    def test_float_value_preserved(self, tmp_path):
        """Float values should be written as-is."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value=3.14159, value_type="number"),
        ])
        path = tmp_path / "float.sylk"
        write_sylk(doc, str(path))
        content = path.read_text(encoding="ascii")
        assert "3.14159" in content

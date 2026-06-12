# R95 Train Q: SYLK Roundtrip Hardening Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R95-GOVERNED-PYTHON-SYLK-ROUNDTRIP-001
# Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

"""Tests for SYLK write-then-parse roundtrip integrity and edge cases."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from sylk.sylk_parser import write_sylk, parse_sylk, SylkDocument, SylkCell


class TestSylkRoundtripHardening:
    """R95 SYLK roundtrip hardening tests."""

    def test_roundtrip_single_string_cell(self, tmp_path):
        """Single string cell roundtrips."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value="Test", value_type="string")])
        path = tmp_path / "single.sylk"
        write_sylk(doc, str(path))
        parsed = parse_sylk(str(path))
        assert parsed.get("ok") is True
        assert parsed.get("cell_count", 0) >= 1

    def test_roundtrip_single_number_cell(self, tmp_path):
        """Single number cell roundtrips."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value=42, value_type="number")])
        path = tmp_path / "number.sylk"
        write_sylk(doc, str(path))
        parsed = parse_sylk(str(path))
        assert parsed.get("ok") is True

    def test_roundtrip_mixed_types(self, tmp_path):
        """Mixed string and number cells roundtrip."""
        doc = SylkDocument(cells=[
            SylkCell(row=1, col=1, value="Name", value_type="string"),
            SylkCell(row=1, col=2, value=100, value_type="number"),
            SylkCell(row=2, col=1, value="Age", value_type="string"),
            SylkCell(row=2, col=2, value=25, value_type="number"),
        ])
        path = tmp_path / "mixed.sylk"
        write_sylk(doc, str(path))
        parsed = parse_sylk(str(path))
        assert parsed.get("ok") is True
        assert parsed.get("cell_count", 0) >= 3

    def test_roundtrip_preserves_header(self, tmp_path):
        """Written file starts with ID;P header."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value="X", value_type="string")])
        path = tmp_path / "header.sylk"
        write_sylk(doc, str(path))
        content = path.read_bytes().decode("ascii")
        assert content.startswith("ID;P")

    def test_roundtrip_preserves_footer(self, tmp_path):
        """Written file ends with E footer."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value="X", value_type="string")])
        path = tmp_path / "footer.sylk"
        write_sylk(doc, str(path))
        content = path.read_bytes().decode("ascii")
        assert content.strip().endswith("E")

    def test_crlf_line_endings(self, tmp_path):
        """Written file uses CRLF line endings."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value="Test", value_type="string")])
        path = tmp_path / "crlf.sylk"
        write_sylk(doc, str(path))
        raw = path.read_bytes()
        assert b"\r\n" in raw
        # No bare LF (that isn't preceded by CR)
        content = raw.replace(b"\r\n", b"")
        assert b"\n" not in content, "Found bare LF not part of CRLF"

    def test_large_grid_roundtrip(self, tmp_path):
        """50-cell grid roundtrips."""
        cells = []
        for r in range(1, 6):
            for c in range(1, 11):
                cells.append(SylkCell(row=r, col=c, value=r * 10 + c, value_type="number"))
        doc = SylkDocument(cells=cells)
        path = tmp_path / "grid.sylk"
        write_sylk(doc, str(path))
        parsed = parse_sylk(str(path))
        assert parsed.get("ok") is True

    def test_float_roundtrip(self, tmp_path):
        """Float values roundtrip through file."""
        doc = SylkDocument(cells=[SylkCell(row=1, col=1, value=3.14159, value_type="number")])
        path = tmp_path / "float.sylk"
        write_sylk(doc, str(path))
        content = path.read_bytes().decode("ascii")
        assert "3.14159" in content

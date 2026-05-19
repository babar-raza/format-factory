"""Gate 6 oracle tests for SYLK parser — deterministic expected-value verification."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import parse_sylk_strict, parse_sylk, probe_sylk, get_capabilities

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "sylk")


class TestSylkGate6Oracle:
    def test_minimal_2x2_oracle(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert doc.rows == 2
        assert doc.cols == 2
        assert len(doc.cells) == 4
        # First cell: "Name" string at (1,1)
        assert doc.cells[0].row == 1
        assert doc.cells[0].col == 1
        assert doc.cells[0].value == "Name"
        assert doc.cells[0].value_type == "string"
        # Fourth cell: 42 numeric at (2,2)
        assert doc.cells[3].row == 2
        assert doc.cells[3].col == 2
        assert doc.cells[3].value == 42
        assert doc.cells[3].value_type == "numeric"

    def test_single_cell_oracle(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        assert len(doc.cells) == 1
        assert doc.cells[0].value == 99
        assert doc.cells[0].value_type == "numeric"
        assert doc.cells[0].row == 1
        assert doc.cells[0].col == 1

    def test_numeric_row_oracle(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "numeric-row.slk"))
        assert len(doc.cells) == 3
        values = [c.value for c in doc.cells]
        assert values == [1, 2, 3]
        cols = [c.col for c in doc.cells]
        assert cols == [1, 2, 3]

    def test_synthetic_empty_table(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False) as f:
            f.write("ID;P\nE\n")
            f.flush()
            doc = parse_sylk_strict(f.name)
        assert len(doc.cells) == 0
        assert doc.rows == 0
        os.unlink(f.name)

    def test_synthetic_mixed_types(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False) as f:
            f.write('ID;P\nC;X1;Y1;K"hello"\nC;X2;Y1;K42\nE\n')
            f.flush()
            doc = parse_sylk_strict(f.name)
        assert doc.cells[0].value == "hello"
        assert doc.cells[0].value_type == "string"
        assert doc.cells[1].value == 42
        assert doc.cells[1].value_type == "numeric"
        os.unlink(f.name)

    def test_synthetic_multi_row(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False) as f:
            f.write("ID;P\nC;X1;Y1;K1\nC;X1;Y2;K2\nC;X1;Y3;K3\nE\n")
            f.flush()
            doc = parse_sylk_strict(f.name)
        assert doc.rows == 3
        assert doc.cols == 1
        values = [c.value for c in doc.cells]
        assert values == [1, 2, 3]
        os.unlink(f.name)

    def test_dict_api_oracle(self):
        result = parse_sylk(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert result["ok"] is True
        assert result["rows"] == 2
        assert result["cols"] == 2
        assert result["cell_count"] == 4
        assert result["id_line"].startswith("ID")

    def test_probe_parse_consistency(self):
        path = os.path.join(SAMPLES, "valid", "minimal-2x2.slk")
        probe = probe_sylk(path)
        doc = parse_sylk_strict(path)
        assert probe["valid_header"] is True
        assert probe["id_line"] == doc.id_line

    def test_id_line_content(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert doc.id_line.startswith("ID")
        assert "P" in doc.id_line

    def test_capabilities_oracle(self):
        caps = get_capabilities()
        assert caps["format"] == "sylk"
        assert caps["gate"] == 5
        assert len(caps["supported"]) >= 7
        assert len(caps["unsupported"]) >= 9

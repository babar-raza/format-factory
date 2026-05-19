"""Gate 6 deterministic oracle tests for DIF parser.

Oracle strategy: Compare parsed output against known expected values
from deterministic synthetic DIF text. No external tool dependency.
"""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from dif.dif_parser import parse_dif, parse_dif_strict

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "dif"


def _make_dif(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w",
                                      encoding="utf-8", newline="")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestDifOracleKnownValues:
    """Deterministic oracle: compare parsed output against expected values."""

    def test_known_minimal_2x2_oracle(self):
        """Oracle: minimal-2x2.dif has title='minimal', vectors=2, tuples=2."""
        doc = parse_dif_strict(SAMPLES / "valid" / "minimal-2x2.dif")
        assert doc.title == "minimal"
        assert doc.vectors == 2
        assert doc.tuples == 2

    def test_known_single_cell_oracle(self):
        """Oracle: single-cell.dif has vectors=1, tuples=1."""
        doc = parse_dif_strict(SAMPLES / "valid" / "single-cell.dif")
        assert doc.title == "single-cell"
        assert doc.vectors == 1
        assert doc.tuples == 1

    def test_known_numeric_row_oracle(self):
        """Oracle: numeric-row.dif has [1, 2, 3]."""
        doc = parse_dif_strict(SAMPLES / "valid" / "numeric-row.dif")
        values = [c.value for c in doc.rows[0] if c.value_type == "numeric"]
        assert values == [1.0, 2.0, 3.0]

    def test_synthetic_string_cells_oracle(self):
        """Oracle: synthetic DIF with string cells extracts exact text."""
        content = (
            'TABLE\n0,1\n"test"\n'
            'VECTORS\n0,2\n""\n'
            'TUPLES\n0,1\n""\n'
            'DATA\n0,0\n""\n'
            '1,0\n"Hello"\n'
            '1,0\n"World"\n'
            '-1,0\nBOT\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert len(doc.rows) == 1
        assert doc.rows[0][0].value == "Hello"
        assert doc.rows[0][0].value_type == "string"
        assert doc.rows[0][1].value == "World"

    def test_synthetic_numeric_cells_oracle(self):
        """Oracle: synthetic DIF with numeric cells extracts exact values."""
        content = (
            'TABLE\n0,1\n"nums"\n'
            'VECTORS\n0,3\n""\n'
            'TUPLES\n0,1\n""\n'
            'DATA\n0,0\n""\n'
            '0,3.14\nV\n'
            '0,-99.5\nV\n'
            '0,0\nV\n'
            '-1,0\nBOT\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert doc.rows[0][0].value == 3.14
        assert doc.rows[0][1].value == -99.5
        assert doc.rows[0][2].value == 0.0

    def test_synthetic_multi_row_oracle(self):
        """Oracle: synthetic DIF with 3 rows of data."""
        content = (
            'TABLE\n0,1\n"multi"\n'
            'VECTORS\n0,1\n""\n'
            'TUPLES\n0,3\n""\n'
            'DATA\n0,0\n""\n'
            '0,10\nV\n'
            '-1,0\nBOT\n'
            '0,20\nV\n'
            '-1,0\nBOT\n'
            '0,30\nV\n'
            '-1,0\nBOT\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert len(doc.rows) == 3
        assert doc.rows[0][0].value == 10.0
        assert doc.rows[1][0].value == 20.0
        assert doc.rows[2][0].value == 30.0

    def test_synthetic_empty_data_oracle(self):
        """Oracle: DIF with DATA section but only BOT+EOD = empty rows."""
        content = (
            'TABLE\n0,1\n"empty"\n'
            'VECTORS\n0,0\n""\n'
            'TUPLES\n0,0\n""\n'
            'DATA\n0,0\n""\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert len(doc.rows) == 0

    def test_dict_api_oracle(self):
        """Oracle: parse_dif dict API returns correct structure."""
        result = parse_dif(SAMPLES / "valid" / "minimal-2x2.dif")
        assert result["ok"] is True
        assert result["title"] == "minimal"
        assert result["vectors"] == 2
        assert result["row_count"] >= 1

    def test_title_extraction_oracle(self):
        """Oracle: title is extracted from TABLE header."""
        content = (
            'TABLE\n0,1\n"My Custom Title"\n'
            'VECTORS\n0,1\n""\n'
            'TUPLES\n0,1\n""\n'
            'DATA\n0,0\n""\n'
            '0,1\nV\n'
            '-1,0\nBOT\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert doc.title == "My Custom Title"

    def test_mixed_types_oracle(self):
        """Oracle: row with both string and numeric cells."""
        content = (
            'TABLE\n0,1\n"mixed"\n'
            'VECTORS\n0,2\n""\n'
            'TUPLES\n0,1\n""\n'
            'DATA\n0,0\n""\n'
            '1,0\n"Label"\n'
            '0,42\nV\n'
            '-1,0\nBOT\n'
            '-1,0\nEOD\n'
        )
        path = _make_dif(content)
        doc = parse_dif_strict(path)
        assert doc.rows[0][0].value == "Label"
        assert doc.rows[0][0].value_type == "string"
        assert doc.rows[0][1].value == 42.0
        assert doc.rows[0][1].value_type == "numeric"

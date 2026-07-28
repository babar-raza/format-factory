"""
tests/python/sylk/test_r233_sylk_writer_value_type_roundtrip.py

Sprint r233: Fix _cell_record / write_sylk_str to honour value_type="number"/"numeric"
when the Python value is a string (e.g. "10" → K10 unquoted, not K"10").

Covers: _cell_record (11 tests) and write_sylk_str roundtrip (9 tests).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import tempfile

from sylk.sylk_writer import _cell_record, write_sylk_str, write_sylk, SylkWriteError
from sylk.sylk_parser import SylkDocument, SylkCell, parse_sylk_strict


# ---------------------------------------------------------------------------
# _cell_record tests (11 tests)
# ---------------------------------------------------------------------------

class TestCellRecord:
    def test_int_value_unquoted(self):
        assert _cell_record(1, 1, 10) == "C;X1;Y1;K10"

    def test_float_value_unquoted(self):
        assert _cell_record(1, 1, 3.14) == "C;X1;Y1;K3.14"

    def test_string_value_quoted(self):
        assert _cell_record(1, 1, "hello") == 'C;X1;Y1;K"hello"'

    def test_string_numeric_no_type_quoted(self):
        # Without value_type hint, string stays quoted
        assert _cell_record(1, 1, "10") == 'C;X1;Y1;K"10"'

    def test_string_numeric_with_number_type_unquoted(self):
        result = _cell_record(1, 1, "10", value_type="number")
        assert result == "C;X1;Y1;K10"

    def test_string_numeric_with_numeric_type_unquoted(self):
        result = _cell_record(1, 1, "10", value_type="numeric")
        assert result == "C;X1;Y1;K10"

    def test_string_float_with_number_type(self):
        result = _cell_record(1, 1, "3.5", value_type="number")
        assert result == "C;X1;Y1;K3.5"

    def test_non_numeric_string_with_number_type_falls_back_quoted(self):
        result = _cell_record(1, 1, "abc", value_type="number")
        assert result == 'C;X1;Y1;K"abc"'

    def test_string_type_still_quoted(self):
        result = _cell_record(1, 1, "hello", value_type="string")
        assert result == 'C;X1;Y1;K"hello"'

    def test_none_value_type_leaves_string_quoted(self):
        result = _cell_record(1, 1, "42", value_type=None)
        assert result == 'C;X1;Y1;K"42"'

    def test_quote_escaping_preserved(self):
        result = _cell_record(1, 2, 'say "hi"')
        assert result == 'C;X2;Y1;K"say ""hi"""'


# ---------------------------------------------------------------------------
# write_sylk_str / write_sylk roundtrip tests (9 tests)
# ---------------------------------------------------------------------------

def _make_doc(*cells_data):
    """Build a SylkDocument from (row, col, value, value_type) tuples."""
    cells = [SylkCell(row=r, col=c, value=v, value_type=vt)
             for r, c, v, vt in cells_data]
    return SylkDocument(cells=cells)


class TestWriteSylkStrRoundtrip:
    def test_numeric_string_cell_roundtrips_as_numeric(self):
        doc = _make_doc((1, 1, "10", "number"))
        text = write_sylk_str(doc)
        assert 'K10' in text
        assert 'K"10"' not in text

    def test_string_cell_roundtrips_as_string(self):
        doc = _make_doc((1, 1, "hello", "string"))
        text = write_sylk_str(doc)
        assert 'K"hello"' in text

    def test_mixed_row_roundtrip(self):
        doc = _make_doc(
            (1, 1, "5", "number"),
            (1, 2, "text", "string"),
        )
        text = write_sylk_str(doc)
        assert "K5" in text
        assert 'K"text"' in text

    def test_parse_after_write_gives_numeric_value_type(self):
        doc = _make_doc((1, 1, "42", "number"))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.slk"
            write_sylk(doc, str(p))
            parsed = parse_sylk_strict(p)
        assert len(parsed.cells) == 1
        assert parsed.cells[0].value_type == "numeric"

    def test_parse_after_write_gives_correct_value(self):
        doc = _make_doc((1, 1, "25", "number"))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.slk"
            write_sylk(doc, str(p))
            parsed = parse_sylk_strict(p)
        assert int(parsed.cells[0].value) == 25

    def test_parse_after_write_string_stays_string(self):
        doc = _make_doc((1, 1, "hello", "string"))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.slk"
            write_sylk(doc, str(p))
            parsed = parse_sylk_strict(p)
        assert parsed.cells[0].value_type == "string"

    def test_python_int_cell_roundtrips(self):
        doc = _make_doc((1, 1, 99, "number"))
        text = write_sylk_str(doc)
        assert "K99" in text

    def test_empty_document_produces_header_and_terminator(self):
        doc = SylkDocument(cells=[])
        text = write_sylk_str(doc)
        assert text.startswith("ID;P")
        assert text.strip().endswith("E")

    def test_float_string_numeric_type_roundtrip(self):
        doc = _make_doc((1, 1, "3.14", "numeric"))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.slk"
            write_sylk(doc, str(p))
            parsed = parse_sylk_strict(p)
        assert parsed.cells[0].value_type == "numeric"
        assert abs(float(parsed.cells[0].value) - 3.14) < 1e-9

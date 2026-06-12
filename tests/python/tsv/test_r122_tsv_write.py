"""
tests/python/tsv/test_r122_tsv_write.py

Sprint: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-TSV-WRITE: write_tsv()
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import write_tsv, parse_tsv_strict


def _tmp() -> Path:
    return Path(tempfile.mktemp(suffix=".tsv"))


class TestWriteTsvBasic:
    def test_creates_file(self):
        out = _tmp()
        try:
            write_tsv([["a", "b"]], out)
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_single_row(self):
        out = _tmp()
        try:
            write_tsv([["hello", "world"]], out)
            assert out.read_text() == "hello\tworld\n"
        finally:
            out.unlink(missing_ok=True)

    def test_multiple_rows(self):
        out = _tmp()
        try:
            write_tsv([["a", "b"], ["c", "d"]], out)
            lines = out.read_text().splitlines()
            assert lines[0] == "a\tb"
            assert lines[1] == "c\td"
        finally:
            out.unlink(missing_ok=True)

    def test_with_headers(self):
        out = _tmp()
        try:
            write_tsv([["1", "2"]], out, headers=["id", "value"])
            lines = out.read_text().splitlines()
            assert lines[0] == "id\tvalue"
            assert lines[1] == "1\t2"
        finally:
            out.unlink(missing_ok=True)

    def test_empty_rows_produces_empty_file(self):
        out = _tmp()
        try:
            write_tsv([], out)
            assert out.read_text() == ""
        finally:
            out.unlink(missing_ok=True)

    def test_tab_in_cell_replaced(self):
        """Tabs in cell values must not produce extra columns."""
        out = _tmp()
        try:
            write_tsv([["a\tb", "c"]], out)
            content = out.read_text()
            # The embedded tab is replaced with a space
            assert "a b\tc" in content
        finally:
            out.unlink(missing_ok=True)

    def test_newline_in_cell_replaced(self):
        out = _tmp()
        try:
            write_tsv([["line1\nline2", "col2"]], out)
            content = out.read_text()
            assert "line1 line2\tcol2" in content
        finally:
            out.unlink(missing_ok=True)

    def test_accepts_string_path(self):
        out = _tmp()
        try:
            write_tsv([["x"]], str(out))
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_file_ends_with_newline(self):
        out = _tmp()
        try:
            write_tsv([["a", "b"]], out)
            assert out.read_text().endswith("\n")
        finally:
            out.unlink(missing_ok=True)

    def test_utf8_encoding(self):
        out = _tmp()
        try:
            write_tsv([["héllo", "wörld"]], out)
            content = out.read_bytes().decode("utf-8")
            assert "héllo" in content
            assert "wörld" in content
        finally:
            out.unlink(missing_ok=True)


class TestWriteTsvRoundtrip:
    """write_tsv → parse_tsv_strict roundtrip tests."""

    def test_simple_roundtrip(self):
        out = _tmp()
        rows = [["Alice", "30"], ["Bob", "25"], ["Carol", "35"]]
        try:
            write_tsv(rows, out, headers=["name", "age"])
            model = parse_tsv_strict(out)
            assert model["row_count"] == 3
            assert model["column_count"] == 2
            assert model["has_header"] is True
            assert model["headers"] == ["name", "age"]
        finally:
            out.unlink(missing_ok=True)

    def test_data_preserved_in_roundtrip(self):
        out = _tmp()
        rows = [["Q1", "100"], ["Q2", "200"], ["Q3", "150"]]
        try:
            write_tsv(rows, out, headers=["quarter", "revenue"])
            model = parse_tsv_strict(out)
            assert model["rows"][0] == ["Q1", "100"]
            assert model["rows"][1] == ["Q2", "200"]
            assert model["rows"][2] == ["Q3", "150"]
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_no_headers(self):
        """Write 3 rows without explicit headers; parser detects row 0 as header
        when all rows share the same column count (has_header heuristic)."""
        out = _tmp()
        rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
        try:
            write_tsv(rows, out)
            model = parse_tsv_strict(out)
            # Parser treats first row as header because all 3 rows have 2 cols
            assert model["column_count"] == 2
            assert model["has_header"] is True
            assert model["headers"] == ["name", "age"]
        finally:
            out.unlink(missing_ok=True)

    def test_single_column_roundtrip(self):
        out = _tmp()
        try:
            write_tsv([["one"], ["two"], ["three"]], out)
            model = parse_tsv_strict(out)
            assert model["column_count"] == 1
        finally:
            out.unlink(missing_ok=True)

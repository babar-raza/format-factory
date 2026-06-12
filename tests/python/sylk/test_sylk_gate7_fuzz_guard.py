"""Gate 7 fuzz guard tests for SYLK parser — malformed input handling."""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import (
    parse_sylk_strict, parse_sylk,
    SylkInvalidFormatError, SylkSizeError, SylkParseError,
)


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestSylkGate7FuzzGuard:
    def test_empty_file(self):
        p = _write_temp("")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_missing_id_record(self):
        p = _write_temp("C;X1;Y1;K42\nE\n")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_missing_end_record(self):
        p = _write_temp("ID;P\nC;X1;Y1;K42\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_invalid_x_field(self):
        p = _write_temp("ID;P\nC;Xabc;Y1;K42\nE\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_invalid_y_field(self):
        p = _write_temp("ID;P\nC;X1;Yabc;K42\nE\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_dict_api_safety(self):
        p = _write_temp("RANDOM GARBAGE NOT SYLK")
        result = parse_sylk(p)
        assert result["ok"] is False
        os.unlink(p)

    def test_binary_garbage(self):
        f = tempfile.NamedTemporaryFile(mode="wb", suffix=".slk", delete=False)
        f.write(bytes(range(256)))
        f.close()
        result = parse_sylk(f.name)
        assert result["ok"] is False
        os.unlink(f.name)

    def test_huge_column(self):
        p = _write_temp("ID;P\nC;X99999;Y1;K1\nE\n")
        with pytest.raises(SylkSizeError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_huge_row(self):
        p = _write_temp("ID;P\nC;X1;Y9999999;K1\nE\n")
        with pytest.raises(SylkSizeError):
            parse_sylk_strict(p)
        os.unlink(p)

    def test_only_id_and_end(self):
        p = _write_temp("ID;P\nE\n")
        doc = parse_sylk_strict(p)
        assert len(doc.cells) == 0
        os.unlink(p)

    def test_id_only_no_end(self):
        p = _write_temp("ID;P\n")
        with pytest.raises(SylkParseError):
            parse_sylk_strict(p)
        os.unlink(p)

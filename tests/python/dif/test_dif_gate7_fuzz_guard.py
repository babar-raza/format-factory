"""Gate 7 security and fuzz guard tests for DIF parser.

Deterministic malformed input guards. No heavy fuzzing.
"""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from dif.dif_parser import (
    DifInvalidFormatError,
    parse_dif,
    parse_dif_strict,
)


def _write_dif(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w",
                                      encoding="utf-8", newline="")
    tmp.write(content)
    tmp.close()
    return tmp.name


class TestDifFuzzGuards:
    """Malformed input guards for DIF parser."""

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False)
        tmp.close()
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(tmp.name)

    def test_random_text(self):
        path = _write_dif("This is not a DIF file at all.")
        result = parse_dif(path)
        assert result["ok"] is False

    def test_missing_table_section(self):
        path = _write_dif("VECTORS\n0,1\n\"\"\nDATA\n0,0\n\"\"\n-1,0\nEOD\n")
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(path)

    def test_missing_vectors_section(self):
        path = _write_dif("TABLE\n0,1\n\"t\"\nDATA\n0,0\n\"\"\n-1,0\nEOD\n")
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(path)

    def test_truncated_header(self):
        path = _write_dif("TABLE\n0,1\n")
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(path)

    def test_dict_api_never_raises(self):
        result = parse_dif("/nonexistent/file.dif")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_binary_garbage(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False)
        tmp.write(bytes(range(256)))
        tmp.close()
        result = parse_dif(tmp.name)
        assert result["ok"] is False

    def test_invalid_numeric_pair(self):
        path = _write_dif("TABLE\nNOT,A,NUMBER\n\"t\"\n")
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(path)

    def test_no_eod_marker(self):
        """DIF without EOD — parser should handle gracefully."""
        path = _write_dif(
            'TABLE\n0,1\n"t"\n'
            'VECTORS\n0,1\n""\n'
            'TUPLES\n0,1\n""\n'
            'DATA\n0,0\n""\n'
            '0,1\nV\n'
        )
        # Should not crash — may return partial data
        result = parse_dif(path)
        assert isinstance(result, dict)

    def test_extremely_long_string_value(self):
        """Very long string value should not OOM."""
        long_str = "x" * 10000
        path = _write_dif(
            f'TABLE\n0,1\n"t"\n'
            f'VECTORS\n0,1\n""\n'
            f'TUPLES\n0,1\n""\n'
            f'DATA\n0,0\n""\n'
            f'1,0\n"{long_str}"\n'
            f'-1,0\nBOT\n'
            f'-1,0\nEOD\n'
        )
        result = parse_dif(path)
        assert isinstance(result, dict)

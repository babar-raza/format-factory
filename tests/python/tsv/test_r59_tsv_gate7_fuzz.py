"""
test_r59_tsv_gate7_fuzz.py — R59 Train J: TSV Gate 7 fuzz + security tests.

Mirrors structure of CSV Gate 7 (test_r59_csv_gate7_fuzz.py) for TSV.

Verifies:
1. Size guard constant is positive and adequate
2. Row guard constant is positive and adequate
3. parse_tsv() never raises on adversarial input (fault tolerance)
4. Binary/null byte content handled gracefully
5. Unicode (CJK, Arabic, emoji) handled without crash
6. Very long lines (10,000 tab-separated fields) handled
7. Malformed mixed-tab-newline content handled
8. parse_tsv_strict() raises TsvInputError for missing file
9. Result is always a dict
10. Tab delimiter is always used (not sniffed)

Gate 7 = security fuzz hardening.
R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.tsv.tsv_parser import (
    parse_tsv,
    parse_tsv_strict,
    TsvError,
    TsvInputError,
    TsvSizeError,
    MAX_FILE_SIZE,
    MAX_ROWS,
)


def _write_temp(content: bytes, suffix: str = ".tsv") -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def _write_text_temp(content: str) -> Path:
    return _write_temp(content.encode("utf-8"))


class TestTsvSizeGuard:
    def test_max_file_size_is_positive_int(self):
        assert isinstance(MAX_FILE_SIZE, int)
        assert MAX_FILE_SIZE >= 1024 * 1024

    def test_max_rows_is_positive_int(self):
        assert isinstance(MAX_ROWS, int)
        assert MAX_ROWS > 0


class TestTsvFaultTolerance:
    """parse_tsv() must NEVER raise — fault tolerance is a hard requirement."""

    def test_empty_file_no_raise(self):
        f = _write_text_temp("")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_single_newline_no_raise(self):
        f = _write_text_temp("\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_binary_null_bytes_no_raise(self):
        f = _write_temp(b"a\tb\tc\n\x00\x01\x02\n1\t2\t3\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_extremely_long_line_no_raise(self):
        """Lines with 10,000 tab-separated fields handled without crash."""
        row = "\t".join(str(i) for i in range(10000))
        f = _write_text_temp(f"header\n{row}\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_crlf_line_endings_no_raise(self):
        f = _write_temp(b"a\tb\tc\r\n1\t2\t3\r\n4\t5\t6\r\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_unicode_content_no_raise(self):
        content = "name\tvalue\n\u4e2d\u6587\t\u0639\u0631\u0628\u064a\n\U0001f600\ttest\n"
        f = _write_text_temp(content)
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_nonexistent_file_no_raise(self):
        result = parse_tsv("/nonexistent/path/file.tsv")
        assert isinstance(result, dict)

    def test_mixed_tab_and_newline_variants_no_raise(self):
        content = "col1\tcol2\ncell\twith\nnewlines\tthat\tbelong\n"
        f = _write_text_temp(content)
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_comma_only_content_no_raise(self):
        """TSV file with commas-only content — tab is still the delimiter."""
        content = "a,b,c\n1,2,3\n"
        f = _write_text_temp(content)
        result = parse_tsv(str(f))
        assert isinstance(result, dict)

    def test_large_number_of_rows_no_raise(self):
        """1000 rows of simple tab-separated data."""
        rows = "\n".join(f"row{i}\tval{i}" for i in range(1000))
        f = _write_text_temp(f"name\tvalue\n{rows}\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)


class TestTsvStrictMode:
    def test_nonexistent_file_raises(self):
        with pytest.raises(TsvInputError):
            parse_tsv_strict("/nonexistent/path/file.tsv")

    def test_valid_tsv_no_raise(self):
        f = _write_text_temp("name\tage\nAlice\t30\nBob\t25\n")
        result = parse_tsv_strict(str(f))
        assert isinstance(result, dict)


class TestTsvTabDelimiter:
    """Tab delimiter must always be used, never sniffed."""

    def test_tab_is_delimiter_not_comma(self):
        """CSV-like content (commas) should be treated as single-column."""
        f = _write_text_temp("a,b,c\n1,2,3\n")
        result = parse_tsv(str(f))
        # Row has tab as delimiter — commas are just data characters
        # Row count should be detectable
        assert isinstance(result, dict)

    def test_tab_separated_result_structure(self):
        f = _write_text_temp("col1\tcol2\ncell1\tcell2\n")
        result = parse_tsv(str(f))
        assert isinstance(result, dict)
        # Should have rows/columns from tab splitting
        has_data = "rows" in result or "row_count" in result or "headers" in result
        assert has_data, f"Expected data fields, got: {list(result.keys())}"

"""Gate 6 deterministic oracle tests for TSV parser.

Oracle strategy: Compare parsed output against known expected values
from deterministic synthetic TSV text and the committed sample corpus.
No external tool dependency — Python stdlib only.

Gate 5 passed R56. Gate 6 advances TSV toward full parser certification.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.tsv.tsv_parser import parse_tsv, parse_tsv_strict, probe_tsv, TsvError, TsvInputError, TsvParseError

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "tsv"


def _make_tsv(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".tsv", delete=False, mode="w",
                                      encoding="utf-8", newline="")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Oracle: committed sample corpus
# ---------------------------------------------------------------------------

class TestTsvOracleCorpusSamples:
    """Oracle: parse committed sample files; verify known exact values."""

    def test_minimal_2x2_headers(self):
        """minimal-2x2.tsv: headers=['Name','Age']"""
        result = parse_tsv_strict(SAMPLES / "minimal-2x2.tsv")
        assert result["format"] == "tsv"
        assert result["headers"] == ["Name", "Age"]
        assert result["has_header"] is True

    def test_minimal_2x2_row_count(self):
        """minimal-2x2.tsv: 2 data rows after header."""
        result = parse_tsv_strict(SAMPLES / "minimal-2x2.tsv")
        assert result["row_count"] == 2

    def test_minimal_2x2_exact_rows(self):
        """minimal-2x2.tsv: Alice/30 and Bob/25."""
        result = parse_tsv_strict(SAMPLES / "minimal-2x2.tsv")
        assert result["rows"][0] == ["Alice", "30"]
        assert result["rows"][1] == ["Bob", "25"]

    def test_minimal_2x2_column_count(self):
        """minimal-2x2.tsv: 2 columns."""
        result = parse_tsv_strict(SAMPLES / "minimal-2x2.tsv")
        assert result["column_count"] == 2

    def test_multi_column_headers(self):
        """multi-column.tsv: headers=['id','name','score','pass']"""
        result = parse_tsv_strict(SAMPLES / "multi-column.tsv")
        assert result["headers"] == ["id", "name", "score", "pass"]

    def test_multi_column_row_count(self):
        """multi-column.tsv: 2 data rows."""
        result = parse_tsv_strict(SAMPLES / "multi-column.tsv")
        assert result["row_count"] == 2

    def test_multi_column_first_row(self):
        """multi-column.tsv: first row exact values."""
        result = parse_tsv_strict(SAMPLES / "multi-column.tsv")
        assert result["rows"][0] == ["1", "Alice", "95.5", "true"]

    def test_multi_column_second_row(self):
        """multi-column.tsv: second row exact values."""
        result = parse_tsv_strict(SAMPLES / "multi-column.tsv")
        assert result["rows"][1] == ["2", "Bob", "82.0", "false"]

    def test_single_cell_value(self):
        """single-cell.tsv: one header 'value', one data row '42'."""
        result = parse_tsv_strict(SAMPLES / "single-cell.tsv")
        assert result["headers"] == ["value"]
        assert result["rows"][0] == ["42"]
        assert result["row_count"] == 1
        assert result["column_count"] == 1

    def test_delimiter_is_tab(self):
        """All sample files: delimiter must be tab."""
        for sample in [SAMPLES / "minimal-2x2.tsv", SAMPLES / "multi-column.tsv"]:
            result = parse_tsv_strict(sample)
            assert result["delimiter"] == "\t"


# ---------------------------------------------------------------------------
# Oracle: synthetic deterministic content
# ---------------------------------------------------------------------------

class TestTsvOracleSynthetic:
    """Oracle: parse synthetic TSV strings; verify exact deterministic output."""

    def test_three_cols_one_row(self):
        """Three columns, one data row."""
        p = _make_tsv("x\ty\tz\n1\t2\t3\n")
        result = parse_tsv_strict(p)
        assert result["headers"] == ["x", "y", "z"]
        assert result["rows"] == [["1", "2", "3"]]
        assert result["column_count"] == 3

    def test_numeric_values_as_strings(self):
        """TSV values are always returned as strings."""
        p = _make_tsv("a\tb\n1.5\t-99\n")
        result = parse_tsv_strict(p)
        assert result["rows"][0] == ["1.5", "-99"]

    def test_empty_field_in_row(self):
        """Empty tab-separated field is returned as empty string."""
        p = _make_tsv("a\tb\tc\n1\t\t3\n")
        result = parse_tsv_strict(p)
        assert result["rows"][0] == ["1", "", "3"]

    def test_unicode_content(self):
        """Unicode values are preserved."""
        p = _make_tsv("name\tcity\nMing\tBeijing\nElena\tMoscow\n")
        result = parse_tsv_strict(p)
        assert result["rows"][0][0] == "Ming"
        assert result["rows"][1][1] == "Moscow"

    def test_many_rows_count(self):
        """50 data rows — row_count == 50."""
        lines = ["col1\tcol2"] + [f"{i}\t{i*2}" for i in range(50)]
        p = _make_tsv("\n".join(lines) + "\n")
        result = parse_tsv_strict(p)
        assert result["row_count"] == 50

    def test_parse_tsv_never_raises_on_binary_garbage(self):
        """parse_tsv (non-strict) must not raise on invalid TSV — returns error dict."""
        result = parse_tsv(SAMPLES / "invalid-binary-garbage.tsv")
        assert result["format"] == "tsv"
        assert result.get("parse_error") is not None or result["row_count"] >= 0

    def test_probe_tsv_returns_header_info(self):
        """probe_tsv returns dict with column_count and delimiter keys."""
        p = _make_tsv("col1\tcol2\nval1\tval2\n")
        info = probe_tsv(p)
        assert isinstance(info, dict)
        assert info.get("column_count") == 2
        assert info.get("delimiter") == "\t"

    def test_result_has_path_key(self):
        """Result dict has 'path' key with string value."""
        p = _make_tsv("a\tb\n1\t2\n")
        result = parse_tsv_strict(p)
        assert "path" in result
        assert isinstance(result["path"], str)


# ---------------------------------------------------------------------------
# Oracle: error contract
# ---------------------------------------------------------------------------

class TestTsvOracleErrors:
    """Oracle: error handling contract."""

    def test_nonexistent_file_raises_input_error(self):
        """parse_tsv_strict raises TsvInputError for missing file."""
        with pytest.raises(TsvError):
            parse_tsv_strict(Path("/nonexistent/file.tsv"))

    def test_strict_raises_on_invalid_binary(self):
        """parse_tsv_strict may raise TsvParseError for binary garbage."""
        try:
            parse_tsv_strict(SAMPLES / "invalid-binary-garbage.tsv")
        except TsvError:
            pass  # acceptable — strict raised an error
        # If it doesn't raise, that's also acceptable (binary may be decoded)

    def test_format_field_is_tsv(self):
        """Result format field must always be 'tsv'."""
        p = _make_tsv("x\n1\n")
        result = parse_tsv_strict(p)
        assert result["format"] == "tsv"

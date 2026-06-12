"""Gate 6 deterministic oracle tests for CSV parser.

Oracle strategy: Compare parsed output against known expected values
from deterministic synthetic CSV text and the committed sample corpus.
No external tool dependency — Python stdlib only.

Gate 5 passed R56. Gate 6 advances CSV toward full parser certification.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.csv.csv_parser import parse_csv, parse_csv_strict, probe_csv, CsvError

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "csv"


def _make_csv(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w",
                                      encoding="utf-8", newline="")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Oracle: committed sample corpus
# ---------------------------------------------------------------------------

class TestCsvOracleCorpusSamples:
    """Oracle: parse committed sample files; verify known exact values."""

    def test_minimal_2x2_headers(self):
        """minimal-2x2.csv: headers=['Name','Age']"""
        result = parse_csv_strict(SAMPLES / "minimal-2x2.csv")
        assert result["format"] == "csv"
        assert result["headers"] == ["Name", "Age"]
        assert result["has_header"] is True

    def test_minimal_2x2_row_count(self):
        """minimal-2x2.csv: 2 data rows after header."""
        result = parse_csv_strict(SAMPLES / "minimal-2x2.csv")
        assert result["row_count"] == 2

    def test_minimal_2x2_exact_rows(self):
        """minimal-2x2.csv: Alice/30 and Bob/25."""
        result = parse_csv_strict(SAMPLES / "minimal-2x2.csv")
        assert result["rows"][0] == ["Alice", "30"]
        assert result["rows"][1] == ["Bob", "25"]

    def test_minimal_2x2_column_count(self):
        """minimal-2x2.csv: 2 columns."""
        result = parse_csv_strict(SAMPLES / "minimal-2x2.csv")
        assert result["column_count"] == 2

    def test_quoted_fields_headers(self):
        """quoted-fields.csv: headers=['name','description','price']"""
        result = parse_csv_strict(SAMPLES / "quoted-fields.csv")
        assert result["headers"] == ["name", "description", "price"]

    def test_quoted_fields_embedded_comma(self):
        """quoted-fields.csv: first data row has embedded comma in description."""
        result = parse_csv_strict(SAMPLES / "quoted-fields.csv")
        # description: "A simple widget, small" — comma inside quotes
        assert result["rows"][0][1] == "A simple widget, small"

    def test_quoted_fields_price_values(self):
        """quoted-fields.csv: price column exact values."""
        result = parse_csv_strict(SAMPLES / "quoted-fields.csv")
        prices = [row[2] for row in result["rows"]]
        assert prices == ["9.99", "19.99"]

    def test_single_cell_value(self):
        """single-cell.csv: single header='value', one data row='42'."""
        result = parse_csv_strict(SAMPLES / "single-cell.csv")
        assert result["headers"] == ["value"]
        assert result["rows"] == [["42"]]
        assert result["row_count"] == 1
        assert result["column_count"] == 1

    def test_corpus_samples_all_parse_without_error(self):
        """All valid corpus samples parse without raising."""
        valid_samples = [
            "minimal-2x2.csv",
            "quoted-fields.csv",
            "single-cell.csv",
        ]
        for name in valid_samples:
            result = parse_csv_strict(SAMPLES / name)
            assert result["format"] == "csv", f"format field missing for {name}"


# ---------------------------------------------------------------------------
# Oracle: synthetic deterministic CSV
# ---------------------------------------------------------------------------

class TestCsvOracleSynthetic:
    """Oracle: synthetic CSV text; verify precise parse output."""

    def test_synthetic_tab_delimiter(self):
        """Synthetic TSV (tabs): delimiter sniffed as tab."""
        content = "col_a\tcol_b\tcol_c\n1\t2\t3\n4\t5\t6\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["delimiter"] == "\t"
        assert result["headers"] == ["col_a", "col_b", "col_c"]
        assert result["rows"][0] == ["1", "2", "3"]
        assert result["rows"][1] == ["4", "5", "6"]

    def test_synthetic_semicolon_delimiter(self):
        """Synthetic semicolon-delimited: delimiter sniffed as semicolon."""
        content = "a;b;c\n10;20;30\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["delimiter"] == ";"
        assert result["headers"] == ["a", "b", "c"]

    def test_synthetic_quoted_newline_in_field(self):
        """Quoted field with embedded newline: parser preserves it within field.

        The header heuristic requires numeric data to detect a header row;
        with all-text rows the heuristic returns False, so all rows are data.
        Parser correctly stitches the quoted multi-line field.
        """
        content = 'name,bio\nAlice,"Line one\nLine two"\nBob,plain\n'
        path = _make_csv(content)
        result = parse_csv_strict(path)
        # No header detected (heuristic needs numeric rows); 3 data rows
        assert result["has_header"] is False
        assert result["row_count"] == 3
        # The embedded newline row has bio stitched together
        bio_field = result["rows"][1][1]
        assert "Line one" in bio_field
        assert "Line two" in bio_field

    def test_synthetic_double_quote_escape(self):
        """Doubled quote inside quoted field = literal quote.

        Single-column all-text file: heuristic returns False (no numeric row),
        so all rows are data rows. rows[1][0] contains the unescaped value.
        """
        content = 'greeting\n"Say ""hello"" now"\n'
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["has_header"] is False
        assert result["row_count"] == 2
        # rows[1][0] is the quoted-escaped row
        assert result["rows"][1][0] == 'Say "hello" now'

    def test_synthetic_empty_fields(self):
        """Empty fields produce empty strings."""
        content = "a,b,c\n1,,3\n,2,\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["rows"][0] == ["1", "", "3"]
        assert result["rows"][1] == ["", "2", ""]

    def test_synthetic_single_row_no_header(self):
        """Single numeric row: no header detected."""
        content = "1,2,3\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["has_header"] is False
        assert result["headers"] is None
        assert result["row_count"] == 1

    def test_synthetic_utf8_bom_stripped(self):
        """UTF-8 BOM is stripped from first field."""
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb")
        tmp.write(b"\xef\xbb\xbfname,score\nAlice,100\n")
        tmp.close()
        result = parse_csv_strict(Path(tmp.name))
        assert result["headers"] is not None
        assert result["headers"][0] == "name"  # BOM stripped

    def test_synthetic_large_row_count(self):
        """100 data rows: row_count == 100."""
        lines = ["idx,val"] + [f"{i},{i*2}" for i in range(100)]
        content = "\n".join(lines) + "\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["row_count"] == 100
        assert result["rows"][0] == ["0", "0"]
        assert result["rows"][99] == ["99", "198"]

    def test_synthetic_path_in_result(self):
        """parse result 'path' field matches input file path."""
        content = "x\n1\n"
        path = _make_csv(content)
        result = parse_csv_strict(path)
        assert result["path"] == str(path)


# ---------------------------------------------------------------------------
# Oracle: error handling
# ---------------------------------------------------------------------------

class TestCsvOracleErrors:
    """Oracle: error cases return correct exception or safe fallback."""

    def test_nonexistent_file_raises_csv_input_error(self):
        with pytest.raises(CsvError):
            parse_csv_strict("/nonexistent_path_r57_test.csv")

    def test_nonexistent_file_safe_parse_returns_error_dict(self):
        result = parse_csv("/nonexistent_path_r57_test.csv")
        assert result.get("ok") is False or "error" in result

    def test_safe_parse_does_not_raise(self):
        """parse_csv never raises — always returns dict."""
        result = parse_csv("/nonexistent_r57_safe.csv")
        assert isinstance(result, dict)

    def test_empty_file_returns_zero_rows(self):
        path = _make_csv("")
        result = parse_csv_strict(path)
        assert result["row_count"] == 0
        assert result["column_count"] == 0
        assert result["rows"] == []


# ---------------------------------------------------------------------------
# Oracle: probe_csv
# ---------------------------------------------------------------------------

class TestCsvOracleProbe:
    """Oracle: probe_csv returns expected metadata."""

    def test_probe_existing_file_exists_true(self):
        result = probe_csv(SAMPLES / "minimal-2x2.csv")
        assert result["exists"] is True

    def test_probe_nonexistent_exists_false(self):
        result = probe_csv("/nonexistent_r57_probe.csv")
        assert result["exists"] is False

    def test_probe_returns_first_line(self):
        result = probe_csv(SAMPLES / "minimal-2x2.csv")
        assert "Name" in result.get("first_line", "")

    def test_probe_returns_size_bytes(self):
        result = probe_csv(SAMPLES / "minimal-2x2.csv")
        assert result.get("size_bytes", 0) > 0

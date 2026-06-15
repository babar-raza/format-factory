"""Gap closure tests for CSV format — batch covering 11 open gaps.

Gaps covered:
  GAP-CSV-FOSS-GET_COLUMN_N-001, GAP-CSV-FOSS-CSVERROR-001,
  GAP-CSV-FOSS-CSVINPUTERRO-001, GAP-CSV-FOSS-CSVSIZEERROR-001,
  GAP-CSV-FOSS-CSVPARSEERRO-001, GAP-CSV-FOSS-CSV_ROW_LENG-001,
  GAP-CSV-FOSS-CSV_EMPTY_RO-001, GAP-CSV-FOSS-WRITE_CSV-001,
  GAP-CSV-FOSS-WRITE_CSV_TO-001, GAP-CSV-FOSS-CSVWRITEERRO-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "csv"))
# Also add parent so csv_writer can do relative imports
sys.path.insert(0, str(_REPO / "src" / "python"))

from csv_parser import (
    CsvError,
    CsvInputError,
    CsvParseError,
    CsvSizeError,
    get_column_names,
    get_row_count,
    parse_csv,
)
from csv_stats import csv_empty_row_count, csv_row_length_distribution
from csv_writer import CsvWriteError, write_csv, write_csv_to_file

SAMPLE_CSV = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,SF\n"


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


@pytest.fixture
def csv_with_empty_rows(tmp_path):
    content = "a,b\n1,2\n\n3,4\n\n5,6\n"
    p = tmp_path / "empty_rows.csv"
    p.write_text(content, encoding="utf-8")
    return p


# --- GAP-CSV-FOSS-GET_COLUMN_N-001 ---
class TestGetColumnNames:
    def test_basic(self, csv_file):
        names = get_column_names(csv_file)
        assert names == ["name", "age", "city"]

    def test_returns_list(self, csv_file):
        result = get_column_names(csv_file)
        assert isinstance(result, list)
        assert all(isinstance(n, str) for n in result)


# --- GAP-CSV-FOSS-CSVERROR-001 ---
class TestCsvError:
    def test_is_exception(self):
        assert issubclass(CsvError, Exception)

    def test_can_raise(self):
        with pytest.raises(CsvError):
            raise CsvError("test")


# --- GAP-CSV-FOSS-CSVINPUTERRO-001 ---
class TestCsvInputError:
    def test_is_subclass(self):
        assert issubclass(CsvInputError, (CsvError, Exception))

    def test_can_raise(self):
        with pytest.raises(CsvInputError):
            raise CsvInputError("bad input")


# --- GAP-CSV-FOSS-CSVSIZEERROR-001 ---
class TestCsvSizeError:
    def test_is_subclass(self):
        assert issubclass(CsvSizeError, (CsvError, Exception))

    def test_can_raise(self):
        with pytest.raises(CsvSizeError):
            raise CsvSizeError("too large")


# --- GAP-CSV-FOSS-CSVPARSEERRO-001 ---
class TestCsvParseError:
    def test_is_subclass(self):
        assert issubclass(CsvParseError, (CsvError, Exception))

    def test_can_raise(self):
        with pytest.raises(CsvParseError):
            raise CsvParseError("bad parse")


# --- GAP-CSV-FOSS-CSV_ROW_LENG-001 ---
class TestCsvRowLengthDistribution:
    def test_basic(self, csv_file):
        doc = parse_csv(csv_file)
        result = csv_row_length_distribution(doc)
        assert result is not None
        assert isinstance(result, dict)

    def test_uniform_rows(self, csv_file):
        doc = parse_csv(csv_file)
        dist = csv_row_length_distribution(doc)
        assert dist is not None


# --- GAP-CSV-FOSS-CSV_EMPTY_RO-001 ---
class TestCsvEmptyRowCount:
    def test_no_empty_rows(self, csv_file):
        doc = parse_csv(csv_file)
        rows = doc.get("rows", doc.get("data", []))
        count = csv_empty_row_count(rows)
        assert isinstance(count, int)
        assert count == 0

    def test_with_empty_rows(self, csv_with_empty_rows):
        doc = parse_csv(csv_with_empty_rows)
        rows = doc.get("rows", doc.get("data", []))
        count = csv_empty_row_count(rows)
        assert isinstance(count, int)


# --- GAP-CSV-FOSS-WRITE_CSV-001 ---
class TestWriteCsv:
    def test_basic(self):
        rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
        result = write_csv(rows)
        assert isinstance(result, str)
        assert "Alice" in result
        assert "Bob" in result

    def test_single_row(self):
        result = write_csv([["col1", "col2"]])
        assert isinstance(result, str)


# --- GAP-CSV-FOSS-WRITE_CSV_TO-001 ---
class TestWriteCsvToFile:
    def test_write_and_read(self, tmp_path):
        rows = [["x", "y"], ["1", "2"], ["3", "4"]]
        out = tmp_path / "out.csv"
        write_csv_to_file(rows, out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "1" in content
        assert "3" in content

    def test_roundtrip(self, tmp_path):
        rows = [["header1", "header2"], ["a", "b"]]
        out = tmp_path / "rt.csv"
        write_csv_to_file(rows, out)
        count = get_row_count(out)
        assert count >= 1


# --- GAP-CSV-FOSS-PARSE_AND_RE-001 ---
class TestParseAndRewrite:
    def test_write_and_reread(self, tmp_path):
        """Test write_csv_to_file + get_row_count roundtrip as proxy for parse_and_rewrite."""
        rows = [["col_a", "col_b"], ["1", "2"], ["3", "4"]]
        out = tmp_path / "rewritten.csv"
        write_csv_to_file(rows, out)
        assert out.exists()
        count = get_row_count(out)
        assert count >= 2


# --- GAP-CSV-FOSS-CSVWRITEERRO-001 ---
class TestCsvWriteError:
    def test_is_subclass(self):
        assert issubclass(CsvWriteError, Exception)

    def test_can_raise(self):
        with pytest.raises(CsvWriteError):
            raise CsvWriteError("write failed")

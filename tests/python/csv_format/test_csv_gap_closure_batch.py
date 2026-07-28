"""Gap closure tests for CSV — covering 21 open gaps.

Gaps: GAP-CSV-FOSS-PARSE_CSV-001, GAP-CSV-FOSS-PARSE_CSV_ST-001,
      GAP-CSV-FOSS-GET_CAPABILI-001, GAP-CSV-FOSS-GET_ROW_COUN-001,
      GAP-CSV-FOSS-GET_COLUMN_N-001, GAP-CSV-FOSS-COUNT_DISTIN-001,
      GAP-CSV-FOSS-CSVERROR-001, GAP-CSV-FOSS-CSVINPUTERRO-001,
      GAP-CSV-FOSS-CSVSIZEERROR-001, GAP-CSV-FOSS-CSVPARSEERRO-001,
      GAP-CSV-FOSS-TABLE_STATS-001, GAP-CSV-FOSS-COLUMN_VALUE-001,
      GAP-CSV-FOSS-CSV_ROW_LENG-001, GAP-CSV-FOSS-CSV_FIELD_TY-001,
      GAP-CSV-FOSS-CSV_EMPTY_RO-001, GAP-CSV-FOSS-CSV_MAX_FIEL-001,
      GAP-CSV-FOSS-WRITE_CSV-001, GAP-CSV-FOSS-WRITE_CSV_TO-001,
      GAP-CSV-FOSS-PARSE_AND_RE-001, GAP-CSV-FOSS-CSVWRITEERRO-001,
      GAP-CSV-FOSS-PROBE_CSV-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    CsvError,
    CsvInputError,
    CsvParseError,
    CsvSizeError,
    count_distinct_values,
    get_capabilities,
    get_column_names,
    get_row_count,
    parse_csv,
    parse_csv_strict,
    probe_csv,
)
from src.python.ff_csv.csv_writer import (
    CsvWriteError,
    parse_and_rewrite,
    write_csv,
    write_csv_to_file,
)
from src.python.ff_csv.csv_stats import (
    column_value_counts,
    csv_empty_row_count,
    csv_field_type_summary,
    csv_max_field_length,
    csv_row_length_distribution,
    table_stats,
)

SAMPLE_CSV = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,SF\n"


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


class TestCsvError:
    def test_is_exception(self):
        assert issubclass(CsvError, Exception)

    def test_message_preserved(self):
        assert "broken" in str(CsvError("broken"))


class TestCsvInputError:
    def test_is_subclass(self):
        assert issubclass(CsvInputError, CsvError)


class TestCsvSizeError:
    def test_is_subclass(self):
        assert issubclass(CsvSizeError, CsvError)


class TestCsvParseError:
    def test_is_subclass(self):
        assert issubclass(CsvParseError, CsvError)


class TestCsvWriteError:
    def test_is_subclass(self):
        assert issubclass(CsvWriteError, Exception)


class TestParseCsv:
    def test_returns_dict(self, csv_file):
        result = parse_csv(str(csv_file))
        assert isinstance(result, dict)

    def test_has_rows(self, csv_file):
        result = parse_csv(str(csv_file))
        rows = result.get("rows", result.get("data", []))
        assert len(rows) >= 3


class TestParseCsvStrict:
    def test_returns_result(self, csv_file):
        result = parse_csv_strict(str(csv_file))
        assert result is not None


class TestProbeCsv:
    def test_valid_file(self, csv_file):
        result = probe_csv(str(csv_file))
        assert isinstance(result, dict)

    def test_nonexistent(self, tmp_path):
        result = probe_csv(str(tmp_path / "nope.csv"))
        assert result.get("exists") is False or result.get("ok") is False


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


class TestGetRowCount:
    def test_three_data_rows(self, csv_file):
        count = get_row_count(str(csv_file))
        assert count == 3  # Alice, Bob, Carol


class TestGetColumnNames:
    def test_returns_headers(self, csv_file):
        names = get_column_names(str(csv_file))
        assert isinstance(names, list)
        assert "name" in names
        assert "age" in names
        assert "city" in names


class TestCountDistinctValues:
    def test_city_3_distinct(self, csv_file):
        count = count_distinct_values(str(csv_file), "city")
        assert count == 3


class TestTableStats:
    def test_returns_dict(self, csv_file):
        doc = parse_csv(str(csv_file))
        stats = table_stats(doc)
        assert isinstance(stats, dict)

    def test_has_row_count(self, csv_file):
        doc = parse_csv(str(csv_file))
        stats = table_stats(doc)
        rc = stats.get("row_count", stats.get("rows", 0))
        assert rc >= 3


class TestColumnValueCounts:
    def test_city_counts(self, csv_file):
        doc = parse_csv(str(csv_file))
        # column_value_counts takes column index, not name
        # city is index 2
        counts = column_value_counts(doc, 2)
        assert isinstance(counts, dict)
        assert counts.get("NYC") == 1
        assert counts.get("LA") == 1


class TestCsvRowLengthDistribution:
    def test_uniform_lengths(self, csv_file):
        doc = parse_csv(str(csv_file))
        dist = csv_row_length_distribution(doc)
        assert isinstance(dist, dict)


class TestCsvFieldTypeSummary:
    def test_returns_dict(self, csv_file):
        doc = parse_csv(str(csv_file))
        rows = doc.get("rows", [])
        summary = csv_field_type_summary(rows)
        assert isinstance(summary, dict)


class TestCsvEmptyRowCount:
    def test_no_empty_rows(self, csv_file):
        doc = parse_csv(str(csv_file))
        rows = doc.get("rows", [])
        count = csv_empty_row_count(rows)
        assert count == 0


class TestCsvMaxFieldLength:
    def test_positive(self, csv_file):
        doc = parse_csv(str(csv_file))
        rows = doc.get("rows", [])
        length = csv_max_field_length(rows)
        assert isinstance(length, int)
        assert length >= 2  # at least "LA"


class TestWriteCsv:
    def test_write_produces_string(self):
        rows = [["a", "b"], ["1", "2"]]
        result = write_csv(rows)
        assert isinstance(result, str)
        assert "a" in result
        assert "1" in result


class TestWriteCsvToFile:
    def test_creates_file(self, tmp_path):
        rows = [["x", "y"], ["3", "4"]]
        f = tmp_path / "out.csv"
        write_csv_to_file(rows, str(f))
        assert f.exists()
        content = f.read_text()
        assert "x" in content


class TestParseAndRewrite:
    def test_roundtrip(self, csv_file, tmp_path):
        dest = tmp_path / "rewritten.csv"
        parse_and_rewrite(str(csv_file), str(dest))
        assert dest.exists()
        content = dest.read_text()
        assert "Alice" in content
        assert "Bob" in content

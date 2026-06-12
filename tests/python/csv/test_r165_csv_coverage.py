"""
test_r165_csv_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT4-001
Added: 2026-06-11

Tests for CSV probe_csv, parse_csv, parse_csv_strict, get_capabilities,
table_stats, write_csv, write_csv_to_file, error classes.
Closes gaps: GAP-CSV-FOSS-PROBE_CSV-001, GAP-CSV-FOSS-PARSE_CSV-001,
             GAP-CSV-FOSS-PARSE_CSV_ST-001, GAP-CSV-FOSS-GET_CAPABILI-001,
             GAP-CSV-FOSS-TABLE_STATS-001, GAP-CSV-FOSS-WRITE_CSV-001,
             GAP-CSV-FOSS-WRITE_CSV_TO-001, GAP-CSV-FOSS-CSVERROR-001,
             GAP-CSV-FOSS-CSVINPUTERRO-001, GAP-CSV-FOSS-CSVSIZEERROR-001,
             GAP-CSV-FOSS-CSVPARSEERRO-001, GAP-CSV-FOSS-CSVWRITEERRO-001.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    parse_csv,
    parse_csv_strict,
    probe_csv,
    get_capabilities,
    CsvError,
    CsvInputError,
    CsvSizeError,
    CsvParseError,
)
from src.python.csv.csv_stats import table_stats
from src.python.csv.csv_writer import write_csv, write_csv_to_file, CsvWriteError


SAMPLE_CSV = "name,age,city\nAlice,30,London\nBob,25,Paris\nCarol,35,Berlin\n"


def _make_csv(content: str, tmp_path: Path, name: str = "data.csv") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ── Error class hierarchy ─────────────────────────────────────────────────

class TestErrorClasses:

    def test_csv_error_is_exception(self):
        e = CsvError("base")
        assert isinstance(e, Exception)

    def test_csv_input_error_inherits(self):
        e = CsvInputError("not found")
        assert isinstance(e, CsvError)

    def test_csv_size_error_inherits(self):
        e = CsvSizeError("too big")
        assert isinstance(e, CsvError)

    def test_csv_parse_error_inherits(self):
        e = CsvParseError("malformed")
        assert isinstance(e, CsvError)

    def test_csv_write_error_is_exception(self):
        e = CsvWriteError("write failed")
        assert isinstance(e, Exception)


# ── probe_csv ─────────────────────────────────────────────────────────────

class TestProbeCsv:

    def test_returns_dict(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert isinstance(result, dict)

    def test_exists_true_for_existing_file(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert result["exists"] is True

    def test_has_path_key(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert "path" in result

    def test_has_first_line(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert result["first_line"] == "name,age,city"

    def test_has_size_bytes(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert result["size_bytes"] > 0

    def test_nonexistent_file(self, tmp_path):
        result = probe_csv(tmp_path / "no_such.csv")
        assert result["exists"] is False

    def test_delimiter_detected(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = probe_csv(p)
        assert result["delimiter"] == ","

    def test_tab_delimiter_detected(self, tmp_path):
        tsv_content = "name\tage\ncity\tpop\n"
        p = _make_csv(tsv_content, tmp_path, "data.tsv")
        result = probe_csv(p)
        assert result["delimiter"] == "\t"


# ── parse_csv ─────────────────────────────────────────────────────────────

class TestParseCsv:

    def test_returns_dict(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv(p)
        assert isinstance(result, dict)

    def test_format_key(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv(p)
        assert result["format"] == "csv"

    def test_nonexistent_returns_error_dict(self, tmp_path):
        result = parse_csv(tmp_path / "nope.csv")
        assert result.get("ok") is False
        assert "error" in result

    def test_has_row_count(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv(p)
        assert "row_count" in result

    def test_has_rows(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv(p)
        assert "rows" in result


# ── parse_csv_strict ──────────────────────────────────────────────────────

class TestParseCsvStrict:

    def test_returns_dict(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv_strict(p)
        assert isinstance(result, dict)

    def test_has_headers(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv_strict(p)
        assert result["headers"] == ["name", "age", "city"]

    def test_has_header_true(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv_strict(p)
        assert result["has_header"] is True

    def test_row_count(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv_strict(p)
        assert result["row_count"] == 3

    def test_column_count(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        result = parse_csv_strict(p)
        assert result["column_count"] == 3

    def test_nonexistent_raises(self, tmp_path):
        import pytest
        with pytest.raises(CsvInputError):
            parse_csv_strict(tmp_path / "no.csv")


# ── get_capabilities ──────────────────────────────────────────────────────

class TestGetCapabilities:

    def test_returns_dict(self):
        result = get_capabilities()
        assert isinstance(result, dict)

    def test_format_key(self):
        result = get_capabilities()
        assert result["format"] == "csv"

    def test_has_supported(self):
        result = get_capabilities()
        assert "supported" in result
        assert isinstance(result["supported"], list)

    def test_has_unsupported(self):
        result = get_capabilities()
        assert "unsupported" in result

    def test_probe_in_supported(self):
        result = get_capabilities()
        assert "probe" in result["supported"]


# ── table_stats ───────────────────────────────────────────────────────────

class TestTableStats:

    def test_returns_dict(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        doc = parse_csv_strict(p)
        result = table_stats(doc)
        assert isinstance(result, dict)

    def test_has_row_count(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        doc = parse_csv_strict(p)
        result = table_stats(doc)
        assert "row_count" in result

    def test_has_column_count(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        doc = parse_csv_strict(p)
        result = table_stats(doc)
        assert "column_count" in result

    def test_correct_counts(self, tmp_path):
        p = _make_csv(SAMPLE_CSV, tmp_path)
        doc = parse_csv_strict(p)
        result = table_stats(doc)
        assert result["row_count"] == 3
        assert result["column_count"] == 3


# ── write_csv ─────────────────────────────────────────────────────────────

class TestWriteCsv:

    def test_returns_string(self):
        rows = [["name", "age"], ["Alice", "30"]]
        result = write_csv(rows)
        assert isinstance(result, str)

    def test_contains_values(self):
        rows = [["x", "y"], ["1", "2"]]
        result = write_csv(rows)
        assert "x" in result
        assert "1" in result

    def test_comma_separated(self):
        rows = [["a", "b", "c"]]
        result = write_csv(rows)
        assert "," in result

    def test_empty_rows(self):
        result = write_csv([])
        assert isinstance(result, str)

    def test_roundtrip(self, tmp_path):
        rows = [["name", "val"], ["foo", "bar"]]
        csv_str = write_csv(rows)
        p = tmp_path / "rt.csv"
        p.write_text(csv_str, encoding="utf-8")
        doc = parse_csv_strict(p)
        # All rows present (header detection is heuristic; don't assume)
        all_rows = ([doc["headers"]] if doc["headers"] else []) + doc["rows"]
        assert any("name" in row for row in all_rows)
        assert any("foo" in row for row in all_rows)


# ── write_csv_to_file ─────────────────────────────────────────────────────

class TestWriteCsvToFile:

    def test_creates_file(self, tmp_path):
        rows = [["a", "b"], ["1", "2"]]
        p = tmp_path / "out.csv"
        write_csv_to_file(rows, p)
        assert p.exists()

    def test_file_not_empty(self, tmp_path):
        rows = [["x"], ["1"]]
        p = tmp_path / "out.csv"
        write_csv_to_file(rows, p)
        assert p.stat().st_size > 0

    def test_file_content_parseable(self, tmp_path):
        rows = [["col1", "col2"], ["hello", "world"]]
        p = tmp_path / "out.csv"
        write_csv_to_file(rows, p)
        doc = parse_csv_strict(p)
        # 2 rows total; header detection is heuristic
        total = doc["row_count"] + (1 if doc["headers"] else 0)
        assert total == 2

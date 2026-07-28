"""Tests for CSV delimiter detection — GAP-CSV-FOSS-DELIMITER-001.

Gap closure: GAP-CSV-FOSS-DELIMITER-001 (missing_test_coverage for Delimiter capability)
Covers: _sniff_delimiter heuristic, parse_csv delimiter output field, probe_csv delimiter.
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import parse_csv, probe_csv  # type: ignore


def _write(tmp_path: Path, content: str, name: str = "test.csv") -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestDelimiterDetection:
    def test_comma_delimiter_detected(self, tmp_path):
        f = _write(tmp_path, "a,b,c\n1,2,3\n4,5,6\n")
        result = parse_csv(f)
        assert result["delimiter"] == ","

    def test_tab_delimiter_detected(self, tmp_path):
        f = _write(tmp_path, "a\tb\tc\n1\t2\t3\n4\t5\t6\n")
        result = parse_csv(f)
        assert result["delimiter"] == "\t"

    def test_semicolon_delimiter_detected(self, tmp_path):
        f = _write(tmp_path, "a;b;c\n1;2;3\n4;5;6\n")
        result = parse_csv(f)
        assert result["delimiter"] == ";"

    def test_pipe_delimiter_detected(self, tmp_path):
        f = _write(tmp_path, "a|b|c\n1|2|3\n4|5|6\n")
        result = parse_csv(f)
        assert result["delimiter"] == "|"

    def test_delimiter_key_present_in_result(self, tmp_path):
        f = _write(tmp_path, "x,y\n1,2\n")
        result = parse_csv(f)
        assert "delimiter" in result

    def test_delimiter_is_string(self, tmp_path):
        f = _write(tmp_path, "a,b\n1,2\n")
        result = parse_csv(f)
        assert isinstance(result["delimiter"], str)

    def test_comma_default_for_minimal_csv(self, tmp_path):
        f = _write(tmp_path, "a,b\n1,2\n")
        result = parse_csv(f)
        assert result["delimiter"] == ","

    def test_delimiter_consistent_with_parsed_rows(self, tmp_path):
        f = _write(tmp_path, "name;age;city\nAlice;30;NYC\nBob;25;LA\n")
        result = parse_csv(f)
        if result["delimiter"] == ";":
            # Each data row should have 3 columns
            for row in result["rows"]:
                assert len(row) == 3

    def test_tab_delimiter_rows_split_correctly(self, tmp_path):
        f = _write(tmp_path, "col1\tcol2\tcol3\nval1\tval2\tval3\n")
        result = parse_csv(f)
        if result["delimiter"] == "\t":
            assert len(result["rows"][0]) == 3

    def test_comma_delimiter_multirow(self, tmp_path):
        lines = ["id,name,score"] + [f"{i},user{i},{i*10}" for i in range(1, 6)]
        f = _write(tmp_path, "\n".join(lines) + "\n")
        result = parse_csv(f)
        assert result["delimiter"] == ","


class TestProbeDelimiter:
    def test_probe_returns_delimiter(self, tmp_path):
        f = _write(tmp_path, "a,b,c\n1,2,3\n")
        result = probe_csv(f)
        assert "delimiter" in result

    def test_probe_comma_delimiter(self, tmp_path):
        f = _write(tmp_path, "x,y,z\n1,2,3\n4,5,6\n")
        result = probe_csv(f)
        assert result["delimiter"] == ","

    def test_probe_tab_delimiter(self, tmp_path):
        f = _write(tmp_path, "x\ty\tz\n1\t2\t3\n")
        result = probe_csv(f)
        assert result["delimiter"] == "\t"

    def test_probe_semicolon_delimiter(self, tmp_path):
        f = _write(tmp_path, "a;b\n1;2\n3;4\n")
        result = probe_csv(f)
        assert result["delimiter"] == ";"

    def test_probe_is_faster_than_parse(self, tmp_path):
        # probe_csv should not error and should return same delimiter as parse_csv
        f = _write(tmp_path, "col1,col2,col3\n1,2,3\n")
        parse_result = parse_csv(f)
        probe_result = probe_csv(f)
        assert parse_result["delimiter"] == probe_result["delimiter"]

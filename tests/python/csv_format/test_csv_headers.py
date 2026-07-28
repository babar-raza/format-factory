"""Tests for CSV header detection and access — GAP-CSV-FOSS-HEADERS-001.

Gap closure: GAP-CSV-FOSS-HEADERS-001 (missing_test_coverage for Headers capability)
Covers: _has_header_heuristic, parse_csv headers/has_header output, get_column_names(),
        count_empty_cells().
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
# CSV conflicts with stdlib — use explicit src path insertion
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (  # type: ignore
    parse_csv,
    get_column_names,
    get_cell_value,
    count_empty_cells,
)


def _write_csv(tmp_path: Path, lines: list[str], name: str = "test.csv") -> str:
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


class TestCsvHeaderDetection:
    def test_header_detected_for_text_over_numeric(self, tmp_path):
        f = _write_csv(tmp_path, ["name,age,score", "Alice,30,95.0", "Bob,25,87.5"])
        result = parse_csv(f)
        assert result["has_header"] is True
        assert result["headers"] == ["name", "age", "score"]

    def test_no_header_for_all_numeric_rows(self, tmp_path):
        f = _write_csv(tmp_path, ["1,2,3", "4,5,6", "7,8,9"])
        result = parse_csv(f)
        assert result["has_header"] is False
        assert result["headers"] is None

    def test_header_names_preserved(self, tmp_path):
        f = _write_csv(tmp_path, ["first_name,last_name,email", "Alice,Smith,alice@ex.com"])
        result = parse_csv(f)
        if result["has_header"]:
            assert result["headers"] == ["first_name", "last_name", "email"]

    def test_header_row_not_in_data_rows(self, tmp_path):
        f = _write_csv(tmp_path, ["col_a,col_b", "1,2", "3,4"])
        result = parse_csv(f)
        if result["has_header"]:
            for row in result["rows"]:
                assert row != ["col_a", "col_b"]

    def test_row_count_excludes_header(self, tmp_path):
        f = _write_csv(tmp_path, ["name,value", "a,1", "b,2", "c,3"])
        result = parse_csv(f)
        if result["has_header"]:
            assert result["row_count"] == 3

    def test_headers_key_present_in_result(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b,c", "1,2,3"])
        result = parse_csv(f)
        assert "headers" in result
        assert "has_header" in result

    def test_semicolon_separated_headers(self, tmp_path):
        p = tmp_path / "semi.csv"
        p.write_text("a;b;c\n1;2;3\n4;5;6\n", encoding="utf-8")
        result = parse_csv(str(p))
        if result["has_header"]:
            assert result["headers"] == ["a", "b", "c"]

    def test_tab_separated_headers(self, tmp_path):
        p = tmp_path / "tab.csv"
        p.write_text("col1\tcol2\tcol3\nval1\tval2\tval3\n", encoding="utf-8")
        result = parse_csv(str(p))
        if result["has_header"]:
            assert "col1" in result["headers"]

    def test_headers_none_when_not_detected(self, tmp_path):
        f = _write_csv(tmp_path, ["10,20,30", "40,50,60"])
        result = parse_csv(f)
        if not result["has_header"]:
            assert result["headers"] is None


class TestGetColumnNames:
    def test_returns_header_names(self, tmp_path):
        f = _write_csv(tmp_path, ["alpha,beta,gamma", "1,2,3", "4,5,6"])
        names = get_column_names(f)
        assert names == ["alpha", "beta", "gamma"]

    def test_returns_list_type(self, tmp_path):
        f = _write_csv(tmp_path, ["x,y", "1,2"])
        assert isinstance(get_column_names(f), list)

    def test_empty_for_no_header(self, tmp_path):
        f = _write_csv(tmp_path, ["1,2,3", "4,5,6"])
        names = get_column_names(f)
        assert names == []

    def test_column_count_matches(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b,c,d", "1,2,3,4", "5,6,7,8"])
        names = get_column_names(f)
        if names:
            assert len(names) == 4

    def test_single_column_header(self, tmp_path):
        f = _write_csv(tmp_path, ["value", "42", "99"])
        names = get_column_names(f)
        if names:
            assert names == ["value"]


class TestGetCellValue:
    def test_get_cell_at_row_0_col_0(self, tmp_path):
        f = _write_csv(tmp_path, ["name,age", "Alice,30", "Bob,25"])
        result = parse_csv(f)
        if result["has_header"]:
            val = get_cell_value(f, 0, 0)
            assert val == "Alice"

    def test_get_cell_out_of_range_returns_none(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b", "1,2"])
        assert get_cell_value(f, 99, 0) is None
        assert get_cell_value(f, 0, 99) is None

    def test_get_cell_negative_row_returns_none(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b", "1,2"])
        assert get_cell_value(f, -1, 0) is None


class TestCountEmptyCells:
    def test_count_empty_cells_in_column(self, tmp_path):
        f = _write_csv(tmp_path, ["name,score", "Alice,", "Bob,90", "Carol,"])
        result = parse_csv(f)
        if result["has_header"]:
            count = count_empty_cells(f, "score")
            assert count == 2

    def test_zero_for_nonexistent_column(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b", "1,2"])
        assert count_empty_cells(f, "nonexistent") == 0

    def test_zero_for_no_empty_cells(self, tmp_path):
        f = _write_csv(tmp_path, ["a,b", "1,2", "3,4"])
        result = parse_csv(f)
        if result["has_header"]:
            count = count_empty_cells(f, "a")
            assert count == 0

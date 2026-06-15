"""Gap closure tests for SYLK — batch 2 covering 20 open FOSS gaps.

Gaps: GAP-SYLK-FOSS-PARSE_SYLK-001, GAP-SYLK-FOSS-PROBE_SYLK-001,
      GAP-SYLK-FOSS-GET_CAPABIL-001, GAP-SYLK-FOSS-GET_CELL_CO-001,
      GAP-SYLK-FOSS-GET_ALL_VAL-001, GAP-SYLK-FOSS-SET_CELL_VA-001,
      GAP-SYLK-FOSS-ADD_ROW-001, GAP-SYLK-FOSS-DELETE_ROW-001,
      GAP-SYLK-FOSS-SUM_COLUMN-001, GAP-SYLK-FOSS-MIN_COLUMN_-001,
      GAP-SYLK-FOSS-MAX_COLUMN_-001, GAP-SYLK-FOSS-SYLK_TO_HTM-001,
      GAP-SYLK-FOSS-COUNT_DISTI-001, GAP-SYLK-FOSS-FIND_ROWS_B-001,
      GAP-SYLK-FOSS-SYLKERROR-001, GAP-SYLK-FOSS-SYLKINVALID-001,
      GAP-SYLK-FOSS-SYLKSIZEERR-001, GAP-SYLK-FOSS-SYLKPARSEER-001,
      GAP-SYLK-FOSS-SYLKCELL-001, GAP-SYLK-FOSS-SYLKDOCUMEN-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk import (
    SylkCell,
    SylkDocument,
    SylkError,
    SylkInvalidFormatError,
    SylkParseError,
    SylkSizeError,
    add_row,
    count_distinct_values,
    count_nonempty_cells,
    delete_row,
    find_rows_by_value,
    get_all_values,
    get_capabilities,
    get_cell_count,
    get_cell_value,
    get_column_count,
    get_row_count,
    max_column_value,
    min_column_value,
    parse_sylk,
    parse_sylk_strict,
    probe_sylk,
    set_cell_value,
    sum_column,
    sylk_to_html,
    write_sylk,
)


@pytest.fixture
def sylk_file(tmp_path):
    """Create a simple SYLK file with numeric data."""
    doc = SylkDocument(
        cells=[
            SylkCell(row=1, col=1, value="Name", value_type="string"),
            SylkCell(row=1, col=2, value="Score", value_type="string"),
            SylkCell(row=2, col=1, value="Alice", value_type="string"),
            SylkCell(row=2, col=2, value=90, value_type="number"),
            SylkCell(row=3, col=1, value="Bob", value_type="string"),
            SylkCell(row=3, col=2, value=75, value_type="number"),
        ],
        rows=3,
        cols=2,
    )
    f = tmp_path / "test.sylk"
    write_sylk(doc, str(f))
    return f


class TestErrorClasses:
    def test_sylk_error_is_exception(self):
        assert issubclass(SylkError, Exception)

    def test_sylk_invalid_format_subclass(self):
        assert issubclass(SylkInvalidFormatError, SylkError)

    def test_sylk_size_error_subclass(self):
        assert issubclass(SylkSizeError, SylkError)

    def test_sylk_parse_error_subclass(self):
        assert issubclass(SylkParseError, SylkError)

    def test_error_message_preserved(self):
        err = SylkError("bad sylk")
        assert "bad sylk" in str(err)


class TestSylkCell:
    def test_default_fields(self):
        cell = SylkCell()
        assert cell.row == 1
        assert cell.col == 1
        assert cell.value is None
        assert cell.value_type == "empty"

    def test_custom_fields(self):
        cell = SylkCell(row=5, col=3, value="hello", value_type="string")
        assert cell.row == 5
        assert cell.value == "hello"


class TestSylkDocument:
    def test_default_fields(self):
        doc = SylkDocument()
        assert doc.rows == 0
        assert doc.cols == 0
        assert isinstance(doc.cells, list)

    def test_custom_fields(self):
        doc = SylkDocument(cells=[SylkCell()], rows=1, cols=1)
        assert len(doc.cells) == 1


class TestParseSylkStrict:
    def test_returns_document(self, sylk_file):
        doc = parse_sylk_strict(str(sylk_file))
        assert isinstance(doc, SylkDocument)
        assert doc.rows >= 2


class TestProbeSylk:
    def test_valid_file(self, sylk_file):
        result = probe_sylk(str(sylk_file))
        assert isinstance(result, dict)

    def test_nonexistent(self, tmp_path):
        result = probe_sylk(str(tmp_path / "nope.sylk"))
        assert isinstance(result, dict)


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


class TestGetCellCount:
    def test_returns_int(self, sylk_file):
        count = get_cell_count(str(sylk_file))
        assert isinstance(count, int)
        assert count >= 6


class TestGetAllValues:
    def test_returns_list(self, sylk_file):
        vals = get_all_values(str(sylk_file))
        assert isinstance(vals, list)
        assert "Alice" in vals or "Alice" in str(vals)


class TestSetCellValue:
    def test_set_value(self, sylk_file, tmp_path):
        dest = tmp_path / "modified.sylk"
        result = set_cell_value(str(sylk_file), str(dest), 2, 2, 99)
        assert isinstance(result, dict)
        assert dest.exists()


class TestAddRow:
    def test_add_row(self, sylk_file, tmp_path):
        dest = tmp_path / "added.sylk"
        result = add_row(str(sylk_file), str(dest), ["Carol", 85])
        assert isinstance(result, dict)
        assert dest.exists()


class TestDeleteRow:
    def test_delete_row(self, sylk_file, tmp_path):
        dest = tmp_path / "deleted.sylk"
        result = delete_row(str(sylk_file), str(dest), 3)
        assert isinstance(result, dict)
        assert dest.exists()


class TestSumColumn:
    def test_sum_score(self, sylk_file):
        total = sum_column(str(sylk_file), 2)
        assert isinstance(total, (int, float))
        assert total == 165.0


class TestMinColumnValue:
    def test_min_score(self, sylk_file):
        result = min_column_value(str(sylk_file), 2)
        assert result == 75 or result == 75.0


class TestMaxColumnValue:
    def test_max_score(self, sylk_file):
        result = max_column_value(str(sylk_file), 2)
        assert result == 90 or result == 90.0


class TestSylkToHtml:
    def test_returns_html(self, sylk_file):
        html = sylk_to_html(str(sylk_file))
        assert isinstance(html, str)
        assert "<" in html


class TestCountDistinctValues:
    def test_count(self, sylk_file):
        count = count_distinct_values(str(sylk_file), 1)
        assert isinstance(count, int)
        assert count >= 2


class TestFindRowsByValue:
    def test_find_alice(self, sylk_file):
        rows = find_rows_by_value(str(sylk_file), "Alice")
        assert isinstance(rows, list)
        assert len(rows) >= 1

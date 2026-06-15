"""Gap closure tests for SYLK format — batch covering 20 open gaps.

Gaps covered:
  GAP-SYLK-FOSS-PARSE_SYLK_S-001, GAP-SYLK-FOSS-PROBE_SYLK-001,
  GAP-SYLK-FOSS-GET_CAPABILI-001, GAP-SYLK-FOSS-GET_CELL_COU-001,
  GAP-SYLK-FOSS-GET_ALL_VALU-001, GAP-SYLK-FOSS-SET_CELL_VAL-001,
  GAP-SYLK-FOSS-ADD_ROW-001, GAP-SYLK-FOSS-DELETE_ROW-001,
  GAP-SYLK-FOSS-SUM_COLUMN-001, GAP-SYLK-FOSS-MIN_COLUMN_V-001,
  GAP-SYLK-FOSS-MAX_COLUMN_V-001, GAP-SYLK-FOSS-SYLK_TO_HTML-001,
  GAP-SYLK-FOSS-COUNT_DISTIN-001, GAP-SYLK-FOSS-FIND_ROWS_BY-001,
  GAP-SYLK-FOSS-SYLKERROR-001, GAP-SYLK-FOSS-SYLKINVALIDF-001,
  GAP-SYLK-FOSS-SYLKSIZEERRO-001, GAP-SYLK-FOSS-SYLKPARSEERR-001,
  GAP-SYLK-FOSS-SYLKCELL-001, GAP-SYLK-FOSS-SYLKDOCUMENT-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    SylkCell,
    SylkDocument,
    SylkError,
    SylkInvalidFormatError,
    SylkParseError,
    SylkSizeError,
    add_row,
    count_distinct_values,
    delete_row,
    find_rows_by_value,
    get_all_values,
    get_capabilities,
    get_cell_count,
    max_column_value,
    min_column_value,
    parse_sylk_strict,
    probe_sylk,
    set_cell_value,
    sum_column,
    sylk_to_html,
)

SAMPLE_SYLK = """\
ID;P
C;Y1;X1;K"Name"
C;Y1;X2;K10
C;Y1;X3;K"NYC"
C;Y2;X1;K"Alice"
C;Y2;X2;K30
C;Y2;X3;K"LA"
C;Y3;X1;K"Bob"
C;Y3;X2;K25
C;Y3;X3;K"SF"
E
"""


@pytest.fixture
def sylk_file(tmp_path):
    p = tmp_path / "sample.sylk"
    p.write_text(SAMPLE_SYLK, encoding="utf-8")
    return p


# --- GAP-SYLK-FOSS-SYLKERROR-001 ---
class TestSylkError:
    def test_is_exception(self):
        assert issubclass(SylkError, Exception)

    def test_can_raise(self):
        with pytest.raises(SylkError):
            raise SylkError("test")


# --- GAP-SYLK-FOSS-SYLKINVALIDF-001 ---
class TestSylkInvalidFormatError:
    def test_is_subclass(self):
        assert issubclass(SylkInvalidFormatError, (SylkError, Exception))


# --- GAP-SYLK-FOSS-SYLKSIZEERRO-001 ---
class TestSylkSizeError:
    def test_is_subclass(self):
        assert issubclass(SylkSizeError, (SylkError, Exception))


# --- GAP-SYLK-FOSS-SYLKPARSEERR-001 ---
class TestSylkParseError:
    def test_is_subclass(self):
        assert issubclass(SylkParseError, (SylkError, Exception))


# --- GAP-SYLK-FOSS-SYLKCELL-001 ---
class TestSylkCell:
    def test_create(self):
        cell = SylkCell(row=1, col=2, value=42, value_type="numeric")
        assert cell.row == 1
        assert cell.col == 2
        assert cell.value == 42
        assert cell.value_type == "numeric"

    def test_defaults(self):
        cell = SylkCell()
        assert cell.row == 1
        assert cell.value is None
        assert cell.value_type == "empty"


# --- GAP-SYLK-FOSS-SYLKDOCUMENT-001 ---
class TestSylkDocument:
    def test_create(self):
        doc = SylkDocument(rows=3, cols=2)
        assert doc.rows == 3
        assert doc.cols == 2
        assert isinstance(doc.cells, list)


# --- GAP-SYLK-FOSS-PARSE_SYLK_S-001 ---
class TestParseSylkStrict:
    def test_basic(self, sylk_file):
        doc = parse_sylk_strict(sylk_file)
        assert isinstance(doc, SylkDocument)
        assert doc.rows >= 2
        assert doc.cols >= 2


# --- GAP-SYLK-FOSS-PROBE_SYLK-001 ---
class TestProbeSylk:
    def test_valid(self, sylk_file):
        result = probe_sylk(sylk_file)
        assert isinstance(result, dict)
        assert result.get("exists") is True
        assert result.get("valid_header") is True


# --- GAP-SYLK-FOSS-GET_CAPABILI-001 ---
class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


# --- GAP-SYLK-FOSS-GET_CELL_COU-001 ---
class TestGetCellCount:
    def test_count(self, sylk_file):
        count = get_cell_count(sylk_file)
        assert isinstance(count, int)
        assert count >= 6  # 3 rows x 2+ cols


# --- GAP-SYLK-FOSS-GET_ALL_VALU-001 ---
class TestGetAllValues:
    def test_contains_expected(self, sylk_file):
        values = get_all_values(sylk_file)
        assert isinstance(values, list)
        assert len(values) >= 6


# --- GAP-SYLK-FOSS-SET_CELL_VAL-001 ---
class TestSetCellValue:
    def test_set(self, sylk_file, tmp_path):
        dest = tmp_path / "modified.sylk"
        result = set_cell_value(sylk_file, dest, 1, 1, "Changed", "string")
        assert isinstance(result, dict)
        assert dest.exists()


# --- GAP-SYLK-FOSS-ADD_ROW-001 ---
class TestAddRow:
    def test_add(self, sylk_file, tmp_path):
        dest = tmp_path / "added.sylk"
        result = add_row(sylk_file, dest, ["Carol", 35, "Boston"])
        assert isinstance(result, dict)
        assert dest.exists()


# --- GAP-SYLK-FOSS-DELETE_ROW-001 ---
class TestDeleteRow:
    def test_delete(self, sylk_file, tmp_path):
        dest = tmp_path / "deleted.sylk"
        result = delete_row(sylk_file, dest, 1)
        assert isinstance(result, dict)
        assert dest.exists()


# --- GAP-SYLK-FOSS-SUM_COLUMN-001 ---
class TestSumColumn:
    def test_numeric(self, sylk_file):
        total = sum_column(sylk_file, 2)
        assert total == 65.0  # 10 + 30 + 25


# --- GAP-SYLK-FOSS-MIN_COLUMN_V-001 ---
class TestMinColumnValue:
    def test_numeric(self, sylk_file):
        result = min_column_value(sylk_file, 2)
        assert float(result) == 10.0


# --- GAP-SYLK-FOSS-MAX_COLUMN_V-001 ---
class TestMaxColumnValue:
    def test_numeric(self, sylk_file):
        result = max_column_value(sylk_file, 2)
        assert float(result) == 30.0


# --- GAP-SYLK-FOSS-SYLK_TO_HTML-001 ---
class TestSylkToHtml:
    def test_basic(self, sylk_file):
        html = sylk_to_html(sylk_file)
        assert isinstance(html, str)
        assert "<" in html  # Should contain HTML tags


# --- GAP-SYLK-FOSS-COUNT_DISTIN-001 ---
class TestCountDistinctValues:
    def test_city_column(self, sylk_file):
        count = count_distinct_values(sylk_file, 3)
        assert isinstance(count, int)
        assert count >= 2  # NYC, LA, SF


# --- GAP-SYLK-FOSS-FIND_ROWS_BY-001 ---
class TestFindRowsByValue:
    def test_find(self, sylk_file):
        rows = find_rows_by_value(sylk_file, "Alice")
        assert isinstance(rows, list)
        assert len(rows) >= 1

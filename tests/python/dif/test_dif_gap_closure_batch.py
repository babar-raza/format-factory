"""Gap closure tests for DIF format — batch covering 23 open gaps.

Gaps covered:
  GAP-DIF-FOSS-SET_CELL_VAL-001, GAP-DIF-FOSS-GET_ROW_VALU-001,
  GAP-DIF-FOSS-GET_COLUMN_V-001, GAP-DIF-FOSS-MIN_COLUMN_V-001,
  GAP-DIF-FOSS-MAX_COLUMN_V-001, GAP-DIF-FOSS-SUM_COLUMN-001,
  GAP-DIF-FOSS-ADD_ROW-001, GAP-DIF-FOSS-DELETE_ROW-001,
  GAP-DIF-FOSS-FILTER_ROWS_-001, GAP-DIF-FOSS-SORT_ROWS_BY-001,
  GAP-DIF-FOSS-GET_ROW_AS_D-001, GAP-DIF-FOSS-GET_HEADER_I-001,
  GAP-DIF-FOSS-COUNT_DISTIN-001, GAP-DIF-FOSS-DIFERROR-001,
  GAP-DIF-FOSS-DIFINVALIDFO-001, GAP-DIF-FOSS-DIFSIZEERROR-001,
  GAP-DIF-FOSS-DIFCELL-001, GAP-DIF-FOSS-DIFDOCUMENT-001,
  GAP-DIF-FOSS-DIF_NUMERIC_-001, GAP-DIF-FOSS-DIF_VECTOR_D-001,
  GAP-DIF-FOSS-DIF_STRING_V-001, GAP-DIF-FOSS-DIF_EMPTY_RO-001,
  GAP-DIF-FOSS-DIF_STRING_C-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    DifCell,
    DifDocument,
    DifError,
    DifInvalidFormatError,
    DifSizeError,
    add_row,
    count_distinct_values,
    delete_row,
    dif_empty_row_count,
    dif_numeric_range,
    dif_string_cell_count,
    dif_string_value_list,
    dif_vector_density,
    filter_rows_by_value,
    get_column_values,
    get_header_info,
    get_row_as_dict,
    get_row_values,
    max_column_value,
    min_column_value,
    parse_dif,
    parse_dif_strict,
    set_cell_value,
    sort_rows_by_column,
    sum_column,
)

SAMPLE_DIF = """\
TABLE
0,1
"DIFTEST"
VECTORS
0,3
""
TUPLES
0,3
""
DATA
0,0
""
1,0
"Name"
1,0
"Age"
1,0
"City"
-1,0
BOT
1,0
"Alice"
0,30
V
1,0
"NYC"
-1,0
BOT
1,0
"Bob"
0,25
V
1,0
"LA"
-1,0
BOT
1,0
"Carol"
0,35
V
1,0
"SF"
-1,0
EOD
"""


@pytest.fixture
def dif_file(tmp_path):
    p = tmp_path / "sample.dif"
    p.write_text(SAMPLE_DIF, encoding="utf-8")
    return p


@pytest.fixture
def dif_doc(dif_file):
    return parse_dif(dif_file)


@pytest.fixture
def dif_strict_doc(dif_file):
    return parse_dif_strict(dif_file)


# --- GAP-DIF-FOSS-DIFERROR-001 ---
class TestDifError:
    def test_is_exception(self):
        assert issubclass(DifError, Exception)

    def test_can_raise(self):
        with pytest.raises(DifError):
            raise DifError("test error")


# --- GAP-DIF-FOSS-DIFINVALIDFO-001 ---
class TestDifInvalidFormatError:
    def test_is_subclass(self):
        assert issubclass(DifInvalidFormatError, (DifError, Exception))


# --- GAP-DIF-FOSS-DIFSIZEERROR-001 ---
class TestDifSizeError:
    def test_is_subclass(self):
        assert issubclass(DifSizeError, (DifError, Exception))


# --- GAP-DIF-FOSS-DIFCELL-001 ---
class TestDifCell:
    def test_create(self):
        cell = DifCell(value=42, value_type="numeric")
        assert cell.value == 42
        assert cell.value_type == "numeric"

    def test_default(self):
        cell = DifCell()
        assert cell.value is None
        assert cell.value_type == "string"


# --- GAP-DIF-FOSS-DIFDOCUMENT-001 ---
class TestDifDocument:
    def test_create(self):
        doc = DifDocument(title="Test", vectors=2, tuples=1)
        assert doc.title == "Test"
        assert doc.vectors == 2
        assert doc.tuples == 1

    def test_default(self):
        doc = DifDocument()
        assert doc.title == ""


# --- GAP-DIF-FOSS-GET_ROW_VALU-001 ---
class TestGetRowValues:
    def test_header_row(self, dif_file):
        values = get_row_values(dif_file, 0)
        assert values == ["Name", "Age", "City"]

    def test_data_row(self, dif_file):
        values = get_row_values(dif_file, 1)
        assert "Alice" in values


# --- GAP-DIF-FOSS-GET_COLUMN_V-001 ---
class TestGetColumnValues:
    def test_name_column(self, dif_file):
        values = get_column_values(dif_file, 0)
        assert "Alice" in values
        assert "Bob" in values
        assert "Carol" in values


# --- GAP-DIF-FOSS-MIN_COLUMN_V-001 ---
class TestMinColumnValue:
    def test_age_min(self, dif_file):
        result = min_column_value(dif_file, 1)
        assert float(result) == 25.0


# --- GAP-DIF-FOSS-MAX_COLUMN_V-001 ---
class TestMaxColumnValue:
    def test_age_max(self, dif_file):
        result = max_column_value(dif_file, 1)
        assert float(result) == 35.0


# --- GAP-DIF-FOSS-ADD_ROW-001 ---
class TestAddRow:
    def test_add_returns_success(self, dif_strict_doc):
        result = add_row(dif_strict_doc, ["Dan", 28, "Boston"])
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["cell_count"] == 3


# --- GAP-DIF-FOSS-DELETE_ROW-001 ---
class TestDeleteRow:
    def test_delete_returns_dict(self, dif_strict_doc):
        result = delete_row(dif_strict_doc, 0)
        assert isinstance(result, dict)


# --- GAP-DIF-FOSS-FILTER_ROWS_-001 ---
class TestFilterRowsByValue:
    def test_filter_returns_list(self, dif_doc):
        result = filter_rows_by_value(dif_doc, 2, "NYC")
        assert isinstance(result, list)


# --- GAP-DIF-FOSS-GET_ROW_AS_D-001 ---
class TestGetRowAsDict:
    def test_header_row_dict(self, dif_strict_doc):
        result = get_row_as_dict(dif_strict_doc, 0)
        assert isinstance(result, dict)
        assert "Name" in result.values() or "Name" in result.keys()


# --- GAP-DIF-FOSS-GET_HEADER_I-001 ---
class TestGetHeaderInfo:
    def test_title(self, dif_file):
        info = get_header_info(dif_file)
        assert info["title"] == "DIFTEST"
        assert info["vectors"] == 3
        assert info["tuples"] == 3
        assert info["row_count"] == 4


# --- GAP-DIF-FOSS-COUNT_DISTIN-001 ---
class TestCountDistinctValues:
    def test_city_column(self, dif_file):
        count = count_distinct_values(dif_file, 2)
        assert isinstance(count, int)
        assert count == 4  # City header + NYC, LA, SF


# --- GAP-DIF-FOSS-DIF_NUMERIC_-001 ---
class TestDifNumericRange:
    def test_range_values(self, dif_doc):
        result = dif_numeric_range(dif_doc)
        assert result["min_value"] == 25.0
        assert result["max_value"] == 35.0
        assert result["numeric_count"] == 3


# --- GAP-DIF-FOSS-DIF_VECTOR_D-001 ---
class TestDifVectorDensity:
    def test_density_calculation(self):
        doc = {
            "vectors": [
                {"tuples": [{"value": "Alice"}, {"value": 30}, {"value": "NYC"}]},
                {"tuples": [{"value": "Bob"}, {"value": 25}, {"value": "LA"}]},
            ]
        }
        result = dif_vector_density(doc)
        assert result["total_vectors"] == 2
        assert result["total_tuples"] == 6
        assert result["non_empty_tuples"] == 6
        assert result["density"] == 1.0
        assert result["avg_tuples_per_vector"] == 3.0


# --- GAP-DIF-FOSS-DIF_STRING_V-001 ---
class TestDifStringValueList:
    def test_contains_expected_strings(self, dif_doc):
        result = dif_string_value_list(dif_doc)
        assert "Alice" in result
        assert "Bob" in result
        assert "Carol" in result
        assert "NYC" in result
        assert len(result) == 9  # 3 headers + 6 data string cells


# --- GAP-DIF-FOSS-DIF_EMPTY_RO-001 ---
class TestDifEmptyRowCount:
    def test_no_empty_rows(self, dif_doc):
        count = dif_empty_row_count(dif_doc)
        assert count == 0


# --- GAP-DIF-FOSS-DIF_STRING_C-001 ---
class TestDifStringCellCount:
    def test_count_value(self, dif_doc):
        count = dif_string_cell_count(dif_doc)
        assert count == 9  # Name, Age, City, Alice, NYC, Bob, LA, Carol, SF


# --- GAP-DIF-FOSS-SET_CELL_VAL-001 ---
class TestSetCellValue:
    def test_set_and_verify(self, dif_file, tmp_path):
        dest = tmp_path / "modified.dif"
        result = set_cell_value(dif_file, dest, 1, 0, "Alicia", "string")
        assert isinstance(result, dict)
        assert dest.exists()


# --- GAP-DIF-FOSS-SUM_COLUMN-001 ---
class TestSumColumn:
    def test_age_sum(self, dif_file):
        total = sum_column(dif_file, 1)
        assert total == 90.0  # 30 + 25 + 35


# --- GAP-DIF-FOSS-SORT_ROWS_BY-001 ---
class TestSortRowsByColumn:
    def test_sort_by_age(self, dif_file):
        result = sort_rows_by_column(dif_file, 1)
        assert result is not None

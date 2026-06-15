"""Gap closure tests for ODS — covering open FOSS gaps.

Gaps cover: parse_ods, parse_ods_strict, probe_ods, get_capabilities,
    write_ods, count_sheets, get_sheet_names, get_cell_value, get_row_count,
    get_column_count, get_row_values, get_all_values, get_column_values,
    sum_column, average_column, min_column_value, max_column_value,
    get_cell_count, count_nonempty_cells, count_distinct_values,
    ods_to_csv, ods_to_html, spreadsheet_stats, set_cell_value,
    add_sheet, remove_sheet, rename_sheet, add_row, delete_row,
    ods_sheet_name_list, ods_cell_type_distribution,
    OdsError, OdsInvalidContainerError, OdsSizeError,
    OdsCell, OdsRow, OdsSheet, OdsDocument
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    OdsCell,
    OdsDocument,
    OdsError,
    OdsInvalidContainerError,
    OdsRow,
    OdsSheet,
    OdsSizeError,
    add_row,
    add_sheet,
    average_column,
    count_distinct_values,
    count_nonempty_cells,
    count_sheets,
    delete_row,
    get_all_values,
    get_capabilities,
    get_cell_count,
    get_cell_value,
    get_column_count,
    get_column_values,
    get_row_count,
    get_row_values,
    get_sheet_names,
    max_column_value,
    min_column_value,
    ods_cell_type_distribution,
    ods_sheet_name_list,
    ods_to_csv,
    ods_to_html,
    parse_ods,
    parse_ods_strict,
    probe_ods,
    remove_sheet,
    rename_sheet,
    set_cell_value,
    spreadsheet_stats,
    sum_column,
    write_ods,
)


@pytest.fixture
def ods_file(tmp_path):
    """Create a small ODS with known data."""
    doc = OdsDocument(sheets=[
        OdsSheet(name="Data", rows=[
            OdsRow(cells=[
                OdsCell(value="Name", value_type="string", text="Name"),
                OdsCell(value="Score", value_type="string", text="Score"),
            ]),
            OdsRow(cells=[
                OdsCell(value="Alice", value_type="string", text="Alice"),
                OdsCell(value=90.0, value_type="float", text="90"),
            ]),
            OdsRow(cells=[
                OdsCell(value="Bob", value_type="string", text="Bob"),
                OdsCell(value=75.0, value_type="float", text="75"),
            ]),
        ]),
    ])
    f = tmp_path / "test.ods"
    write_ods(doc, str(f))
    return f


@pytest.fixture
def ods_doc(ods_file):
    """Parsed ODS document."""
    return parse_ods_strict(str(ods_file))


@pytest.fixture
def ods_dict(ods_file):
    """Parsed ODS as dict."""
    return parse_ods(str(ods_file))


class TestErrorClasses:
    def test_ods_error_is_exception(self):
        assert issubclass(OdsError, Exception)

    def test_ods_invalid_container_subclass(self):
        assert issubclass(OdsInvalidContainerError, OdsError)

    def test_ods_size_error_subclass(self):
        assert issubclass(OdsSizeError, OdsError)

    def test_message_preserved(self):
        err = OdsError("bad ods")
        assert "bad ods" in str(err)


class TestDataClasses:
    def test_ods_cell(self):
        cell = OdsCell(value="hello", value_type="string", text="hello")
        assert cell.value == "hello"

    def test_ods_row(self):
        row = OdsRow(cells=[OdsCell()])
        assert len(row.cells) == 1

    def test_ods_sheet(self):
        sheet = OdsSheet(name="S1")
        assert sheet.name == "S1"
        assert isinstance(sheet.rows, list)

    def test_ods_document(self):
        doc = OdsDocument()
        assert isinstance(doc.sheets, list)


class TestParseOds:
    def test_returns_dict(self, ods_file):
        result = parse_ods(str(ods_file))
        assert isinstance(result, dict)


class TestParseOdsStrict:
    def test_returns_document(self, ods_file):
        doc = parse_ods_strict(str(ods_file))
        assert isinstance(doc, OdsDocument)
        assert len(doc.sheets) >= 1


class TestProbeOds:
    def test_valid_file(self, ods_file):
        result = probe_ods(str(ods_file))
        assert isinstance(result, dict)


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)


class TestWriteOds:
    def test_creates_file(self, ods_file):
        assert ods_file.exists()
        assert ods_file.stat().st_size > 0


class TestCountSheets:
    def test_count(self, ods_file):
        count = count_sheets(str(ods_file))
        assert count == 1


class TestGetSheetNames:
    def test_returns_list(self, ods_file):
        names = get_sheet_names(str(ods_file))
        assert isinstance(names, list)
        assert "Data" in names


class TestGetCellValue:
    def test_known_cell(self, ods_file):
        val = get_cell_value(str(ods_file), 0, 0, 0)
        assert val is not None


class TestGetRowCount:
    def test_count(self, ods_file):
        count = get_row_count(str(ods_file))
        assert isinstance(count, int)
        assert count >= 3


class TestGetColumnCount:
    def test_count(self, ods_file):
        count = get_column_count(str(ods_file))
        assert isinstance(count, int)
        assert count >= 2


class TestGetRowValues:
    def test_returns_list(self, ods_file):
        vals = get_row_values(str(ods_file), 0, 0)
        assert isinstance(vals, list)


class TestGetAllValues:
    def test_returns_list(self, ods_file):
        vals = get_all_values(str(ods_file))
        assert isinstance(vals, list)


class TestGetColumnValues:
    def test_returns_list(self, ods_file):
        vals = get_column_values(str(ods_file), 0)
        assert isinstance(vals, list)


class TestSumColumn:
    def test_sum(self, ods_file):
        total = sum_column(str(ods_file), 1)
        assert isinstance(total, (int, float))


class TestAverageColumn:
    def test_avg(self, ods_file):
        avg = average_column(str(ods_file), 1)
        assert isinstance(avg, (int, float))


class TestMinColumnValue:
    def test_min(self, ods_file):
        result = min_column_value(str(ods_file), 1)
        assert result is not None


class TestMaxColumnValue:
    def test_max(self, ods_file):
        result = max_column_value(str(ods_file), 1)
        assert result is not None


class TestGetCellCount:
    def test_count(self, ods_file):
        count = get_cell_count(str(ods_file))
        assert isinstance(count, int)
        assert count >= 6


class TestCountNonemptyCells:
    def test_count(self, ods_file):
        count = count_nonempty_cells(str(ods_file))
        assert isinstance(count, int)
        assert count >= 0


class TestCountDistinctValues:
    def test_count(self, ods_file):
        count = count_distinct_values(str(ods_file), 0)
        assert isinstance(count, int)


class TestOdsToCsv:
    def test_returns_string(self, ods_file):
        csv = ods_to_csv(str(ods_file))
        assert isinstance(csv, str)


class TestOdsToHtml:
    def test_returns_string(self, ods_file):
        html = ods_to_html(str(ods_file))
        assert isinstance(html, str)


class TestSpreadsheetStats:
    def test_returns_dict(self, ods_dict):
        stats = spreadsheet_stats(ods_dict)
        assert isinstance(stats, dict)


class TestSetCellValue:
    def test_set(self, ods_doc):
        result = set_cell_value(ods_doc, 0, 1, 0, "Updated")
        assert result is not None


class TestAddSheet:
    def test_add(self, ods_doc):
        ok, msg = add_sheet(ods_doc, "NewSheet")
        assert ok is True


class TestRemoveSheet:
    def test_remove(self, ods_doc):
        ok, msg = remove_sheet(ods_doc, "Data")
        assert ok is True


class TestRenameSheet:
    def test_rename(self, ods_doc):
        ok, msg = rename_sheet(ods_doc, "Data", "Renamed")
        assert ok is True


class TestAddRow:
    def test_add(self, ods_doc):
        ok, msg = add_row(ods_doc, 0, ["Carol", "85"])
        assert ok is True


class TestDeleteRow:
    def test_delete(self, ods_doc):
        ok, msg = delete_row(ods_doc, 0, 2)
        assert ok is True


class TestOdsSheetNameList:
    def test_returns_list(self, ods_dict):
        names = ods_sheet_name_list(ods_dict)
        assert isinstance(names, list)


class TestOdsCellTypeDistribution:
    def test_returns_dict(self, ods_dict):
        dist = ods_cell_type_distribution(ods_dict)
        assert isinstance(dist, dict)

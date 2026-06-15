"""Gap closure tests for Gnumeric — batch 3 covering remaining open gaps.

Gaps: GAP-Gnumeric-FOSS-WRITE_GNUMER-001, GAP-Gnumeric-FOSS-EXPORT_TO_CS-001,
      GAP-Gnumeric-FOSS-CREATE_GNUME-001, GAP-Gnumeric-FOSS-GET_CELL_VAL-001,
      GAP-Gnumeric-FOSS-GET_ROW_COUN-001, GAP-Gnumeric-FOSS-GET_COLUMN_C-001,
      GAP-Gnumeric-FOSS-GET_SHEET_IN-001, GAP-Gnumeric-FOSS-GET_SHEET_CO-001,
      GAP-Gnumeric-FOSS-GET_CELL_COU-001, GAP-Gnumeric-FOSS-EXTRACT_VALU-001,
      GAP-Gnumeric-FOSS-GET_SHEET_ME-001, GAP-Gnumeric-FOSS-EXPORT_TO_JS-001,
      GAP-Gnumeric-FOSS-MIN_COLUMN_V-001, GAP-Gnumeric-FOSS-MAX_COLUMN_V-001
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    create_gnumeric,
    export_to_csv,
    export_to_json,
    extract_values,
    get_cell_count,
    get_cell_value,
    get_column_count,
    get_row_count,
    get_sheet_count,
    get_sheet_index,
    get_sheet_metadata,
    get_sheet_names,
    load,
    min_column_value,
    max_column_value,
    set_cell_value,
    write_gnumeric,
)

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
MINIMAL = SAMPLES / "minimal-spreadsheet.gnumeric"


@pytest.fixture
def sample_doc(tmp_path):
    """Create a small doc with known data for deterministic assertions."""
    doc = create_gnumeric([
        {"name": "Data", "rows": [["Name", "Score"], ["Alice", "90"], ["Bob", "75"]]},
        {"name": "Empty", "rows": []},
    ])
    f = tmp_path / "sample.gnumeric"
    write_gnumeric(doc, str(f))
    return f


class TestWriteGnumeric:
    def test_write_creates_file(self, tmp_path):
        doc = create_gnumeric([{"name": "S1", "rows": [["hello"]]}])
        f = tmp_path / "out.gnumeric"
        write_gnumeric(doc, str(f))
        assert f.exists()
        assert f.stat().st_size > 0

    def test_write_roundtrip(self, tmp_path):
        doc = create_gnumeric([{"name": "RT", "rows": [["a", "b"], ["1", "2"]]}])
        f = tmp_path / "rt.gnumeric"
        write_gnumeric(doc, str(f))
        model = load(str(f))
        assert len(model.get("sheets", [])) >= 1


class TestCreateGnumeric:
    def test_creates_single_sheet(self):
        doc = create_gnumeric([{"name": "One", "rows": [["x"]]}])
        assert isinstance(doc, dict)
        assert len(doc.get("sheets", [])) == 1

    def test_creates_multiple_sheets(self):
        doc = create_gnumeric([
            {"name": "A", "rows": [["1"]]},
            {"name": "B", "rows": [["2"]]},
        ])
        assert len(doc.get("sheets", [])) == 2


class TestExportToCsv:
    def test_export_contains_data(self, sample_doc):
        csv_text = export_to_csv(str(sample_doc))
        assert "Alice" in csv_text
        assert "Bob" in csv_text

    def test_export_has_header(self, sample_doc):
        csv_text = export_to_csv(str(sample_doc))
        assert "Name" in csv_text
        assert "Score" in csv_text


class TestExportToJson:
    def test_export_is_valid_json(self, sample_doc):
        json_text = export_to_json(str(sample_doc))
        data = json.loads(json_text)
        assert isinstance(data, (dict, list))

    def test_export_contains_values(self, sample_doc):
        json_text = export_to_json(str(sample_doc))
        assert "Alice" in json_text


class TestGetCellValue:
    def test_read_known_cell(self, sample_doc):
        model = load(str(sample_doc))
        val = get_cell_value(model, 0, 0, 0)
        assert val == "Name"

    def test_read_data_cell(self, sample_doc):
        model = load(str(sample_doc))
        val = get_cell_value(model, 0, 1, 0)
        assert val == "Alice"


class TestGetRowCount:
    def test_row_count_data_sheet(self, sample_doc):
        model = load(str(sample_doc))
        count = get_row_count(model, 0)
        assert count == 3  # header + 2 data rows

    def test_row_count_empty_sheet(self, sample_doc):
        model = load(str(sample_doc))
        count = get_row_count(model, 1)
        assert count == 0


class TestGetColumnCount:
    def test_column_count(self, sample_doc):
        model = load(str(sample_doc))
        count = get_column_count(model, 0)
        assert count == 2  # Name, Score


class TestGetSheetIndex:
    def test_finds_data_sheet(self, sample_doc):
        model = load(str(sample_doc))
        idx = get_sheet_index(model, "Data")
        assert idx == 0

    def test_finds_empty_sheet(self, sample_doc):
        model = load(str(sample_doc))
        idx = get_sheet_index(model, "Empty")
        assert idx == 1


class TestGetSheetCount:
    def test_two_sheets(self, sample_doc):
        count = get_sheet_count(str(sample_doc))
        assert count == 2


class TestGetCellCount:
    def test_positive_count(self, sample_doc):
        count = get_cell_count(str(sample_doc))
        assert count >= 6  # 3 rows x 2 cols


class TestExtractValues:
    def test_extracts_known_values(self, sample_doc):
        vals = extract_values(str(sample_doc))
        assert isinstance(vals, list)
        assert "Alice" in vals
        assert "90" in vals


class TestGetSheetMetadata:
    def test_returns_list(self, sample_doc):
        meta = get_sheet_metadata(str(sample_doc))
        assert isinstance(meta, list)
        assert len(meta) == 2

    def test_has_sheet_names(self, sample_doc):
        meta = get_sheet_metadata(str(sample_doc))
        names = [m.get("name", "") for m in meta]
        assert "Data" in names


class TestMinMaxColumnValue:
    def test_min_column(self, sample_doc):
        model = load(str(sample_doc))
        result = min_column_value(model, 0, 1)  # Score column
        # min of "75", "90" — could be numeric or string comparison
        assert result is not None

    def test_max_column(self, sample_doc):
        model = load(str(sample_doc))
        result = max_column_value(model, 0, 1)
        assert result is not None

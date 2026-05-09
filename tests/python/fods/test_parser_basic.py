"""
test_parser_basic.py -- Basic functional tests for parse_fods().

Covers: IR-FODS-001, IR-FODS-005, IR-FODS-006, IR-FODS-007,
        IR-FODS-008 (deferred), IR-FODS-009, IR-FODS-010,
        IR-FODS-014, IR-FODS-019
"""
from pathlib import Path
import pytest
from fods import parse_fods
from fods.constants import FORMAT_ID, SPEC_VERSION

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fods"


def _sample(name):
    return str(SAMPLES / name)


# ---------------------------------------------------------------------------
# Workbook-level fields
# ---------------------------------------------------------------------------

def test_format_id():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert result.get("format_id") == FORMAT_ID


def test_spec_version():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert result.get("spec_version") == SPEC_VERSION


def test_mimetype_present():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert "mimetype" in result


def test_sheet_count_matches_sheets():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert result["sheet_count"] == len(result["sheets"])


# ---------------------------------------------------------------------------
# Multi-sheet (IR-FODS-005)
# ---------------------------------------------------------------------------

def test_multi_sheet_count():
    result = parse_fods(_sample("multi-sheet-basic.fods"))
    assert result.get("sheet_count", 0) >= 2


def test_multi_sheet_names_distinct():
    result = parse_fods(_sample("multi-sheet-basic.fods"))
    names = [s["name"] for s in result["sheets"]]
    assert len(names) == len(set(names))


def test_sheet_indices_sequential():
    result = parse_fods(_sample("multi-sheet-basic.fods"))
    for i, sheet in enumerate(result["sheets"]):
        assert sheet["index"] == i


# ---------------------------------------------------------------------------
# Row / cell extraction (IR-FODS-006)
# ---------------------------------------------------------------------------

def test_rows_list():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert isinstance(result["sheets"][0]["rows"], list)


def test_row_count_matches_rows():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    sheet = result["sheets"][0]
    assert sheet["row_count"] == len(sheet["rows"])


# ---------------------------------------------------------------------------
# Value types (IR-FODS-007)
# ---------------------------------------------------------------------------

def test_typed_values_present():
    result = parse_fods(_sample("typed-values-basic.fods"))
    assert "error" not in result
    all_cells = [
        cell
        for sheet in result["sheets"]
        for row in sheet["rows"]
        for cell in row["cells"]
    ]
    types_found = {c["value_type"] for c in all_cells if c["value_type"]}
    assert len(types_found) >= 2


# ---------------------------------------------------------------------------
# Boolean normalisation (IR-FODS-014)
# ---------------------------------------------------------------------------

def test_boolean_cells_are_python_bool():
    result = parse_fods(_sample("typed-values-basic.fods"))
    bool_cells = [
        cell
        for sheet in result["sheets"]
        for row in sheet["rows"]
        for cell in row["cells"]
        if cell.get("value_type") == "boolean"
    ]
    for cell in bool_cells:
        assert isinstance(cell["value"], bool), f"Expected bool, got {type(cell['value'])}"


# ---------------------------------------------------------------------------
# Formula capture (IR-FODS-008 deferred -- formula text captured, not evaluated)
# ---------------------------------------------------------------------------

def test_formula_field_present_in_cells():
    result = parse_fods(_sample("formula-basic.fods"))
    assert "error" not in result
    formula_cells = [
        cell
        for sheet in result["sheets"]
        for row in sheet["rows"]
        for cell in row["cells"]
        if cell.get("formula") is not None
    ]
    assert len(formula_cells) >= 1, "Expected at least one cell with formula"


def test_formula_value_is_string():
    result = parse_fods(_sample("formula-basic.fods"))
    for sheet in result["sheets"]:
        for row in sheet["rows"]:
            for cell in row["cells"]:
                if cell.get("formula") is not None:
                    assert isinstance(cell["formula"], str)


# ---------------------------------------------------------------------------
# Whitespace strip (IR-FODS-019)
# ---------------------------------------------------------------------------

def test_string_values_stripped():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    for sheet in result["sheets"]:
        for row in sheet["rows"]:
            for cell in row["cells"]:
                if cell.get("value_type") == "string" and cell["value"] is not None:
                    assert cell["value"] == cell["value"].strip()

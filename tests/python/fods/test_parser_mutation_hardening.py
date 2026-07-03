"""
test_parser_mutation_hardening.py -- Targeted tests to kill surviving mutants.

TC-MUT-001 (2026-07-03): FODS parser mutation kill rate was 50% (15/30 survived).
This file adds tests that specifically distinguish correct behavior from each of
the 15 surviving mutation patterns in src/python/fods/parser.py.

Mutants targeted:
  L102  return_none   parse_fods() unexpected-error path returns dict, not None
  L201  off_by_one    Empty sheet row_count initialises to 0, not -1
  L307  off_by_one    col_idx increments by 1 after draw:frame, not 2
  L313  negate_comparison  is_covered=True for covered cells, False for normal
  L327  off_by_one    col_repeat defaults to 1 (no attr), not 2
  L337  off_by_one    WARN_COVERED_CELL emitted when col_repeat >= 1 (not > 1)
  L349  off_by_one    col_span absent when no table:number-columns-spanned attr
  L350  off_by_one    row_span absent when no table:number-rows-spanned attr
  L378  off_by_one    col_idx increments exactly 1 per repeated cell
  L410  swap_bool     boolean "true" -> Python True (not False)
  L411  negate_comparison  boolean "false" -> Python False (not True)
  L416  return_none   date cell value is not None
  L421  negate_comparison  void cell value is None
  L429  return_none   unknown value-type falls back to text, not None
  L457  negate_comparison  text:span content is collected into cell value
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from fods import parse_fods

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fods"
SAMPLES_VALID = SAMPLES / "valid"


def _s(name):
    return str(SAMPLES / name)


def _sv(name):
    return str(SAMPLES_VALID / name)


def _load_mc():
    """Parse the mutation-coverage.fods sample (in valid/ to avoid dogfood glob)."""
    return parse_fods(_sv("mutation-coverage.fods"))


# ---------------------------------------------------------------------------
# L102 -- return_none: unexpected-error path returns dict, not None
# ---------------------------------------------------------------------------

def test_unexpected_error_returns_dict_not_none():
    """When parse_fods_strict raises a generic Exception, result must be a dict."""
    with patch("fods.parser.parse_fods_strict", side_effect=RuntimeError("synthetic")):
        result = parse_fods(_s("minimal-spreadsheet.fods"))
    assert result is not None, "parse_fods() must never return None"
    assert isinstance(result, dict), "parse_fods() must return a dict on any error"
    assert "error" in result, "Unexpected-error dict must contain 'error' key"


# ---------------------------------------------------------------------------
# L201 -- off_by_one: empty sheet initialises row_count to 0, not -1
# ---------------------------------------------------------------------------

def test_empty_sheet_row_count_is_zero():
    """EmptySheet has no rows; row_count must be 0 (not -1)."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    empty = sheets["EmptySheet"]
    assert empty["row_count"] == 0, f"Expected row_count=0, got {empty['row_count']}"
    assert empty["rows"] == []


# ---------------------------------------------------------------------------
# L307 -- off_by_one: col_idx increments by 1 after draw:frame, not 2
# ---------------------------------------------------------------------------

def test_cell_after_draw_frame_has_index_one():
    """draw:frame consumes one col slot (index=0); cell after frame is at index=1."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    # Row 2 (index=2): draw:frame at col 0, regular cell at col 1
    row2 = vt["rows"][2]
    cells = row2["cells"]
    assert len(cells) == 1, "Only the non-frame cell should be in cells list"
    assert cells[0]["index"] == 1, (
        f"Cell after draw:frame must be at index 1, got {cells[0]['index']}"
    )


# ---------------------------------------------------------------------------
# L313 -- negate_comparison: is_covered flag
# ---------------------------------------------------------------------------

def test_covered_cell_is_covered_true():
    """Covered cells must have is_covered=True."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    row1 = vt["rows"][1]  # row with main cell + covered cell
    covered = [c for c in row1["cells"] if c.get("is_covered")]
    assert len(covered) >= 1, "Expected at least one covered cell in row 1"


def test_normal_cell_is_covered_false():
    """Non-covered cells must have is_covered=False."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    row0 = vt["rows"][0]
    for cell in row0["cells"]:
        assert cell.get("is_covered") is False, (
            f"Normal cell at index {cell['index']} must have is_covered=False"
        )


# ---------------------------------------------------------------------------
# L327 -- off_by_one: col_repeat default is 1 (produces one cell, not two)
# ---------------------------------------------------------------------------

def test_no_col_repeat_attr_produces_one_cell_per_element():
    """Cells with no table:number-columns-repeated attr default to 1 — no duplication."""
    result = parse_fods(_s("minimal-spreadsheet.fods"))
    sheet = result["sheets"][0]
    # minimal-spreadsheet has exactly 1 cell in 1 row
    assert sheet["rows"][0]["cells"][0]["index"] == 0
    # Only one cell in that row
    assert len(sheet["rows"][0]["cells"]) == 1


# ---------------------------------------------------------------------------
# L337 -- off_by_one: WARN_COVERED_CELL fires for col_repeat >= 1 (default)
# ---------------------------------------------------------------------------

def test_covered_cell_with_default_repeat_emits_warning():
    """A covered cell with implicit col_repeat=1 must trigger WARN_COVERED_CELL."""
    result = _load_mc()
    warning_types = [w.get("type", w.get("code", "")) for w in result.get("warnings", [])]
    assert any("COVERED" in wt.upper() for wt in warning_types), (
        f"Expected WARN_COVERED_CELL warning, got: {warning_types}"
    )


# ---------------------------------------------------------------------------
# L349 -- off_by_one: no col_span key when no table:number-columns-spanned
# ---------------------------------------------------------------------------

def test_cell_without_col_span_attr_has_no_col_span_key():
    """Cells lacking table:number-columns-spanned must not have 'col_span' in output."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    row0 = vt["rows"][0]
    # All cells in row0 lack explicit col_span; the parser only adds it when > 1
    for cell in row0["cells"]:
        assert "col_span" not in cell, (
            f"Cell at index {cell['index']} must not have col_span (no attr in source)"
        )


# ---------------------------------------------------------------------------
# L350 -- off_by_one: no row_span key when no table:number-rows-spanned
# ---------------------------------------------------------------------------

def test_cell_without_row_span_attr_has_no_row_span_key():
    """Cells lacking table:number-rows-spanned must not have 'row_span' in output."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    row0 = vt["rows"][0]
    for cell in row0["cells"]:
        assert "row_span" not in cell, (
            f"Cell at index {cell['index']} must not have row_span (no attr in source)"
        )


# ---------------------------------------------------------------------------
# L378 -- off_by_one: col_idx increments exactly 1 per cell in the repeat loop
# ---------------------------------------------------------------------------

def test_cell_indices_are_sequential_in_multi_cell_row():
    """In a row with N cells (no col_repeat), indices must be 0, 1, 2, ..., N-1."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    row0 = vt["rows"][0]
    cells = row0["cells"]
    for expected_idx, cell in enumerate(cells):
        assert cell["index"] == expected_idx, (
            f"Cell {expected_idx}: expected index={expected_idx}, got {cell['index']}"
        )


# ---------------------------------------------------------------------------
# L410 -- swap_bool: boolean "true" -> Python True
# ---------------------------------------------------------------------------

def test_boolean_true_value_is_python_true():
    """office:boolean-value='true' must produce Python True, not False."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    bool_true_cell = vt["rows"][0]["cells"][0]  # index=0, boolean true
    assert bool_true_cell["value_type"] == "boolean"
    assert bool_true_cell["value"] is True, (
        f"'true' must map to Python True, got {bool_true_cell['value']!r}"
    )


# ---------------------------------------------------------------------------
# L411 -- negate_comparison: boolean "false" -> Python False
# ---------------------------------------------------------------------------

def test_boolean_false_value_is_python_false():
    """office:boolean-value='false' must produce Python False, not True."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    bool_false_cell = vt["rows"][0]["cells"][1]  # index=1, boolean false
    assert bool_false_cell["value_type"] == "boolean"
    assert bool_false_cell["value"] is False, (
        f"'false' must map to Python False, got {bool_false_cell['value']!r}"
    )


# ---------------------------------------------------------------------------
# L416 -- return_none: date cell returns actual date string, not None
# ---------------------------------------------------------------------------

def test_date_cell_value_is_not_none():
    """Date cell must return the office:date-value string, not None."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    date_cell = vt["rows"][0]["cells"][2]  # index=2, date
    assert date_cell["value_type"] == "date"
    assert date_cell["value"] is not None, "Date cell value must not be None"
    assert date_cell["value"] == "2026-07-03", (
        f"Date cell value must be '2026-07-03', got {date_cell['value']!r}"
    )


# ---------------------------------------------------------------------------
# L421 -- negate_comparison: void cell returns None (not text content)
# ---------------------------------------------------------------------------

def test_void_cell_value_is_none():
    """Void value type must produce None regardless of any text content."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    void_cell = vt["rows"][0]["cells"][3]  # index=3, void
    assert void_cell["value_type"] == "void"
    assert void_cell["value"] is None, (
        f"Void cell value must be None, got {void_cell['value']!r}"
    )


# ---------------------------------------------------------------------------
# L429 -- return_none: unknown value type falls back to text extraction, not None
# ---------------------------------------------------------------------------

def test_unknown_value_type_falls_back_to_text():
    """Cells with unrecognised office:value-type must return extracted text, not None."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    unknown_cell = vt["rows"][0]["cells"][5]  # index=5, custom-unknown type
    # value_type is "custom-unknown" — not None because the XML attribute is present
    assert unknown_cell["value"] is not None, (
        "Unknown value-type cell with text content must not produce None"
    )
    assert unknown_cell["value"] == "fallback-text", (
        f"Text fallback must be 'fallback-text', got {unknown_cell['value']!r}"
    )


# ---------------------------------------------------------------------------
# L457 -- negate_comparison: text:span content is collected into cell value
# ---------------------------------------------------------------------------

def test_text_span_content_is_collected():
    """Text inside text:span children must be included in the cell string value."""
    result = _load_mc()
    sheets = {s["name"]: s for s in result["sheets"]}
    vt = sheets["ValueTypes"]
    span_cell = vt["rows"][0]["cells"][4]  # index=4, string with text:span
    assert span_cell["value_type"] == "string"
    assert span_cell["value"] == "span-text", (
        f"text:span content must be collected; got {span_cell['value']!r}"
    )

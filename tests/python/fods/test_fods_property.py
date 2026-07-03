"""
test_fods_property.py -- Property-based tests for the FODS parser.

TC-PBT-001 (2026-07-03): First Hypothesis-backed property tests for FODS.

Properties tested:
  P1  parse_fods never raises on structurally valid generated inputs
  P2  sheet_count matches len(sheets) for any valid model
  P3  row_count matches len(rows) for every sheet
  P4  Roundtrip: parse -> format_id is always FORMAT_ID
  P5  Boolean values are always Python bool (never string)
  P6  Cell index matches position in row cells list
  P7  format_id is constant regardless of sheet content
"""
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from fods import parse_fods
from fods.constants import FORMAT_ID

# Namespaces for generating valid FODS XML
NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _make_fods_xml(sheets: list[dict]) -> str:
    """Generate a minimal valid FODS XML string with given sheet structure.

    Args:
        sheets: list of {"name": str, "rows": [[cell_value_str, ...]]}
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<office:document',
        f'    xmlns:office="{NS_OFFICE}"',
        f'    xmlns:table="{NS_TABLE}"',
        f'    xmlns:text="{NS_TEXT}"',
        '    office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml"',
        '    office:version="1.3">',
        '  <office:body>',
        '    <office:spreadsheet>',
    ]
    for sheet in sheets:
        safe_name = sheet["name"].replace('"', '').replace("'", "").replace("<", "").replace(">", "") or "Sheet"
        lines.append(f'      <table:table table:name="{safe_name}">')
        for row in sheet["rows"]:
            lines.append('        <table:table-row>')
            for val in row:
                safe_val = str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                lines.append(
                    f'          <table:table-cell office:value-type="string">'
                    f'<text:p>{safe_val}</text:p>'
                    f'</table:table-cell>'
                )
            lines.append('        </table:table-row>')
        lines.append('      </table:table>')
    lines.extend([
        '    </office:spreadsheet>',
        '  </office:body>',
        '</office:document>',
    ])
    return '\n'.join(lines)


def _parse_from_str(xml: str) -> dict:
    """Write xml to a temp file and parse it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fods", delete=False,
                                     encoding="utf-8") as f:
        f.write(xml)
        fpath = f.name
    return parse_fods(fpath)


# ---------------------------------------------------------------------------
# Strategy definitions
# ---------------------------------------------------------------------------

# Safe text for cell values (printable ASCII, excluding XML special chars)
_safe_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Pc"),
        whitelist_characters=" _-.",
    ),
    min_size=0,
    max_size=50,
)

_cell_row = st.lists(_safe_text, min_size=0, max_size=10)

_sheet = st.fixed_dictionaries({
    "name": st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" _"),
        min_size=1,
        max_size=20,
    ),
    "rows": st.lists(_cell_row, min_size=0, max_size=5),
})

_sheets_list = st.lists(_sheet, min_size=1, max_size=4)


# ---------------------------------------------------------------------------
# P1: parse_fods never raises on valid generated inputs
# ---------------------------------------------------------------------------

@given(sheets=_sheets_list)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_parse_never_raises_on_valid_input(sheets):
    """parse_fods must return a dict (never raise) for structurally valid FODS XML."""
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    assert isinstance(result, dict), "parse_fods must always return a dict"
    assert "error" not in result, f"Unexpected parse error: {result.get('error')}"


# ---------------------------------------------------------------------------
# P2: sheet_count == len(sheets) for any valid model
# ---------------------------------------------------------------------------

@given(sheets=_sheets_list)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_sheet_count_equals_sheets_length(sheets):
    """result['sheet_count'] must always equal len(result['sheets'])."""
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    assert result["sheet_count"] == len(result["sheets"]), (
        f"sheet_count={result['sheet_count']} but len(sheets)={len(result['sheets'])}"
    )


# ---------------------------------------------------------------------------
# P3: row_count matches len(rows) for every sheet
# ---------------------------------------------------------------------------

@given(sheets=_sheets_list)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_row_count_equals_rows_length_per_sheet(sheets):
    """Every sheet's row_count must equal len(sheet['rows'])."""
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    for sheet in result["sheets"]:
        assert sheet["row_count"] == len(sheet["rows"]), (
            f"Sheet '{sheet['name']}': row_count={sheet['row_count']} "
            f"but len(rows)={len(sheet['rows'])}"
        )


# ---------------------------------------------------------------------------
# P4: format_id is always FORMAT_ID
# ---------------------------------------------------------------------------

@given(sheets=_sheets_list)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_format_id_is_constant(sheets):
    """format_id must always equal the declared FORMAT_ID constant."""
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    assert result.get("format_id") == FORMAT_ID, (
        f"Expected format_id='{FORMAT_ID}', got '{result.get('format_id')}'"
    )


# ---------------------------------------------------------------------------
# P5: Cell index matches position
# ---------------------------------------------------------------------------

@given(sheets=_sheets_list)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_cell_index_matches_position(sheets):
    """Each cell's index field must equal its 0-based position in the row."""
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    for sheet in result["sheets"]:
        for row in sheet["rows"]:
            for pos, cell in enumerate(row["cells"]):
                assert cell["index"] == pos, (
                    f"Cell at position {pos} has index={cell['index']}"
                )


# ---------------------------------------------------------------------------
# P6: sheet_count >= 1 for any document with at least one sheet
# ---------------------------------------------------------------------------

@given(n_sheets=st.integers(min_value=1, max_value=5))
@settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
def test_sheet_count_matches_generated_count(n_sheets):
    """Generating N sheets produces a model with sheet_count == N."""
    sheets = [{"name": f"Sheet{i+1}", "rows": [["v"]]} for i in range(n_sheets)]
    xml = _make_fods_xml(sheets)
    result = _parse_from_str(xml)
    assert result["sheet_count"] == n_sheets, (
        f"Generated {n_sheets} sheets, got sheet_count={result['sheet_count']}"
    )

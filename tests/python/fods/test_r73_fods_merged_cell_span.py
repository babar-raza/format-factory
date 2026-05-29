"""
R73 Train D — test_r73_fods_merged_cell_span.py

Test FODS merged-cell span metadata preservation (R73 improvement).
New parser behavior (R73):
  - cell["col_span"] present when table:number-columns-spanned > 1
  - cell["row_span"] present when table:number-rows-spanned > 1
  - WARN_FORMULA_CELL emitted for cells with formulas
  - span attributes absent for default (span=1) cells

ODF 1.3 section 9.1.4 (table:table-cell attributes)
"""
from __future__ import annotations

import io
import pathlib
import sys
import tempfile
import textwrap
import pytest

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.parser import parse_fods
from src.python.fods.constants import WARN_FORMULA_CELL, WARN_COVERED_CELL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_fods(content: str, tmpdir: pathlib.Path) -> pathlib.Path:
    p = tmpdir / "test.fods"
    p.write_text(content, encoding="utf-8")
    return p


FODS_WITH_MERGE = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml"
                 office:version="1.3">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell office:value-type="string"
                            table:number-columns-spanned="3"
                            table:number-rows-spanned="2">
            <text:p>Merged</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="float" office:value="42">
            <text:p>42</text:p>
          </table:table-cell>
          <table:table-cell/>
          <table:table-cell/>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
""")

FODS_WITH_FORMULA = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml"
                 office:version="1.3">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
        <table:table-row>
          <table:table-cell office:value-type="float" office:value="1">
            <text:p>1</text:p>
          </table:table-cell>
          <table:table-cell office:value-type="float" office:value="2">
            <text:p>2</text:p>
          </table:table-cell>
          <table:table-cell office:value-type="float" office:value="3"
                            table:formula="of:=[.A1]+[.B1]">
            <text:p>3</text:p>
          </table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
""")


# ---------------------------------------------------------------------------
# Tests: merged cell span metadata
# ---------------------------------------------------------------------------

def test_merged_cell_col_span_captured():
    """Cell with table:number-columns-spanned=3 must have col_span=3."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_MERGE, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    sheet = wb["sheets"][0]
    merged_cell = sheet["rows"][0]["cells"][0]
    assert merged_cell.get("col_span") == 3, (
        f"Merged cell must have col_span=3. Got: {merged_cell}"
    )


def test_merged_cell_row_span_captured():
    """Cell with table:number-rows-spanned=2 must have row_span=2."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_MERGE, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    sheet = wb["sheets"][0]
    merged_cell = sheet["rows"][0]["cells"][0]
    assert merged_cell.get("row_span") == 2, (
        f"Merged cell must have row_span=2. Got: {merged_cell}"
    )


def test_non_spanning_cell_no_span_fields():
    """Cells with default span (1) must NOT have col_span or row_span keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_MERGE, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    sheet = wb["sheets"][0]
    plain_cell = sheet["rows"][2]["cells"][0]
    assert "col_span" not in plain_cell, (
        f"Non-spanning cell must not have col_span. Got: {plain_cell}"
    )
    assert "row_span" not in plain_cell, (
        f"Non-spanning cell must not have row_span. Got: {plain_cell}"
    )


def test_merged_cell_still_has_standard_fields():
    """Merged cell must still have index, value_type, value, formula, is_covered fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_MERGE, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    sheet = wb["sheets"][0]
    merged_cell = sheet["rows"][0]["cells"][0]
    for field in ("index", "value_type", "value", "formula", "is_covered"):
        assert field in merged_cell, f"Merged cell must have '{field}' field. Got: {merged_cell}"


# ---------------------------------------------------------------------------
# Tests: formula warning code
# ---------------------------------------------------------------------------

def test_formula_cell_emits_warn_formula_cell():
    """Cell with formula must emit WARN_FORMULA_CELL warning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_FORMULA, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    warning_codes = [w["code"] for w in wb["warnings"]]
    assert WARN_FORMULA_CELL in warning_codes, (
        f"Formula cell must emit {WARN_FORMULA_CELL}. Got warning codes: {warning_codes}"
    )


def test_formula_cell_unsupported_features():
    """Cell with formula must add 'formula' to unsupported_features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_FORMULA, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    assert "formula" in wb.get("unsupported_features", []), (
        f"Formula cell must add 'formula' to unsupported_features. Got: {wb.get('unsupported_features')}"
    )


def test_formula_cell_captured_in_neutral_model():
    """Formula string must still be captured in cell dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(FODS_WITH_FORMULA, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    sheet = wb["sheets"][0]
    formula_cell = sheet["rows"][0]["cells"][2]
    assert formula_cell.get("formula") is not None, (
        f"Formula must be captured in cell. Got: {formula_cell}"
    )
    assert "of:" in formula_cell["formula"], (
        f"Formula must contain 'of:' (OpenFormula prefix). Got: {formula_cell['formula']}"
    )


def test_no_formula_cell_no_formula_warning():
    """Cells without formulas must NOT emit WARN_FORMULA_CELL."""
    fods_no_formula = textwrap.dedent("""\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml"
                 office:version="1.3">
  <office:body><office:spreadsheet>
    <table:table table:name="S">
      <table:table-row>
        <table:table-cell office:value-type="string"><text:p>Hello</text:p></table:table-cell>
      </table:table-row>
    </table:table>
  </office:spreadsheet></office:body>
</office:document>
""")
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _write_fods(fods_no_formula, pathlib.Path(tmpdir))
        wb = parse_fods(p)
    assert "error" not in wb
    warning_codes = [w["code"] for w in wb["warnings"]]
    assert WARN_FORMULA_CELL not in warning_codes, (
        f"No formula cells must not emit {WARN_FORMULA_CELL}. Got: {warning_codes}"
    )

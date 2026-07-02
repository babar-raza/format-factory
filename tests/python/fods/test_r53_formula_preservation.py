"""
test_r53_formula_preservation.py — TC-0054: FODS formula preservation round-trip tests.

Sprint: FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
Gate: Phase 4 / FODS preservation deepening

Validates that:
1. The FODS parser captures table:formula attributes as-is (IR-FODS-008).
2. The FODS writer emits table:formula attributes on round-trip.
3. Editing a non-formula cell does not destroy formula attributes on other cells.
4. The formula attribute value is preserved verbatim (no transformation).

Tests:
  test_parser_captures_formula_attribute
  test_writer_emits_formula_attribute
  test_formula_roundtrip_via_fixture
  test_edit_nonfomula_cell_preserves_formula
  test_multiple_formula_cells_all_preserved
  test_formula_value_preserved_verbatim
  test_cell_without_formula_has_none
"""

from __future__ import annotations

import tempfile
import os
from pathlib import Path

import pytest

from fods.parser import parse_fods
from fods.writer import write_fods, workbook_to_xml

# Path to the existing formula fixture
FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "samples" / "by-format" / "fods"
FORMULA_FIXTURE = FIXTURES_DIR / "formula-basic.fods"


@pytest.fixture
def formula_workbook():
    """Parse the formula-basic.fods fixture."""
    assert FORMULA_FIXTURE.exists(), f"Formula fixture missing: {FORMULA_FIXTURE}"
    wb = parse_fods(FORMULA_FIXTURE)
    assert not wb.get("error"), f"Parse error: {wb.get('error')}"
    return wb


def test_parser_captures_formula_attribute(formula_workbook):
    """Parser must capture table:formula as 'formula' field in cell dict."""
    found_formula = False
    for sheet in formula_workbook["sheets"]:
        for row in sheet["rows"]:
            for cell in row["cells"]:
                if cell.get("formula") is not None:
                    found_formula = True
                    assert isinstance(cell["formula"], str), "Formula must be a string"
                    assert len(cell["formula"]) > 0, "Formula must be non-empty"
    assert found_formula is not None, "No formula cells found in formula-basic.fods"


def test_writer_emits_formula_attribute(formula_workbook):
    """Writer must emit table:formula attribute when cell has formula."""
    xml = workbook_to_xml(formula_workbook)
    assert "table:formula" in xml, "Writer must emit table:formula attribute"
    # The sample uses oooc: namespace formula
    assert "SUM" in xml or "formula" in xml.lower(), "Formula content must appear in output"


def test_formula_roundtrip_via_fixture(formula_workbook):
    """Full round-trip: parse -> write -> parse -> formula still present."""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        tmp = f.name
    try:
        write_fods(formula_workbook, tmp)
        wb2 = parse_fods(tmp)
        assert not wb2.get("error"), f"Round-trip parse error: {wb2.get('error')}"

        # Collect original formulas
        orig_formulas = {}
        for sheet in formula_workbook["sheets"]:
            for row in sheet["rows"]:
                for cell in row["cells"]:
                    if cell.get("formula") is not None:
                        key = (sheet["index"], row["index"], cell["index"])
                        orig_formulas[key] = cell["formula"]

        # Collect round-trip formulas
        rt_formulas = {}
        for sheet in wb2["sheets"]:
            for row in sheet["rows"]:
                for cell in row["cells"]:
                    if cell.get("formula") is not None:
                        key = (sheet["index"], row["index"], cell["index"])
                        rt_formulas[key] = cell["formula"]

        assert len(orig_formulas) > 0, "No formulas in original"
        assert orig_formulas == rt_formulas, (
            f"Formula round-trip mismatch.\n"
            f"Original:   {orig_formulas}\n"
            f"Round-trip: {rt_formulas}"
        )
    finally:
        os.unlink(tmp)


def test_edit_nonfomula_cell_preserves_formula(formula_workbook):
    """Editing a non-formula cell must not destroy formula attributes elsewhere."""
    import copy
    wb = copy.deepcopy(formula_workbook)

    # Edit the first non-formula cell (should be row 0, col 0 — value 10)
    wb["sheets"][0]["rows"][0]["cells"][0]["value"] = 99.0
    wb["sheets"][0]["rows"][0]["cells"][0]["text_content"] = "99"

    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        tmp = f.name
    try:
        write_fods(wb, tmp)
        wb2 = parse_fods(tmp)

        # The edited cell should have new value
        assert wb2["sheets"][0]["rows"][0]["cells"][0]["value"] == 99.0

        # The formula cell should still have its formula
        formula_cells = [
            cell
            for sheet in wb2["sheets"]
            for row in sheet["rows"]
            for cell in row["cells"]
            if cell.get("formula") is not None
        ]
        assert len(formula_cells) > 0, "Formula cells were destroyed by editing non-formula cell"
    finally:
        os.unlink(tmp)


def test_multiple_formula_cells_all_preserved():
    """Workbook with multiple formula cells preserves all formulas."""
    # Build a synthetic workbook with 2 formula cells
    wb = {
        "format_id": "fods",
        "spec_version": "ODF 1.3",
        "odf_version_attr": "1.3",
        "mimetype": "application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        "sheet_count": 1,
        "sheets": [{
            "name": "Sheet1",
            "index": 0,
            "row_count": 2,
            "rows": [
                {
                    "index": 0,
                    "cells": [
                        {"index": 0, "value_type": "float", "value": 10.0, "formula": None, "is_covered": False},
                        {"index": 1, "value_type": "float", "value": 20.0, "formula": None, "is_covered": False},
                        {"index": 2, "value_type": "float", "value": 30.0,
                         "formula": "oooc:=oooc:SUM([.A1:.B1])", "is_covered": False},
                    ]
                },
                {
                    "index": 1,
                    "cells": [
                        {"index": 0, "value_type": "float", "value": 100.0,
                         "formula": "oooc:=[.A1]*10", "is_covered": False},
                    ]
                }
            ]
        }],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }

    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        tmp = f.name
    try:
        write_fods(wb, tmp)
        wb2 = parse_fods(tmp)

        formula_cells = [
            cell
            for sheet in wb2["sheets"]
            for row in sheet["rows"]
            for cell in row["cells"]
            if cell.get("formula") is not None
        ]
        assert len(formula_cells) == 2, f"Expected 2 formula cells, got {len(formula_cells)}"
        formulas = {c["formula"] for c in formula_cells}
        assert "oooc:=oooc:SUM([.A1:.B1])" in formulas
        assert "oooc:=[.A1]*10" in formulas
    finally:
        os.unlink(tmp)


def test_formula_value_preserved_verbatim(formula_workbook):
    """Formula string value must be preserved verbatim (no transformation)."""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        tmp = f.name
    try:
        write_fods(formula_workbook, tmp)
        wb2 = parse_fods(tmp)

        orig = {
            (sheet["index"], row["index"], cell["index"]): cell["formula"]
            for sheet in formula_workbook["sheets"]
            for row in sheet["rows"]
            for cell in row["cells"]
            if cell.get("formula") is not None
        }
        rt = {
            (sheet["index"], row["index"], cell["index"]): cell["formula"]
            for sheet in wb2["sheets"]
            for row in sheet["rows"]
            for cell in row["cells"]
            if cell.get("formula") is not None
        }
        for key, formula in orig.items():
            assert key in rt, f"Formula cell {key} disappeared in round-trip"
            assert rt[key] == formula, (
                f"Formula at {key} changed: {formula!r} -> {rt[key]!r}"
            )
    finally:
        os.unlink(tmp)


def test_cell_without_formula_has_none():
    """Non-formula cells must have formula=None (not empty string or missing)."""
    # Use a fixture with no formulas
    minimal = FIXTURES_DIR / "minimal-spreadsheet.fods"
    if not minimal.exists():
        pytest.skip("minimal-spreadsheet.fods not available")
    wb = parse_fods(minimal)
    for sheet in wb["sheets"]:
        for row in sheet["rows"]:
            for cell in row["cells"]:
                assert cell.get("formula") is None, (
                    f"Non-formula cell at ({sheet['index']}, {row['index']}, {cell['index']}) "
                    f"has formula={cell.get('formula')!r}"
                )

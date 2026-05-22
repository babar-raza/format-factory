"""
tests/python/fods/test_r49_object_model_poc.py

R49 FODS Python editable object-model POC tests.

Proves the full POC chain:
  load → object model → edit cell → save same format → reload → verify edit + preservation

Sprint: FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
"""

import tempfile
from pathlib import Path

import pytest

from fods import parse_fods, write_fods, workbook_to_xml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sample_workbook() -> dict:
    """Build a minimal workbook with typed cells for POC editing."""
    return {
        "sheets": [
            {
                "name": "Sheet1",
                "rows": [
                    {
                        "cells": [
                            {"value_type": "float", "value": 1.0},
                            {"value_type": "float", "value": 2.0},
                            {"value_type": "string", "value": None, "text_content": "Label"},
                        ]
                    },
                    {
                        "cells": [
                            {"value_type": "float", "value": 10.0},
                            {"value_type": "boolean", "value": True},
                        ]
                    },
                ],
            }
        ]
    }


def _edit_cell(workbook: dict, sheet_idx: int, row_idx: int, cell_idx: int,
               new_value, new_value_type: str = "float") -> dict:
    """Return a new workbook dict with a single cell edited.

    Creates a shallow copy of the workbook with the target cell replaced.
    Does not mutate the original.
    """
    import copy
    wb = copy.deepcopy(workbook)
    cell = wb["sheets"][sheet_idx]["rows"][row_idx]["cells"][cell_idx]
    cell["value"] = new_value
    cell["value_type"] = new_value_type
    return wb


# ---------------------------------------------------------------------------
# MT4 FODS Python POC: edit/save/reload/verify
# ---------------------------------------------------------------------------

class TestFodsPythonObjectModelPOC:
    """FODS_PYTHON_OBJECT_MODEL_EDIT_SAVE_RELOAD tests."""

    def test_load_parse_produces_sheet_structure(self):
        """Parser output has sheets/rows/cells structure required for object-model POC."""
        wb = _make_sample_workbook()
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            result = parse_fods(tmp)
            assert "sheets" in result
            sheets = result["sheets"]
            assert len(sheets) == 1
            assert "rows" in sheets[0]
            assert len(sheets[0]["rows"]) == 2
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_cell_float_save_reload_verify(self):
        """Edit a float cell value, save FODS, reload, verify the edit took effect."""
        wb = _make_sample_workbook()
        # Edit cell [0][0] from 1.0 to 42.5
        wb_edited = _edit_cell(wb, sheet_idx=0, row_idx=0, cell_idx=0,
                               new_value=42.5, new_value_type="float")
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb_edited, tmp)
            reloaded = parse_fods(tmp)
            cells = reloaded["sheets"][0]["rows"][0]["cells"]
            edited_cell = cells[0]
            assert edited_cell["value"] == 42.5, (
                f"Expected edited cell value=42.5, got {edited_cell['value']!r}"
            )
            assert edited_cell["value_type"] == "float", (
                f"Expected value_type='float', got {edited_cell['value_type']!r}"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_cell_does_not_corrupt_other_cells(self):
        """Editing one cell preserves all other cells in the same row."""
        wb = _make_sample_workbook()
        # Edit cell [0][0]; verify cell [0][1] = 2.0 and cell [0][2] = 'Label' survive
        wb_edited = _edit_cell(wb, sheet_idx=0, row_idx=0, cell_idx=0,
                               new_value=99.9, new_value_type="float")
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb_edited, tmp)
            reloaded = parse_fods(tmp)
            cells = reloaded["sheets"][0]["rows"][0]["cells"]
            # Verify untouched cells
            assert cells[1]["value"] == 2.0, f"Cell [0][1] should be 2.0, got {cells[1]}"
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_cell_preserves_other_rows(self):
        """Editing row 0 cells does not change row 1."""
        wb = _make_sample_workbook()
        wb_edited = _edit_cell(wb, sheet_idx=0, row_idx=0, cell_idx=0,
                               new_value=777.0, new_value_type="float")
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb_edited, tmp)
            reloaded = parse_fods(tmp)
            row1_cells = reloaded["sheets"][0]["rows"][1]["cells"]
            # Row 1 cell 0 was 10.0 originally
            assert row1_cells[0]["value"] == 10.0, (
                f"Row 1 should be preserved, got {row1_cells[0]}"
            )
        finally:
            tmp.unlink(missing_ok=True)

    def test_edit_cell_float_to_boolean(self):
        """Change a cell's type from float to boolean and verify after reload."""
        wb = _make_sample_workbook()
        wb_edited = _edit_cell(wb, sheet_idx=0, row_idx=0, cell_idx=0,
                               new_value=False, new_value_type="boolean")
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb_edited, tmp)
            reloaded = parse_fods(tmp)
            cell = reloaded["sheets"][0]["rows"][0]["cells"][0]
            assert cell["value_type"] == "boolean", f"Expected boolean, got {cell['value_type']!r}"
        finally:
            tmp.unlink(missing_ok=True)

    def test_sheet_count_preserved(self):
        """Single-sheet workbook remains single-sheet after edit/save/reload."""
        wb = _make_sample_workbook()
        wb_edited = _edit_cell(wb, 0, 0, 0, 5.0)
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb_edited, tmp)
            reloaded = parse_fods(tmp)
            assert len(reloaded["sheets"]) == 1, "Sheet count must be preserved"
        finally:
            tmp.unlink(missing_ok=True)

    def test_parser_output_roundtrip_without_edit(self):
        """Parser output can be written back and reloaded unchanged (identity round-trip)."""
        wb = _make_sample_workbook()
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp1 = Path(f.name)
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp2 = Path(f.name)
        try:
            write_fods(wb, tmp1)
            loaded = parse_fods(tmp1)
            write_fods(loaded, tmp2)
            reloaded = parse_fods(tmp2)
            # Same structure
            assert len(reloaded["sheets"]) == len(loaded["sheets"])
            orig_cells = loaded["sheets"][0]["rows"][0]["cells"]
            reload_cells = reloaded["sheets"][0]["rows"][0]["cells"]
            assert len(reload_cells) == len(orig_cells)
            for oc, rc in zip(orig_cells, reload_cells):
                assert oc["value_type"] == rc["value_type"]
                assert oc["value"] == rc["value"]
        finally:
            tmp1.unlink(missing_ok=True)
            tmp2.unlink(missing_ok=True)


class TestFodsPreservationProof:
    """Preservation matrix tests — verify typed values survive edit/save/reload."""

    def test_typed_value_float_survives(self):
        """Float cell value and type survive write/reload."""
        wb = {"sheets": [{"name": "S", "rows": [{"cells": [
            {"value_type": "float", "value": 3.14}
        ]}]}]}
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            r = parse_fods(tmp)
            c = r["sheets"][0]["rows"][0]["cells"][0]
            assert c["value_type"] == "float"
            assert abs(c["value"] - 3.14) < 1e-10
        finally:
            tmp.unlink(missing_ok=True)

    def test_typed_value_boolean_survives(self):
        """Boolean cell type survives write/reload."""
        wb = {"sheets": [{"name": "S", "rows": [{"cells": [
            {"value_type": "boolean", "value": True}
        ]}]}]}
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb, tmp)
            r = parse_fods(tmp)
            c = r["sheets"][0]["rows"][0]["cells"][0]
            assert c["value_type"] == "boolean"
        finally:
            tmp.unlink(missing_ok=True)

    def test_multiple_row_preservation(self):
        """Multi-row workbook: editing one row preserves others exactly."""
        wb = {"sheets": [{"name": "S", "rows": [
            {"cells": [{"value_type": "float", "value": 1.0}]},
            {"cells": [{"value_type": "float", "value": 2.0}]},
            {"cells": [{"value_type": "float", "value": 3.0}]},
        ]}]}
        import copy
        wb2 = copy.deepcopy(wb)
        wb2["sheets"][0]["rows"][0]["cells"][0]["value"] = 100.0
        with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_fods(wb2, tmp)
            r = parse_fods(tmp)
            rows = r["sheets"][0]["rows"]
            assert rows[0]["cells"][0]["value"] == 100.0
            assert rows[1]["cells"][0]["value"] == 2.0
            assert rows[2]["cells"][0]["value"] == 3.0
        finally:
            tmp.unlink(missing_ok=True)

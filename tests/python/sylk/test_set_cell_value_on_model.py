"""Pilot B: test set_cell_value_on_model() — model-based SYLK edit API (PQ-021 fix).

This tests the new model-based mutation function that avoids file-based editing.
"""
import os
import tempfile

import pytest

from sylk import parse_sylk_strict, set_cell_value_on_model, write_sylk, SylkError


SAMPLES = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "samples", "by-format", "sylk", "valid"
)


def sample(name: str) -> str:
    return os.path.join(SAMPLES, name)


def test_set_cell_value_on_model_mutates_existing_cell():
    """Model-based edit changes an existing cell value without file I/O."""
    doc = parse_sylk_strict(sample("minimal-2x2.slk"))
    # Find first cell
    first = doc.cells[0]
    row, col = first.row, first.col
    result = set_cell_value_on_model(doc, row, col, "UPDATED")
    assert result["ok"] is True
    assert result["new_value"] == "UPDATED"
    updated = next(c for c in doc.cells if c.row == row and c.col == col)
    assert updated.value == "UPDATED"


def test_set_cell_value_on_model_adds_new_cell():
    """Model-based edit adds a new cell when coordinates don't exist."""
    doc = parse_sylk_strict(sample("single-cell.slk"))
    initial_count = len(doc.cells)
    set_cell_value_on_model(doc, 99, 99, "NEW_CELL")
    assert len(doc.cells) == initial_count + 1
    new_cell = next(c for c in doc.cells if c.row == 99 and c.col == 99)
    assert new_cell.value == "NEW_CELL"


def test_set_cell_value_on_model_returns_old_value():
    """Returns the previous value in old_value when overwriting."""
    doc = parse_sylk_strict(sample("single-cell.slk"))
    cell = doc.cells[0]
    old_val = cell.value
    result = set_cell_value_on_model(doc, cell.row, cell.col, "REPLACEMENT")
    assert result["old_value"] == old_val


def test_set_cell_value_on_model_invalid_row_raises():
    """Row < 1 raises SylkError."""
    doc = parse_sylk_strict(sample("single-cell.slk"))
    with pytest.raises(SylkError):
        set_cell_value_on_model(doc, 0, 1, "bad")


def test_set_cell_value_on_model_invalid_col_raises():
    """Col < 1 raises SylkError."""
    doc = parse_sylk_strict(sample("single-cell.slk"))
    with pytest.raises(SylkError):
        set_cell_value_on_model(doc, 1, 0, "bad")


def test_set_cell_value_on_model_roundtrip():
    """Full roundtrip: parse → set_cell_value_on_model → write → parse → assert."""
    doc = parse_sylk_strict(sample("single-cell.slk"))
    original_cell = doc.cells[0]
    row, col = original_cell.row, original_cell.col

    # Model-based edit
    set_cell_value_on_model(doc, row, col, "ROUNDTRIP_VALUE")

    # Write to temp file
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False) as f:
        tmppath = f.name
    try:
        write_sylk(doc, tmppath)
        # Reload and verify
        doc2 = parse_sylk_strict(tmppath)
        reloaded = next((c for c in doc2.cells if c.row == row and c.col == col), None)
        assert reloaded is not None, "Cell not found after reload"
        assert reloaded.value == "ROUNDTRIP_VALUE"
    finally:
        os.unlink(tmppath)

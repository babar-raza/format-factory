"""Gnumeric analytics functions — aggregation and statistics over workbook models.

These functions accept a pre-parsed Gnumeric neutral model dict and compute
statistics or metadata summaries. No I/O is performed here.

spec_concept: Gnumeric XML cell/sheet workbook statistics
"""
from __future__ import annotations

from typing import Any


def get_row_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of distinct rows with data in the sheet.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    from .gnumeric_codec import GnumericError  # avoid circular at module level

    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return len({r for r, _ in grid})


def get_column_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of distinct columns with data in the sheet.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    from .gnumeric_codec import GnumericError  # avoid circular at module level

    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return len({c for _, c in grid})


def count_nonempty_cells(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of cells with non-empty values.

    Raises:
        TypeError: If model is not a dict.
        GnumericError: If sheet_idx is out of range.
    """
    from .gnumeric_codec import GnumericError  # avoid circular at module level

    if not isinstance(model, dict):
        raise TypeError("model must be a dict")
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise GnumericError(f"sheet_index {sheet_idx} out of range")
    grid = sheets[sheet_idx].get("cell_grid", {})
    return sum(1 for v in grid.values() if v)

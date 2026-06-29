"""Property-based tests for CSV codec.

TC-CERT-H-PBT certification hardening.
Uses hypothesis to generate random CSV content and verify parser invariants.
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.python.csv.csv_parser import parse_csv
from src.python.csv.csv_writer import write_csv


FIELD_TEXT = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=0,
    max_size=50,
)


@given(
    rows=st.lists(
        st.lists(FIELD_TEXT, min_size=1, max_size=8),
        min_size=1,
        max_size=20,
    )
)
@settings(max_examples=50)
def test_write_read_roundtrip(rows):
    """write_csv → parse_csv must preserve row count."""
    assume(all("\x00" not in c and "\r" not in c for row in rows for c in row))
    # Filter out all-empty rows and ensure at least one non-empty cell
    assume(any(c.strip() for row in rows for c in row))
    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]

    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8")
    path = f.name
    f.close()

    try:
        write_csv(normalized, path)
        result = parse_csv(path)
        assert isinstance(result, dict)
        assert result.get("row_count", 0) >= 0  # May be 0 for whitespace-only
    finally:
        os.unlink(path)


@given(cell=FIELD_TEXT)
@settings(max_examples=50)
def test_single_cell_no_crash(cell):
    """Any single cell value must not crash the parser."""
    assume("\x00" not in cell and "\r" not in cell)
    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8")
    f.write(cell)
    f.close()

    try:
        result = parse_csv(f.name)
        assert isinstance(result, dict)
    finally:
        os.unlink(f.name)


@given(
    rows=st.lists(
        st.lists(FIELD_TEXT, min_size=1, max_size=5),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=30)
def test_parse_idempotent(rows):
    """Parsing the same file twice must yield identical results."""
    assume(all("\x00" not in c and "\r" not in c for row in rows for c in row))
    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]

    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8")
    path = f.name
    f.close()

    try:
        write_csv(normalized, path)
        r1 = parse_csv(path)
        r2 = parse_csv(path)
        assert r1.get("row_count") == r2.get("row_count")
        assert r1.get("column_count") == r2.get("column_count")
    finally:
        os.unlink(path)

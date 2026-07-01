"""Property-based tests for CSV parser and writer using Hypothesis.

TC-CERT-R2-002 certification hardening.
"""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "csv"))
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from csv_parser import parse_csv
from csv_writer import write_csv


# Strategy: generate valid CSV content as rows of strings
safe_cell = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "Z"),
        blacklist_characters="\x00",
    ),
    min_size=0,
    max_size=30,
)
rows_st = st.lists(
    st.lists(safe_cell, min_size=1, max_size=8),
    min_size=1,
    max_size=20,
)


def _make_csv_file(rows: list[list[str]]) -> Path:
    """Build a CSV file from rows, properly quoting fields."""
    import csv as stdlib_csv
    import io

    buf = io.StringIO()
    writer = stdlib_csv.writer(buf)
    for row in rows:
        writer.writerow(row)
    tmp = Path(tempfile.mktemp(suffix=".csv"))
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    return tmp


@given(rows=rows_st)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_parse_never_crashes_on_valid_csv(rows):
    """parse_csv must not crash on any well-formed CSV file."""
    tmp = _make_csv_file(rows)
    try:
        result = parse_csv(tmp)
        assert isinstance(result, dict)
    finally:
        tmp.unlink(missing_ok=True)


@given(rows=rows_st)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_roundtrip_preserves_row_count(rows):
    """write_csv -> re-parse preserves the number of data rows."""
    tmp = _make_csv_file(rows)
    try:
        model = parse_csv(tmp)
        parsed_rows = model.get("rows", [])

        # Write back
        dst = Path(tempfile.mktemp(suffix=".csv"))
        try:
            csv_text = write_csv(parsed_rows, headers=model.get("headers"))
            dst.write_text(csv_text, encoding="utf-8")
            reloaded = parse_csv(dst)
            assert len(reloaded.get("rows", [])) == len(parsed_rows)
        finally:
            dst.unlink(missing_ok=True)
    finally:
        tmp.unlink(missing_ok=True)

"""
test_csv_property.py -- Property-based tests for the CSV parser.

TC-PBT-001 (2026-07-03): First Hypothesis-backed property tests for CSV.

Properties tested:
  P1  parse_csv never raises on any well-formed list-of-lists input
  P2  Row count matches number of data rows written (within header detection margin)
  P3  column_count is within [0, max_width_of_any_row]
  P4  format_id is always 'csv'
  P5  Determinism — same input produces identical output twice
"""
import csv
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from src.python.csv.csv_parser import parse_csv  # type: ignore

# Safe cell value text (printable, no special CSV chars)
_cell_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        whitelist_characters=" _-.",
    ),
    min_size=1,  # Non-empty to avoid all-empty rows being stripped
    max_size=30,
)

_row_strategy = st.lists(_cell_text, min_size=1, max_size=8)
_rows_strategy = st.lists(_row_strategy, min_size=1, max_size=20)


def _write_csv(rows: list[list[str]], path: str) -> None:
    """Write rows to a CSV file using newline='' to avoid Windows CRLF double-encoding."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# P1: parse_csv never raises on well-formed CSV input
# ---------------------------------------------------------------------------

@given(rows=_rows_strategy)
@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
def test_parse_csv_never_raises(rows):
    """parse_csv must return a dict for any well-formed CSV input."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        fpath = f.name
    _write_csv(rows, fpath)
    result = parse_csv(fpath)
    assert isinstance(result, dict), "parse_csv must return a dict"
    assert "error" not in result, f"Unexpected parse error: {result.get('error')}"


# ---------------------------------------------------------------------------
# P2: row_count matches number of data rows in the file
# ---------------------------------------------------------------------------

@given(rows=_rows_strategy)
@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
def test_row_count_matches_input_row_count(rows):
    """row_count must be within [len(rows)-1, len(rows)] (header detection may remove one row)."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        fpath = f.name
    _write_csv(rows, fpath)
    result = parse_csv(fpath)
    total_rows = len(rows)
    assert result["row_count"] in (total_rows, total_rows - 1), (
        f"Expected row_count in ({total_rows}, {total_rows-1}), got {result['row_count']}"
    )


# ---------------------------------------------------------------------------
# P3: format_id is always 'csv'
# ---------------------------------------------------------------------------

@given(rows=_rows_strategy)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_format_id_is_always_csv(rows):
    """format='csv' must always be present in parse result."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        fpath = f.name
    _write_csv(rows, fpath)
    result = parse_csv(fpath)
    assert result.get("format") == "csv", (
        f"Expected format='csv', got '{result.get('format')}'"
    )


# ---------------------------------------------------------------------------
# P4: column_count >= 0 and <= max width of any row
# ---------------------------------------------------------------------------

@given(rows=_rows_strategy)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_column_count_within_bounds(rows):
    """column_count must be >= 0 and <= max width of any row."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        fpath = f.name
    _write_csv(rows, fpath)
    result = parse_csv(fpath)
    max_width = max(len(r) for r in rows)
    assert 0 <= result["column_count"] <= max_width, (
        f"column_count={result['column_count']} outside [0, {max_width}]"
    )


# ---------------------------------------------------------------------------
# P5: Determinism — same input produces same output twice
# ---------------------------------------------------------------------------

@given(rows=_rows_strategy)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_parsing_is_deterministic(rows):
    """Parsing the same file twice must produce identical results."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        fpath = f.name
    _write_csv(rows, fpath)
    r1 = parse_csv(fpath)
    r2 = parse_csv(fpath)
    assert r1["row_count"] == r2["row_count"]
    assert r1["column_count"] == r2["column_count"]
    assert r1["format"] == r2["format"]

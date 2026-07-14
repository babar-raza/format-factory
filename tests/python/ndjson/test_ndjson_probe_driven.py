"""Pilot A: Probe-driven test for ndjson — TC-INT-006.

This test was generated via the scaffold workflow (generate_and_write_scaffold)
and promoted by replacing all FIXTURE_REQUIRED/ORACLE_REQUIRED markers with real
values from samples/by-format/ndjson/valid/minimal.ndjson.

is_maintained_test() == True (verified during TC-INT-006 promotion).
"""
from __future__ import annotations

from pathlib import Path


_SAMPLE_PATH = (
    Path(__file__).resolve().parents[3]
    / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"
)


def test_load_ndjson_record_count():
    """Load ndjson from sample file and confirm exact record count (spec: 3 records)."""
    from ndjson import load_ndjson, ndjson_record_count
    doc = load_ndjson(str(_SAMPLE_PATH))
    count = ndjson_record_count(doc)
    assert count == 3, f"Expected 3 records, got {count}"


def test_load_ndjson_first_record_name():
    """First record has name field 'Alice' — exact value assertion."""
    from ndjson import load_ndjson
    doc = load_ndjson(str(_SAMPLE_PATH))
    assert doc[0]["name"] == "Alice", f"Expected 'Alice', got {doc[0].get('name')!r}"


def test_load_ndjson_boundary_empty_bytes():
    """Empty bytes input returns empty list (boundary case)."""
    from ndjson import load_ndjson
    doc = load_ndjson(b"")
    assert doc == [], f"Expected empty list for empty input, got {doc!r}"


def test_probe_ndjson_valid_returns_true():
    """probe_ndjson on valid NDJSON bytes returns True."""
    from ndjson import probe_ndjson
    data = b'{"id": 1}\n{"id": 2}\n'
    result = probe_ndjson(data)
    assert result is True, f"Expected True, got {result!r}"


def test_probe_ndjson_invalid_returns_false():
    """probe_ndjson on truncated/invalid JSON returns False (negative control)."""
    from ndjson import probe_ndjson
    result = probe_ndjson(b'{"broken":')
    assert result is False, f"Expected False for invalid JSON, got {result!r}"

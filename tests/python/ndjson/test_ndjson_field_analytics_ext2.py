"""Tests for ndjson_field_analytics.py's remaining (non-duplicate) functions.

TC-FI025-001 (2026-07-17): this file used to also test ndjson_record_count,
ndjson_dict_record_count, ndjson_unique_key_count, ndjson_min_field_count, and
ndjson_total_field_count -- all 5 deleted from ndjson_field_analytics.py as
part of closing FI-025 (they were permanently-dead, unreachable duplicates of
the canonical, already-tested implementations in json_stream.py /
ndjson_record_stats.py; see registry/found-issue-register.yaml FI-025 and
src/python/ndjson/__init__.py's import comment). Their canonical counterparts
already have equivalent edge-case coverage in test_ndjson_record_stats_ext.py
and test_r305_ndjson_new_analytics.py -- no coverage was lost by this removal.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_field_analytics import (
    ndjson_has_arrays,
)

VALID = _REPO / "samples" / "by-format" / "ndjson" / "valid"
MINIMAL = VALID / "minimal.ndjson"

# minimal.ndjson has 3 records, each dict with keys: name, score, active


# --- ndjson_has_arrays ---

def test_has_arrays_minimal():
    # minimal.ndjson has no list values
    assert ndjson_has_arrays(MINIMAL) is False

def test_has_arrays_with_list():
    data = b'{"tags": ["a", "b"]}\n'
    assert ndjson_has_arrays(data) is True

def test_has_arrays_without_list():
    data = b'{"name": "Alice", "score": 99}\n'
    assert ndjson_has_arrays(data) is False

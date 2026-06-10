"""Tests for NDJSON head export — mainstream-product-deepening-rnext8.

Covers: first N records, default n=10, empty source, negative n raises.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import head


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ndjson_bytes(*records) -> bytes:
    import json
    return b"\n".join(json.dumps(r).encode() for r in records) + b"\n"


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_head_basic():
    src = _ndjson_bytes({"id": 1}, {"id": 2}, {"id": 3}, {"id": 4})
    result = head(src, 2)
    assert result == [{"id": 1}, {"id": 2}]


def test_head_all():
    src = _ndjson_bytes({"x": "a"}, {"x": "b"})
    result = head(src, 5)
    assert result == [{"x": "a"}, {"x": "b"}]


def test_head_default_n():
    src = _ndjson_bytes(*[{"i": i} for i in range(15)])
    result = head(src)
    assert len(result) == 10


def test_head_zero_returns_empty():
    src = _ndjson_bytes({"id": 1})
    assert head(src, 0) == []


def test_head_empty_source():
    assert head(b"") == []


def test_head_returns_list():
    src = _ndjson_bytes({"k": "v"})
    assert isinstance(head(src, 1), list)


def test_head_negative_raises():
    src = _ndjson_bytes({"k": 1})
    with pytest.raises(ValueError):
        head(src, -1)

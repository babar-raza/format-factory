"""
test_zst_roundtrip_ratio_w118_pipeline.py -- ZST validate_roundtrip + estimate_ratio pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-118
Tests validate_roundtrip returns dict, valid=True, match=True,
estimate_ratio returns dict, ratio < 1.0 (data is compressed smaller).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    validate_roundtrip,
    estimate_ratio,
)

_DATA = b"Hello World! This is repetitive data for compression testing. " * 100


def test_validate_roundtrip_returns_dict():
    result = validate_roundtrip(_DATA)
    assert isinstance(result, dict)


def test_validate_roundtrip_valid():
    result = validate_roundtrip(_DATA)
    assert result["valid"] is True


def test_validate_roundtrip_match():
    result = validate_roundtrip(_DATA)
    assert result["match"] is True


def test_estimate_ratio_returns_dict():
    result = estimate_ratio(_DATA)
    assert isinstance(result, dict)


def test_estimate_ratio_compresses_data():
    result = estimate_ratio(_DATA)
    assert result["ratio"] < 1.0

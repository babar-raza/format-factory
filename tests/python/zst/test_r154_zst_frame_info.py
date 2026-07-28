"""
test_r154_zst_frame_info.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT12-001
Added: 2026-06-09

Tests for ZST get_frame_info and estimate_ratio functions.
Authority: P6 (SAL-ZST-00001: Zstandard magic 0xFD2FB528, RFC 8878 §3.1.1)
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.zst.zst_codec import (
    get_frame_info,
    estimate_ratio,
    compress_bytes,
)


class TestGetFrameInfo:
    """get_frame_info: return metadata about a Zstandard compressed frame."""

    def test_valid_frame_returns_valid_true(self):
        data = compress_bytes(b"Hello Zstandard frame info!" * 10)
        info = get_frame_info(data)
        assert info["valid"] is True
        assert info["magic_ok"] is True

    def test_valid_frame_has_content_size(self):
        original = b"Test content size" * 20
        data = compress_bytes(original)
        info = get_frame_info(data)
        assert info["content_size"] == len(original)

    def test_valid_frame_has_compressed_size(self):
        data = compress_bytes(b"compressed size check" * 10)
        info = get_frame_info(data)
        assert info["compressed_size"] == len(data)

    def test_valid_frame_has_compression_ratio(self):
        original = b"ratio test data " * 50
        data = compress_bytes(original)
        info = get_frame_info(data)
        assert info["compression_ratio"] is not None
        assert 0.0 < info["compression_ratio"] < 1.0

    def test_invalid_magic_returns_error(self):
        info = get_frame_info(b"\xFF\xFF\xFF\xFF bad data")
        assert info["valid"] is False
        assert info["magic_ok"] is False
        assert info["error"] is not None

    def test_too_short_data_returns_error(self):
        info = get_frame_info(b"\x28\xb5")
        assert info["valid"] is False
        assert "short" in info["error"].lower() or "Too short" in info["error"]

    def test_non_bytes_returns_error(self):
        info = get_frame_info("not bytes")
        assert info["valid"] is False
        assert "bytes" in info["error"].lower() or "Expected" in info["error"]


class TestEstimateRatio:
    """estimate_ratio: estimate compression ratio for raw data."""

    def test_returns_ratio_less_than_one_for_compressible_data(self):
        data = b"AAAA" * 1000
        result = estimate_ratio(data)
        assert result["ratio"] is not None
        assert result["ratio"] < 1.0

    def test_returns_correct_input_bytes(self):
        data = b"input size test" * 10
        result = estimate_ratio(data)
        assert result["input_bytes"] == len(data)

    def test_returns_compressed_bytes(self):
        data = b"compressed bytes field" * 20
        result = estimate_ratio(data)
        assert result["compressed_bytes"] is not None
        assert result["compressed_bytes"] > 0

    def test_savings_pct_positive_for_compressible(self):
        data = b"savings percent test " * 100
        result = estimate_ratio(data)
        assert result["savings_pct"] is not None
        assert result["savings_pct"] > 0

    def test_custom_level(self):
        data = b"level test " * 100
        r1 = estimate_ratio(data, level=1)
        r9 = estimate_ratio(data, level=9)
        assert r1["error"] is None
        assert r9["error"] is None
        assert r1["level"] == 1
        assert r9["level"] == 9

    def test_empty_data(self):
        result = estimate_ratio(b"")
        assert result["input_bytes"] == 0
        assert result["ratio"] == 0.0
        assert result["error"] is None

    def test_non_bytes_returns_error(self):
        result = estimate_ratio("not bytes")
        assert result["error"] is not None

"""
test_r165_zst_frame_ratio.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT29-001
Added: 2026-06-10

Tests for ZST get_frame_info and estimate_ratio functions.
Authority: P6 (FACT-ZST-001: magic 0xFD2FB528)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    get_frame_info,
    estimate_ratio,
    compress_bytes,
)


# ── get_frame_info ───────────────────────────────────────────────────────

class TestGetFrameInfo:

    def test_valid_compressed_data(self):
        original = b"Hello World" * 100
        compressed = compress_bytes(original)
        result = get_frame_info(compressed)
        assert result["valid"] is True
        assert result["magic_ok"] is True
        assert result["content_size"] == len(original)
        assert result["error"] is None

    def test_compression_ratio_calculated(self):
        original = b"AAAA" * 1000
        compressed = compress_bytes(original)
        result = get_frame_info(compressed)
        assert result["compression_ratio"] is not None
        assert result["compression_ratio"] < 1.0

    def test_compressed_size_set(self):
        compressed = compress_bytes(b"test data")
        result = get_frame_info(compressed)
        assert result["compressed_size"] == len(compressed)

    def test_invalid_magic(self):
        result = get_frame_info(b"\x00\x00\x00\x00some data")
        assert result["valid"] is False
        assert result["magic_ok"] is False
        assert result["error"] is not None

    def test_too_short(self):
        result = get_frame_info(b"\xFD")
        assert result["valid"] is False
        assert "short" in result["error"].lower() or "Too short" in result["error"]

    def test_not_bytes(self):
        result = get_frame_info("not bytes")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_empty_original(self):
        compressed = compress_bytes(b"")
        result = get_frame_info(compressed)
        assert result["valid"] is True
        assert result["magic_ok"] is True


# ── estimate_ratio ───────────────────────────────────────────────────────

class TestEstimateRatio:

    def test_compressible_data(self):
        data = b"A" * 10000
        result = estimate_ratio(data)
        assert result["input_bytes"] == 10000
        assert result["compressed_bytes"] is not None
        assert result["compressed_bytes"] < 10000
        assert result["ratio"] < 1.0
        assert result["savings_pct"] > 0.0
        assert result["error"] is None

    def test_empty_data(self):
        result = estimate_ratio(b"")
        assert result["input_bytes"] == 0
        assert result["compressed_bytes"] == 0
        assert result["ratio"] == 0.0
        assert result["savings_pct"] == 0.0

    def test_not_bytes(self):
        result = estimate_ratio("string data")
        assert result["error"] is not None

    def test_custom_level(self):
        data = b"test " * 500
        result = estimate_ratio(data, level=1)
        assert result["level"] == 1
        assert result["compressed_bytes"] is not None

    def test_high_level(self):
        data = b"test " * 500
        result = estimate_ratio(data, level=19)
        assert result["level"] == 19
        assert result["compressed_bytes"] is not None

    def test_small_data(self):
        result = estimate_ratio(b"tiny")
        assert result["input_bytes"] == 4
        assert result["compressed_bytes"] is not None

    def test_savings_pct_range(self):
        data = b"AAAA" * 1000
        result = estimate_ratio(data)
        assert 0.0 <= result["savings_pct"] <= 100.0

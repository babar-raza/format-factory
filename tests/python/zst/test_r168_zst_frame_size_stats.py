"""
test_r168_zst_frame_size_stats.py

Lane G — Product Advancement:
Tests for get_frame_size_stats() added in RNEXT sprint.

Sprint: FORMAT-FACTORY-SAL-ENFORCEMENT-CLOSEOUT-AND-PRODUCT-ACCELERATION-RNEXT-001
spec_fact_refs: SAL-ZST-00001
route_decision_id: RDEC-RNEXT-LG-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "src" / "python"))

from zst.zst_codec import compress_bytes, get_frame_size_stats, ZstError
from zst import get_frame_size_stats as pkg_get_frame_size_stats


class TestGetFrameSizeStats:
    def test_valid_frame_has_all_fields(self):
        data = compress_bytes(b"Hello frame size stats!")
        result = get_frame_size_stats(data)
        assert result["valid"] is True
        assert isinstance(result["compressed_bytes"], int)
        assert isinstance(result["decompressed_bytes"], int)
        assert isinstance(result["space_saved_bytes"], int)
        assert isinstance(result["space_saved_pct"], float)
        assert result["error"] is None

    def test_compressed_bytes_matches_input_length(self):
        original = b"Test content for frame stats."
        data = compress_bytes(original)
        result = get_frame_size_stats(data)
        assert result["compressed_bytes"] == len(data)

    def test_decompressed_bytes_matches_original(self):
        original = b"Decompressed size verification."
        data = compress_bytes(original)
        result = get_frame_size_stats(data)
        assert result["decompressed_bytes"] == len(original)

    def test_space_saved_bytes_calculation(self):
        # Use highly compressible data
        original = b"A" * 1000
        data = compress_bytes(original)
        result = get_frame_size_stats(data)
        assert result["space_saved_bytes"] == len(original) - len(data)
        assert result["space_saved_bytes"] > 0

    def test_space_saved_pct_range(self):
        original = b"Z" * 500
        data = compress_bytes(original)
        result = get_frame_size_stats(data)
        assert 0.0 <= result["space_saved_pct"] <= 100.0

    def test_compression_ratio_present(self):
        data = compress_bytes(b"ratio test" * 50)
        result = get_frame_size_stats(data)
        assert result["compression_ratio"] is not None
        assert result["compression_ratio"] > 0

    def test_invalid_frame(self):
        result = get_frame_size_stats(b"not a zstandard frame!!!!!!!!")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_non_bytes_raises(self):
        with pytest.raises(ZstError):
            get_frame_size_stats("not bytes")

    def test_empty_frame_decompressed_zero(self):
        data = compress_bytes(b"")
        result = get_frame_size_stats(data)
        assert result["valid"] is True
        assert result["decompressed_bytes"] == 0
        assert result["space_saved_pct"] is None  # 0 input, no savings %

    def test_package_level_import(self):
        data = compress_bytes(b"package import test")
        result = pkg_get_frame_size_stats(data)
        assert result["valid"] is True
        assert "compressed_bytes" in result

    def test_get_frame_size_stats_in_all(self):
        import zst
        assert "get_frame_size_stats" in zst.__all__

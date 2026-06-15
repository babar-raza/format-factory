"""Gap closure tests for ZST — batch 2, covering remaining 6 open gaps.

Gaps: GAP-ZST-FOSS-ZSTINVALIDFR-001, GAP-ZST-FOSS-ZSTOUTPUTLIM-001,
      GAP-ZST-FOSS-ESTIMATE_RAT-001, GAP-ZST-FOSS-GET_FRAME_SI-001,
      GAP-ZST-FOSS-COMPRESS_WIT-001, GAP-ZST-FOSS-DECOMPRESS_W-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    ZstInvalidFrameError,
    ZstOutputLimitExceeded,
    ZstError,
    compress_bytes,
    compress_string,
    compress_with_dict,
    decompress_with_dict,
    estimate_ratio,
    get_frame_size_stats,
)


@pytest.fixture
def zst_data():
    """Compressed bytes from known input."""
    original = b"Hello world! " * 100
    return compress_bytes(original), original


# --- GAP-ZST-FOSS-ZSTINVALIDFR-001 ---
class TestZstInvalidFrameError:
    def test_is_subclass(self):
        assert issubclass(ZstInvalidFrameError, ZstError)

    def test_can_raise(self):
        with pytest.raises(ZstInvalidFrameError):
            raise ZstInvalidFrameError("bad frame")

    def test_message(self):
        err = ZstInvalidFrameError("invalid frame header")
        assert "invalid frame header" in str(err)


# --- GAP-ZST-FOSS-ZSTOUTPUTLIM-001 ---
class TestZstOutputLimitExceeded:
    def test_is_subclass(self):
        assert issubclass(ZstOutputLimitExceeded, ZstError)

    def test_can_raise(self):
        with pytest.raises(ZstOutputLimitExceeded):
            raise ZstOutputLimitExceeded("output too large")

    def test_message(self):
        err = ZstOutputLimitExceeded("limit exceeded")
        assert "limit exceeded" in str(err)


# --- GAP-ZST-FOSS-ESTIMATE_RAT-001 ---
class TestEstimateRatio:
    def test_returns_dict(self, zst_data):
        _, original = zst_data
        result = estimate_ratio(original)
        assert isinstance(result, dict)
        assert result["error"] is None
        assert result["input_bytes"] == len(original)

    def test_compression_ratio(self, zst_data):
        _, original = zst_data
        result = estimate_ratio(original)
        assert result["compressed_bytes"] < result["input_bytes"]
        assert result["savings_pct"] > 90.0  # repeated text compresses well


# --- GAP-ZST-FOSS-GET_FRAME_SI-001 ---
class TestGetFrameSizeStats:
    def test_returns_dict(self, zst_data):
        compressed, _ = zst_data
        stats = get_frame_size_stats(compressed)
        assert isinstance(stats, dict)
        assert stats["valid"] is True

    def test_has_size_info(self, zst_data):
        compressed, original = zst_data
        stats = get_frame_size_stats(compressed)
        assert stats["compressed_bytes"] == len(compressed)
        assert stats["decompressed_bytes"] == len(original)


# --- GAP-ZST-FOSS-COMPRESS_WIT-001 ---
class TestCompressWithDict:
    def test_returns_bytes(self):
        data = b"test data for dict compression"
        dictionary = b"test data" * 10
        result = compress_with_dict(data, dictionary)
        assert isinstance(result, bytes)
        assert len(result) > 0


# --- GAP-ZST-FOSS-DECOMPRESS_W-001 ---
class TestDecompressWithDict:
    def test_roundtrip(self):
        data = b"dictionary-based roundtrip test data"
        dictionary = b"dictionary-based" * 10
        compressed = compress_with_dict(data, dictionary)
        result = decompress_with_dict(compressed, dictionary)
        assert result == data

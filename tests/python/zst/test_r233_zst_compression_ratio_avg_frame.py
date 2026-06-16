"""Tests for zst_compression_ratio and zst_avg_frame_size (Sprint 23)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

zstandard = pytest.importorskip("zstandard", reason="python-zstandard not installed")

from zst import compress_bytes, zst_compression_ratio, zst_avg_frame_size


def _make_zst(tmp_path, name, data: bytes) -> str:
    compressed = compress_bytes(data)
    p = tmp_path / f"{name}.zst"
    p.write_bytes(compressed)
    return str(p)


class TestZstCompressionRatio:
    def test_return_type(self, tmp_path):
        p = _make_zst(tmp_path, "rt", b"hello world " * 100)
        result = zst_compression_ratio(p)
        assert isinstance(result, float)

    def test_positive_ratio(self, tmp_path):
        p = _make_zst(tmp_path, "pos", b"aaaa" * 500)
        result = zst_compression_ratio(p)
        assert result >= 0.0

    def test_ratio_less_than_one_for_compressible(self, tmp_path):
        p = _make_zst(tmp_path, "lt1", b"a" * 10000)
        result = zst_compression_ratio(p)
        assert result < 1.0

    def test_nonzero_for_real_file(self, tmp_path):
        p = _make_zst(tmp_path, "nz", b"test data " * 200)
        result = zst_compression_ratio(p)
        assert result > 0.0

    def test_float_precision(self, tmp_path):
        p = _make_zst(tmp_path, "fp", b"x" * 5000)
        result = zst_compression_ratio(p)
        assert isinstance(result, float)
        assert result >= 0.0


class TestZstAvgFrameSize:
    def test_return_type(self, tmp_path):
        p = _make_zst(tmp_path, "rt2", b"hello world")
        result = zst_avg_frame_size(p)
        assert isinstance(result, float)

    def test_positive_for_valid_file(self, tmp_path):
        p = _make_zst(tmp_path, "pos2", b"some content " * 50)
        result = zst_avg_frame_size(p)
        assert result > 0.0

    def test_nonnegative(self, tmp_path):
        p = _make_zst(tmp_path, "nn", b"data " * 100)
        result = zst_avg_frame_size(p)
        assert result >= 0.0

    def test_single_frame(self, tmp_path):
        p = _make_zst(tmp_path, "sf", b"single frame data")
        result = zst_avg_frame_size(p)
        assert isinstance(result, float)
        assert result > 0.0

    def test_larger_data_has_positive_avg(self, tmp_path):
        p = _make_zst(tmp_path, "big", b"large content " * 1000)
        result = zst_avg_frame_size(p)
        assert result > 0.0

"""Tests for ZstDocument computed properties: has_multiple_frames, is_empty,
compressed_size_kb, compression_ratio.

Sprint: FORMAT-FACTORY-ZST-PYTHON-PROPS-20260625
Ledger: R118-GOVERNED-PYTHON-ZST-DOCUMENT-PROPS-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.models import ZstDocument


def _doc(compressed_size: int = 0, decompressed_size: int = 0, frame_count: int = 0) -> ZstDocument:
    return ZstDocument("/tmp/test.zst", {
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "frame_count": frame_count,
    })


class TestHasMultipleFrames:
    def test_one_frame_returns_false(self):
        assert not _doc(frame_count=1).has_multiple_frames

    def test_two_frames_returns_true(self):
        assert _doc(frame_count=2).has_multiple_frames

    def test_zero_frames_returns_false(self):
        assert not _doc(frame_count=0).has_multiple_frames

    def test_many_frames_returns_true(self):
        assert _doc(frame_count=10).has_multiple_frames


class TestIsEmpty:
    def test_zero_frames_returns_true(self):
        assert _doc(frame_count=0).is_empty

    def test_one_frame_returns_false(self):
        assert not _doc(frame_count=1).is_empty

    def test_default_construction_is_empty(self):
        assert ZstDocument("/tmp/test.zst").is_empty


class TestCompressedSizeKb:
    def test_exactly_one_kb(self):
        assert _doc(compressed_size=1024).compressed_size_kb == pytest.approx(1.0)

    def test_zero_bytes_is_zero(self):
        assert _doc(compressed_size=0).compressed_size_kb == pytest.approx(0.0)

    def test_512_bytes_is_half_kb(self):
        assert _doc(compressed_size=512).compressed_size_kb == pytest.approx(0.5)

    def test_two_kb(self):
        assert _doc(compressed_size=2048).compressed_size_kb == pytest.approx(2.0)


class TestCompressionRatio:
    def test_no_compression_data_returns_zero(self):
        assert _doc(compressed_size=0, decompressed_size=0).compression_ratio == pytest.approx(0.0)

    def test_compressed_size_zero_returns_zero(self):
        assert _doc(compressed_size=0, decompressed_size=100).compression_ratio == pytest.approx(0.0)

    def test_two_to_one_ratio(self):
        assert _doc(compressed_size=50, decompressed_size=100).compression_ratio == pytest.approx(2.0)

    def test_ratio_less_than_one_for_incompressible(self):
        # compressed is larger than decompressed — ratio < 1
        ratio = _doc(compressed_size=110, decompressed_size=100).compression_ratio
        assert ratio < 1.0

    def test_ratio_one_for_no_compression(self):
        assert _doc(compressed_size=100, decompressed_size=100).compression_ratio == pytest.approx(1.0)

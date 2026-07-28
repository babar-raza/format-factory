"""Tests for R1272: ZstDocument compression quality analysis properties.

Properties under test:
    space_saved_bytes     — decompressed_size - compressed_size (0 if compressed is larger)
    is_highly_compressible — savings_ratio > 0.9
    frames_per_mb         — frame_count / decompressed_size_mb (0.0 if no decompressed data)

spec_fact_ref: SAL-ZST-00001
"""

import pytest
from zst.models import ZstDocument
from pathlib import Path


def _make_doc(compressed: int, decompressed: int, frames: int = 1) -> ZstDocument:
    """Build a ZstDocument stub."""
    doc = ZstDocument.__new__(ZstDocument)
    doc._path = Path("test.zst")
    doc._data = {
        "compressed_size": compressed,
        "decompressed_size": decompressed,
        "frame_count": frames,
    }
    return doc


# ── space_saved_bytes ─────────────────────────────────────────────────────────

class TestSpaceSavedBytes:
    def test_normal_compression(self):
        doc = _make_doc(100, 1000)
        assert doc.space_saved_bytes == 900

    def test_no_compression_returns_zero(self):
        doc = _make_doc(1000, 1000)
        assert doc.space_saved_bytes == 0

    def test_compressed_larger_returns_zero(self):
        # compressed > decompressed (expansion)
        doc = _make_doc(1100, 1000)
        assert doc.space_saved_bytes == 0

    def test_zero_decompressed(self):
        doc = _make_doc(0, 0)
        assert doc.space_saved_bytes == 0

    def test_high_savings(self):
        doc = _make_doc(100, 10000)
        assert doc.space_saved_bytes == 9900


# ── is_highly_compressible ────────────────────────────────────────────────────

class TestIsHighlyCompressible:
    def test_91_pct_savings_is_high(self):
        # savings = 1 - 90/1000 = 0.91
        doc = _make_doc(90, 1000)
        assert doc.is_highly_compressible is True

    def test_exactly_90_pct_not_high(self):
        # savings = 1 - 100/1000 = 0.9 (not > 0.9)
        doc = _make_doc(100, 1000)
        assert doc.is_highly_compressible is False

    def test_no_compression_not_high(self):
        doc = _make_doc(1000, 1000)
        assert doc.is_highly_compressible is False

    def test_99_pct_savings(self):
        doc = _make_doc(10, 1000)
        assert doc.is_highly_compressible is True

    def test_zero_decompressed_not_high(self):
        doc = _make_doc(0, 0)
        assert doc.is_highly_compressible is False


# ── frames_per_mb ─────────────────────────────────────────────────────────────

class TestFramesPerMb:
    def test_zero_decompressed_returns_zero(self):
        doc = _make_doc(0, 0, frames=0)
        assert doc.frames_per_mb == pytest.approx(0.0)

    def test_one_frame_per_mb(self):
        # 1 frame, exactly 1 binary MB (1048576 bytes) decompressed
        doc = _make_doc(500_000, 1_048_576, frames=1)
        assert doc.frames_per_mb == pytest.approx(1.0)

    def test_two_frames_per_mb(self):
        # 2 frames, exactly 1 binary MB decompressed
        doc = _make_doc(500_000, 1_048_576, frames=2)
        assert doc.frames_per_mb == pytest.approx(2.0)

    def test_many_frames_small_file(self):
        # 10 frames, 0.5 binary MB (524288 bytes) → 20 frames/MB
        doc = _make_doc(100_000, 524_288, frames=10)
        assert doc.frames_per_mb == pytest.approx(20.0)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_high_compressible_implies_lossless_verified(self):
        # 91% savings → compressed < decompressed
        doc = _make_doc(90, 1000)
        assert doc.is_highly_compressible is True
        assert doc.is_lossless_verified is True

    def test_space_saved_consistent_with_sizes(self):
        doc = _make_doc(200, 800)
        assert doc.space_saved_bytes == doc.decompressed_size - doc.compressed_size

    def test_no_savings_no_high_compressibility(self):
        doc = _make_doc(1000, 1000)
        assert doc.space_saved_bytes == 0
        assert doc.is_highly_compressible is False

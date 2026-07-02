"""Tests for R1288: ZstDocument frame structure and compression classification properties.

Properties under test:
    is_multi_frame     — frame_count > 1
    compression_class  — 'none', 'low', 'moderate', 'high', or 'very_high'
    avg_frame_size_kb  — (compressed_size / frame_count) / 1024 (0.0 if no frames)

spec_fact_ref: FACT-ZST-001
"""

import pytest
from zst.models import ZstDocument
from pathlib import Path


def _make_doc(compressed: int, decompressed: int, frames: int = 1) -> ZstDocument:
    doc = ZstDocument.__new__(ZstDocument)
    doc._path = Path("test.zst")
    doc._data = {
        "compressed_size": compressed,
        "decompressed_size": decompressed,
        "frame_count": frames,
    }
    return doc


# ── is_multi_frame ────────────────────────────────────────────────────────────

class TestIsMultiFrame:
    def test_zero_frames_not_multi(self):
        doc = _make_doc(0, 0, frames=0)
        assert doc.is_multi_frame is False

    def test_single_frame_not_multi(self):
        doc = _make_doc(100, 1000, frames=1)
        assert doc.is_multi_frame is False

    def test_two_frames_is_multi(self):
        doc = _make_doc(200, 2000, frames=2)
        assert doc.is_multi_frame is True

    def test_many_frames_is_multi(self):
        doc = _make_doc(500, 5000, frames=10)
        assert doc.is_multi_frame is True


# ── compression_class ─────────────────────────────────────────────────────────

class TestCompressionClass:
    def test_no_compression_none(self):
        # compressed == decompressed → savings_ratio = 0.0
        doc = _make_doc(1000, 1000)
        assert doc.compression_class == "none"

    def test_expansion_is_none(self):
        # compressed > decompressed → negative ratio
        doc = _make_doc(1100, 1000)
        assert doc.compression_class == "none"

    def test_zero_savings_is_none(self):
        doc = _make_doc(0, 0)
        assert doc.compression_class == "none"

    def test_25_pct_savings_is_low(self):
        # savings_ratio = 0.25 → low
        doc = _make_doc(750, 1000)
        assert doc.compression_class == "low"

    def test_50_pct_boundary_is_low(self):
        # savings_ratio = 0.5, <= 0.5 → low
        doc = _make_doc(500, 1000)
        assert doc.compression_class == "low"

    def test_60_pct_savings_is_moderate(self):
        # savings_ratio = 0.6 → moderate
        doc = _make_doc(400, 1000)
        assert doc.compression_class == "moderate"

    def test_80_pct_boundary_is_moderate(self):
        # savings_ratio = 0.8, <= 0.8 → moderate
        doc = _make_doc(200, 1000)
        assert doc.compression_class == "moderate"

    def test_85_pct_savings_is_high(self):
        # savings_ratio = 0.85 → high
        doc = _make_doc(150, 1000)
        assert doc.compression_class == "high"

    def test_90_pct_boundary_is_high(self):
        # savings_ratio = 0.9, <= 0.9 → high
        doc = _make_doc(100, 1000)
        assert doc.compression_class == "high"

    def test_95_pct_savings_is_very_high(self):
        # savings_ratio = 0.95 > 0.9 → very_high
        doc = _make_doc(50, 1000)
        assert doc.compression_class == "very_high"


# ── avg_frame_size_kb ─────────────────────────────────────────────────────────

class TestAvgFrameSizeKb:
    def test_no_frames_returns_zero(self):
        doc = _make_doc(0, 0, frames=0)
        assert doc.avg_frame_size_kb == pytest.approx(0.0)

    def test_single_frame_1024_bytes_is_1kb(self):
        doc = _make_doc(1024, 10000, frames=1)
        assert doc.avg_frame_size_kb == pytest.approx(1.0)

    def test_two_frames_2048_bytes_is_1kb_each(self):
        doc = _make_doc(2048, 10000, frames=2)
        assert doc.avg_frame_size_kb == pytest.approx(1.0)

    def test_larger_compressed_size(self):
        # 10 * 1024 bytes / 10 frames = 1024 bytes / frame = 1.0 KB
        doc = _make_doc(10 * 1024, 100000, frames=10)
        assert doc.avg_frame_size_kb == pytest.approx(1.0)

    def test_fraction_kb(self):
        # 512 bytes / 1 frame = 0.5 KB
        doc = _make_doc(512, 5000, frames=1)
        assert doc.avg_frame_size_kb == pytest.approx(0.5)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_very_high_implies_highly_compressible(self):
        doc = _make_doc(50, 1000)
        assert doc.compression_class == "very_high"
        assert doc.is_highly_compressible is True

    def test_none_class_not_highly_compressible(self):
        doc = _make_doc(1000, 1000)
        assert doc.compression_class == "none"
        assert doc.is_highly_compressible is False

    def test_multi_frame_avg_size_consistent(self):
        doc = _make_doc(4096, 40000, frames=4)
        assert doc.is_multi_frame is True
        assert doc.avg_frame_size_kb == pytest.approx(1.0)

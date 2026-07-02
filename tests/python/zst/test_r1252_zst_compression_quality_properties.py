"""Tests for R1252: ZstDocument compression quality classification properties.

Properties under test:
    compressed_size_mb   — compressed_size / 1_048_576.0
    savings_ratio        — 1 - (compressed / decompressed); 0.0 if decompressed == 0
    is_lossless_verified — compressed > 0 and compressed < decompressed

spec_fact_ref: FACT-ZST-001
"""

import pytest
from zst.models import ZstDocument


def _make_doc(compressed: int, decompressed: int, frames: int = 1) -> ZstDocument:
    return ZstDocument(
        path="test.zst",
        data={
            "compressed_size": compressed,
            "decompressed_size": decompressed,
            "frame_count": frames,
        },
    )


# ── compressed_size_mb ────────────────────────────────────────────────────────

class TestCompressedSizeMb:
    def test_one_mib_gives_one(self):
        doc = _make_doc(1_048_576, 2_000_000)
        assert doc.compressed_size_mb == pytest.approx(1.0)

    def test_zero_compressed_zero_mb(self):
        doc = _make_doc(0, 0)
        assert doc.compressed_size_mb == pytest.approx(0.0)

    def test_half_mib(self):
        doc = _make_doc(524_288, 1_000_000)
        assert doc.compressed_size_mb == pytest.approx(0.5)

    def test_small_file_fractional(self):
        doc = _make_doc(1_024, 4_096)
        assert doc.compressed_size_mb == pytest.approx(1_024 / 1_048_576)


# ── savings_ratio ─────────────────────────────────────────────────────────────

class TestSavingsRatio:
    def test_no_decompressed_returns_zero(self):
        doc = _make_doc(0, 0)
        assert doc.savings_ratio == pytest.approx(0.0)

    def test_half_size_savings_50_percent(self):
        doc = _make_doc(500, 1_000)
        assert doc.savings_ratio == pytest.approx(0.5)

    def test_90_percent_savings(self):
        doc = _make_doc(100, 1_000)
        assert doc.savings_ratio == pytest.approx(0.9)

    def test_no_savings_equal_sizes(self):
        doc = _make_doc(1_000, 1_000)
        assert doc.savings_ratio == pytest.approx(0.0)

    def test_large_savings(self):
        doc = _make_doc(10, 10_000)
        assert doc.savings_ratio == pytest.approx(0.999)


# ── is_lossless_verified ──────────────────────────────────────────────────────

class TestIsLosslessVerified:
    def test_compressed_smaller_is_verified(self):
        doc = _make_doc(100, 1_000)
        assert doc.is_lossless_verified is True

    def test_equal_sizes_not_verified(self):
        doc = _make_doc(1_000, 1_000)
        assert doc.is_lossless_verified is False

    def test_zero_compressed_not_verified(self):
        doc = _make_doc(0, 1_000)
        assert doc.is_lossless_verified is False

    def test_zero_decompressed_not_verified(self):
        doc = _make_doc(0, 0)
        assert doc.is_lossless_verified is False

    def test_compressed_larger_not_verified(self):
        doc = _make_doc(2_000, 1_000)
        assert doc.is_lossless_verified is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_verified_implies_positive_savings(self):
        doc = _make_doc(300, 1_000)
        assert doc.is_lossless_verified is True
        assert doc.savings_ratio > 0.0

    def test_savings_ratio_and_size_mb_independent(self):
        doc = _make_doc(1_048_576, 2_097_152)
        assert doc.compressed_size_mb == pytest.approx(1.0)
        assert doc.savings_ratio == pytest.approx(0.5)

    def test_not_verified_savings_not_necessarily_zero(self):
        # equal sizes: verified=False, savings=0.0
        doc = _make_doc(500, 500)
        assert doc.is_lossless_verified is False
        assert doc.savings_ratio == pytest.approx(0.0)

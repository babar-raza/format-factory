"""Tests for R1232: ZstDocument compression quality classification properties.

Properties under test:
    compressed_size_mb  — compressed_size / 1_048_576.0
    savings_ratio       — 1 - (compressed / decompressed); 0.0 if decompressed == 0
    is_lossless_verified — compressed > 0 and compressed < decompressed

spec_fact_ref: FACT-ZST-001
"""

import pytest
from zst.models import ZstDocument


def _make_doc(compressed_size: int, decompressed_size: int, frame_count: int = 1):
    """Build a ZstDocument stub with the given sizes."""
    data = {
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "frame_count": frame_count,
    }
    return ZstDocument("test.zst", data)


# ── compressed_size_mb ────────────────────────────────────────────────────────

class TestCompressedSizeMb:
    def test_zero_compressed_is_zero_mb(self):
        doc = _make_doc(0, 0)
        assert doc.compressed_size_mb == 0.0

    def test_exactly_one_mb(self):
        doc = _make_doc(1_048_576, 0)
        assert doc.compressed_size_mb == pytest.approx(1.0)

    def test_half_mb(self):
        doc = _make_doc(524_288, 0)
        assert doc.compressed_size_mb == pytest.approx(0.5)

    def test_small_file(self):
        doc = _make_doc(1024, 0)
        assert doc.compressed_size_mb == pytest.approx(1024 / 1_048_576.0)

    def test_large_file(self):
        doc = _make_doc(10_485_760, 0)
        assert doc.compressed_size_mb == pytest.approx(10.0)

    def test_returns_float(self):
        doc = _make_doc(1_048_576, 0)
        assert isinstance(doc.compressed_size_mb, float)


# ── savings_ratio ─────────────────────────────────────────────────────────────

class TestSavingsRatio:
    def test_zero_decompressed_returns_zero(self):
        doc = _make_doc(1000, 0)
        assert doc.savings_ratio == 0.0

    def test_no_compression_returns_zero(self):
        doc = _make_doc(1000, 1000)
        assert doc.savings_ratio == pytest.approx(0.0)

    def test_fifty_percent_savings(self):
        doc = _make_doc(500, 1000)  # 1 - 500/1000 = 0.5
        assert doc.savings_ratio == pytest.approx(0.5)

    def test_ninety_percent_savings(self):
        doc = _make_doc(100, 1000)  # 1 - 100/1000 = 0.9
        assert doc.savings_ratio == pytest.approx(0.9)

    def test_expansion_is_negative(self):
        doc = _make_doc(1100, 1000)  # 1 - 1100/1000 = -0.1
        assert doc.savings_ratio == pytest.approx(-0.1)

    def test_full_compression_returns_one(self):
        doc = _make_doc(0, 1000)  # 1 - 0/1000 = 1.0
        assert doc.savings_ratio == pytest.approx(1.0)

    def test_returns_float(self):
        doc = _make_doc(500, 1000)
        assert isinstance(doc.savings_ratio, float)


# ── is_lossless_verified ──────────────────────────────────────────────────────

class TestIsLosslessVerified:
    def test_compressed_less_than_decompressed_is_verified(self):
        doc = _make_doc(100, 1000)
        assert doc.is_lossless_verified is True

    def test_equal_sizes_not_verified(self):
        doc = _make_doc(1000, 1000)
        assert doc.is_lossless_verified is False

    def test_compressed_greater_not_verified(self):
        doc = _make_doc(1100, 1000)
        assert doc.is_lossless_verified is False

    def test_zero_compressed_not_verified(self):
        doc = _make_doc(0, 1000)
        assert doc.is_lossless_verified is False

    def test_zero_both_not_verified(self):
        doc = _make_doc(0, 0)
        assert doc.is_lossless_verified is False

    def test_small_savings_is_verified(self):
        doc = _make_doc(999, 1000)
        assert doc.is_lossless_verified is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_good_compression_has_high_savings_and_verified(self):
        doc = _make_doc(100, 1000)
        assert doc.is_lossless_verified is True
        assert doc.savings_ratio == pytest.approx(0.9)

    def test_expansion_not_verified(self):
        doc = _make_doc(1200, 1000)
        assert doc.is_lossless_verified is False
        assert doc.savings_ratio < 0

    def test_mb_size_consistent_with_compressed_size(self):
        doc = _make_doc(2_097_152, 10_000_000)  # 2 MB compressed
        assert doc.compressed_size_mb == pytest.approx(2.0)
        assert doc.is_lossless_verified is True

    def test_empty_file_all_zero(self):
        doc = _make_doc(0, 0)
        assert doc.compressed_size_mb == 0.0
        assert doc.savings_ratio == 0.0
        assert doc.is_lossless_verified is False

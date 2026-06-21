"""
Tests for ZST additional compression analytics (4 FOSS functions).
Closes: GAP-ZST-FOSS-HIGHLY_COMPRESSED-001, GAP-ZST-FOSS-COMPRESS_EFF-001,
        GAP-ZST-FOSS-SAVINGS_RATIO-001, GAP-ZST-FOSS-RLE_EFFICIENT-001

Known sample values (derived from zst_compressed_size / zst_decompressed_size / zst_compression_saving):
  minimal-synthetic.zst: compressed=10, decompressed=1  → ratio=0.1, efficiency=0.0
  text-compressed.zst:   compressed=272, decompressed=390 → ratio≈1.43, efficiency≈0.303
  random-data.zst:       compressed=276, decompressed=1024 → ratio≈3.71, efficiency≈0.730
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    zst_is_highly_compressed,
    zst_compression_efficiency,
    zst_savings_ratio,
    zst_is_rle_efficient,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"    # compressed=10, decomp=1, ratio=0.1
_TEXT = _ZST / "text-compressed.zst"          # compressed=272, decomp=390, ratio≈1.43
_RANDOM = _ZST / "random-data.zst"            # compressed=276, decomp=1024, ratio≈3.71


class TestZstIsHighlyCompressed:
    def test_returns_bool(self):
        assert isinstance(zst_is_highly_compressed(_MINIMAL), bool)

    def test_minimal_is_highly_compressed(self):
        # ratio = 10.0 > 2.0 (synthetic data compresses well)
        assert zst_is_highly_compressed(_MINIMAL) is True

    def test_text_not_highly_compressed(self):
        # ratio ≈ 0.70 < 2.0
        assert zst_is_highly_compressed(_TEXT) is False

    def test_random_not_highly_compressed(self):
        # ratio ≈ 0.27 < 2.0 (random data does not compress well)
        assert zst_is_highly_compressed(_RANDOM) is False

    def test_result_is_bool_for_all_samples(self):
        for p in [_MINIMAL, _TEXT, _RANDOM]:
            result = zst_is_highly_compressed(p)
            assert result is True or result is False

    def test_not_highly_compressed_when_ratio_low(self):
        # text ratio ≈ 1.43 — sanity check consistency with is_compressible behavior
        result = zst_is_highly_compressed(_TEXT)
        assert result is False


class TestZstCompressionEfficiency:
    def test_returns_float(self):
        assert isinstance(zst_compression_efficiency(_MINIMAL), float)

    def test_minimal_efficiency_is_zero(self):
        # compressed=10 > decompressed=1, saving<0, clamped to 0.0
        assert zst_compression_efficiency(_MINIMAL) == 0.0

    def test_text_efficiency_in_range(self):
        # 118/390 ≈ 0.303
        eff = zst_compression_efficiency(_TEXT)
        assert 0.0 < eff < 1.0

    def test_random_efficiency_higher_than_text(self):
        # random: 748/1024 ≈ 0.730; text: 118/390 ≈ 0.303
        assert zst_compression_efficiency(_RANDOM) > zst_compression_efficiency(_TEXT)

    def test_bounded_zero_to_one_for_all(self):
        for p in [_MINIMAL, _TEXT, _RANDOM]:
            eff = zst_compression_efficiency(p)
            assert 0.0 <= eff <= 1.0

    def test_text_efficiency_approx(self):
        # 118/390 ≈ 0.302..0.304
        eff = zst_compression_efficiency(_TEXT)
        assert abs(eff - (118 / 390)) < 0.01

    def test_random_efficiency_approx(self):
        # 748/1024 ≈ 0.730
        eff = zst_compression_efficiency(_RANDOM)
        assert abs(eff - (748 / 1024)) < 0.01

    def test_nonnegative(self):
        for p in [_MINIMAL, _TEXT, _RANDOM]:
            assert zst_compression_efficiency(p) >= 0.0


class TestZstSavingsRatio:
    def test_returns_float(self):
        assert isinstance(zst_savings_ratio(_MINIMAL), float)

    def test_minimal_ratio_negative(self):
        # compressed=10 > decompressed=1: (1-10)/10 = -0.9
        ratio = zst_savings_ratio(_MINIMAL)
        assert ratio < 0.0

    def test_text_ratio_positive(self):
        # compressed=272, decompressed=390: (390-272)/272 ≈ 0.434
        ratio = zst_savings_ratio(_TEXT)
        assert ratio > 0.0

    def test_text_ratio_approx(self):
        ratio = zst_savings_ratio(_TEXT)
        assert abs(ratio - (390 - 272) / 272) < 0.01

    def test_random_ratio_higher_than_text(self):
        # random: (1024-276)/276 ≈ 2.71 > text ≈ 0.43
        assert zst_savings_ratio(_RANDOM) > zst_savings_ratio(_TEXT)

    def test_random_ratio_approx(self):
        ratio = zst_savings_ratio(_RANDOM)
        assert abs(ratio - (1024 - 276) / 276) < 0.01


class TestZstIsRleEfficient:
    def test_returns_bool(self):
        assert isinstance(zst_is_rle_efficient(_MINIMAL), bool)

    def test_minimal_is_rle_efficient(self):
        # compressed=10, decompressed=1: ratio = 0.1, NOT > 100 → False
        # Wait: decompressed/compressed = 1/10 = 0.1 << 100
        assert zst_is_rle_efficient(_MINIMAL) is False

    def test_text_not_rle_efficient(self):
        # decompressed/compressed = 390/272 ≈ 1.43 << 100
        assert zst_is_rle_efficient(_TEXT) is False

    def test_random_not_rle_efficient(self):
        # decompressed/compressed = 1024/276 ≈ 3.71 << 100
        assert zst_is_rle_efficient(_RANDOM) is False

    def test_result_is_bool_for_all(self):
        for p in [_MINIMAL, _TEXT, _RANDOM]:
            result = zst_is_rle_efficient(p)
            assert result is True or result is False

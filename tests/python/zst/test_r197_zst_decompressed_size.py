"""
Tests for zst_decompressed_size — sprint product-deepening-rnext66.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ZST_SAMPLES = REPO / "samples" / "by-format" / "zst" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from zst.zst_codec import zst_decompressed_size


def test_import():
    assert callable(zst_decompressed_size)


def test_minimal_synthetic_returns_one():
    result = zst_decompressed_size(ZST_SAMPLES / "minimal-synthetic.zst")
    assert result == 1


def test_text_compressed_returns_correct_size():
    result = zst_decompressed_size(ZST_SAMPLES / "text-compressed.zst")
    assert result == 390


def test_returns_int():
    result = zst_decompressed_size(ZST_SAMPLES / "minimal-synthetic.zst")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = zst_decompressed_size(ZST_SAMPLES / "text-compressed.zst")
    assert result >= 0


def test_random_data_positive_size():
    result = zst_decompressed_size(ZST_SAMPLES / "random-data.zst")
    assert result > 0

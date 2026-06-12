"""
Tests for zst_frame_count — sprint product-deepening-rnext73.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ZST_SAMPLES = REPO / "samples" / "by-format" / "zst" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from zst.zst_codec import zst_frame_count


def test_import():
    assert callable(zst_frame_count)


def test_minimal_synthetic_has_one_frame():
    result = zst_frame_count(ZST_SAMPLES / "minimal-synthetic.zst")
    assert result == 1


def test_text_compressed_has_one_frame():
    result = zst_frame_count(ZST_SAMPLES / "text-compressed.zst")
    assert result == 1


def test_random_data_has_one_frame():
    result = zst_frame_count(ZST_SAMPLES / "random-data.zst")
    assert result == 1


def test_returns_int():
    result = zst_frame_count(ZST_SAMPLES / "minimal-synthetic.zst")
    assert isinstance(result, int)


def test_result_positive_for_valid_file():
    result = zst_frame_count(ZST_SAMPLES / "text-compressed.zst")
    assert result >= 1

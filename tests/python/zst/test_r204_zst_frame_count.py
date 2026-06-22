"""
Tests for zst_frame_count — sprint product-deepening-rnext73.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
GAP-ZST-FOSS-ZST_FRAME_CO-001: missing_test_coverage (multi-frame, edge cases added)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

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


def test_string_path_accepted():
    result = zst_frame_count(str(ZST_SAMPLES / "minimal-synthetic.zst"))
    assert isinstance(result, int)
    assert result >= 1


def test_empty_file_returns_zero(tmp_path):
    empty = tmp_path / "empty.zst"
    empty.write_bytes(b"")
    result = zst_frame_count(empty)
    assert result == 0


def test_multi_frame_count(tmp_path):
    """Two concatenated ZST frames must yield count == 2."""
    try:
        import zstandard
    except ImportError:
        pytest.skip("zstandard not installed")
    cctx = zstandard.ZstdCompressor()
    frame1 = cctx.compress(b"Frame one " * 50)
    frame2 = cctx.compress(b"Frame two " * 50)
    p = tmp_path / "multi.zst"
    p.write_bytes(frame1 + frame2)
    result = zst_frame_count(p)
    assert result == 2


def test_single_constructed_frame_count(tmp_path):
    """Programmatically constructed single-frame file returns 1."""
    try:
        import zstandard
    except ImportError:
        pytest.skip("zstandard not installed")
    data = b"Hello ZST frame count test " * 100
    compressed = zstandard.ZstdCompressor().compress(data)
    p = tmp_path / "single.zst"
    p.write_bytes(compressed)
    assert zst_frame_count(p) == 1

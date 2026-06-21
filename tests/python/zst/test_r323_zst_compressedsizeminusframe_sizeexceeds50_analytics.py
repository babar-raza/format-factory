"""
r323 ZST analytics: zst_compressed_size_minus_frame_count, zst_size_exceeds_50.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_compressed_size_minus_frame_count, zst_size_exceeds_50

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


# --- zst_compressed_size_minus_frame_count ---

def test_minus_frame_minimal():
    assert zst_compressed_size_minus_frame_count(_ZST / "minimal-synthetic.zst") == 9

def test_minus_frame_empty_block():
    assert zst_compressed_size_minus_frame_count(_ZST / "empty-block.zst") == 10

def test_minus_frame_block_128k():
    assert zst_compressed_size_minus_frame_count(_ZST / "block-128k.zst") == 131080

def test_minus_frame_returns_int():
    result = zst_compressed_size_minus_frame_count(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, int)

def test_minus_frame_nonnegative():
    for f in ["minimal-synthetic.zst", "empty-block.zst", "block-128k.zst"]:
        assert zst_compressed_size_minus_frame_count(_ZST / f) >= 0

def test_minus_frame_all_distinct():
    results = [
        zst_compressed_size_minus_frame_count(_ZST / "minimal-synthetic.zst"),
        zst_compressed_size_minus_frame_count(_ZST / "empty-block.zst"),
        zst_compressed_size_minus_frame_count(_ZST / "block-128k.zst"),
    ]
    assert len(set(results)) == 3


# --- zst_size_exceeds_50 ---

def test_size_exceeds_50_minimal_false():
    assert zst_size_exceeds_50(_ZST / "minimal-synthetic.zst") is False

def test_size_exceeds_50_empty_block_false():
    assert zst_size_exceeds_50(_ZST / "empty-block.zst") is False

def test_size_exceeds_50_block_128k_true():
    assert zst_size_exceeds_50(_ZST / "block-128k.zst") is True

def test_size_exceeds_50_returns_bool():
    result = zst_size_exceeds_50(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, bool)

def test_size_exceeds_50_empty_is_bool():
    result = zst_size_exceeds_50(_ZST / "empty-block.zst")
    assert isinstance(result, bool)

def test_size_exceeds_50_only_128k_true():
    results = [
        zst_size_exceeds_50(_ZST / "minimal-synthetic.zst"),
        zst_size_exceeds_50(_ZST / "empty-block.zst"),
        zst_size_exceeds_50(_ZST / "block-128k.zst"),
    ]
    assert results.count(True) == 1

"""
r325 ZST analytics: zst_compressed_size_plus_frame_count, zst_overhead_ratio_exceeds_half.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_compressed_size_plus_frame_count, zst_overhead_ratio_exceeds_half

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


# --- zst_compressed_size_plus_frame_count ---

def test_size_plus_frame_minimal():
    assert zst_compressed_size_plus_frame_count(_ZST / "minimal-synthetic.zst") == 11

def test_size_plus_frame_empty_block():
    assert zst_compressed_size_plus_frame_count(_ZST / "empty-block.zst") == 12

def test_size_plus_frame_block_128k():
    assert zst_compressed_size_plus_frame_count(_ZST / "block-128k.zst") == 131082

def test_size_plus_frame_returns_int():
    result = zst_compressed_size_plus_frame_count(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, int)

def test_size_plus_frame_positive():
    for f in ["minimal-synthetic.zst", "empty-block.zst", "block-128k.zst"]:
        assert zst_compressed_size_plus_frame_count(_ZST / f) > 0

def test_size_plus_frame_all_distinct():
    results = [
        zst_compressed_size_plus_frame_count(_ZST / "minimal-synthetic.zst"),
        zst_compressed_size_plus_frame_count(_ZST / "empty-block.zst"),
        zst_compressed_size_plus_frame_count(_ZST / "block-128k.zst"),
    ]
    assert len(set(results)) == 3


# --- zst_overhead_ratio_exceeds_half ---

def test_overhead_exceeds_half_minimal_true():
    assert zst_overhead_ratio_exceeds_half(_ZST / "minimal-synthetic.zst") is True

def test_overhead_exceeds_half_empty_block_true():
    assert zst_overhead_ratio_exceeds_half(_ZST / "empty-block.zst") is True

def test_overhead_exceeds_half_block_128k_false():
    assert zst_overhead_ratio_exceeds_half(_ZST / "block-128k.zst") is False

def test_overhead_exceeds_half_returns_bool():
    result = zst_overhead_ratio_exceeds_half(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, bool)

def test_overhead_exceeds_half_empty_block_is_bool():
    result = zst_overhead_ratio_exceeds_half(_ZST / "empty-block.zst")
    assert isinstance(result, bool)

def test_overhead_exceeds_half_only_128k_false():
    results = [
        zst_overhead_ratio_exceeds_half(_ZST / "minimal-synthetic.zst"),
        zst_overhead_ratio_exceeds_half(_ZST / "empty-block.zst"),
        zst_overhead_ratio_exceeds_half(_ZST / "block-128k.zst"),
    ]
    assert results.count(False) == 1

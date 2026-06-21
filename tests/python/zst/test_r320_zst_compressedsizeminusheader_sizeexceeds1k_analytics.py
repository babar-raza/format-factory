"""
r320 ZST analytics: zst_compressed_size_minus_header, zst_size_exceeds_1k.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_compressed_size_minus_header, zst_size_exceeds_1k

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


# --- zst_compressed_size_minus_header ---

def test_compressed_minus_header_minimal_synthetic():
    assert zst_compressed_size_minus_header(_ZST / "minimal-synthetic.zst") == 4

def test_compressed_minus_header_dict_compressed():
    assert zst_compressed_size_minus_header(_ZST / "dict-compressed.zst") == 68

def test_compressed_minus_header_block_128k():
    assert zst_compressed_size_minus_header(_ZST / "block-128k.zst") == 131075

def test_compressed_minus_header_returns_int():
    result = zst_compressed_size_minus_header(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, int)

def test_compressed_minus_header_nonnegative():
    for f in ["minimal-synthetic.zst", "dict-compressed.zst", "block-128k.zst"]:
        assert zst_compressed_size_minus_header(_ZST / f) >= 0

def test_compressed_minus_header_all_distinct():
    results = [
        zst_compressed_size_minus_header(_ZST / "minimal-synthetic.zst"),
        zst_compressed_size_minus_header(_ZST / "dict-compressed.zst"),
        zst_compressed_size_minus_header(_ZST / "block-128k.zst"),
    ]
    assert len(set(results)) == 3


# --- zst_size_exceeds_1k ---

def test_size_exceeds_1k_minimal_synthetic_false():
    assert zst_size_exceeds_1k(_ZST / "minimal-synthetic.zst") is False

def test_size_exceeds_1k_dict_compressed_false():
    assert zst_size_exceeds_1k(_ZST / "dict-compressed.zst") is False

def test_size_exceeds_1k_block_128k_true():
    assert zst_size_exceeds_1k(_ZST / "block-128k.zst") is True

def test_size_exceeds_1k_returns_bool():
    result = zst_size_exceeds_1k(_ZST / "minimal-synthetic.zst")
    assert isinstance(result, bool)

def test_size_exceeds_1k_dict_compressed_is_bool():
    result = zst_size_exceeds_1k(_ZST / "dict-compressed.zst")
    assert isinstance(result, bool)

def test_size_exceeds_1k_only_block_true():
    results = [
        zst_size_exceeds_1k(_ZST / "minimal-synthetic.zst"),
        zst_size_exceeds_1k(_ZST / "dict-compressed.zst"),
        zst_size_exceeds_1k(_ZST / "block-128k.zst"),
    ]
    assert results.count(True) == 1

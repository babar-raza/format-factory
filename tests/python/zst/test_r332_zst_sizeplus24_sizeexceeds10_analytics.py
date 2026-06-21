"""
Sprint r332: ZST analytics — zst_compressed_size_plus_24, zst_compressed_size_exceeds_10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_plus_24,
    zst_compressed_size_exceeds_10,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → +24=34, >10=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → +24=98, >10=True
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → +24=131105, >10=True


# --- zst_compressed_size_plus_24 ---

def test_size_plus_24_minimal():
    assert zst_compressed_size_plus_24(_MINIMAL) == 34


def test_size_plus_24_dict():
    assert zst_compressed_size_plus_24(_DICT) == 98


def test_size_plus_24_block():
    assert zst_compressed_size_plus_24(_BLOCK) == 131105


def test_size_plus_24_returns_int():
    assert isinstance(zst_compressed_size_plus_24(_MINIMAL), int)


def test_size_plus_24_positive():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_plus_24(p) > 0


def test_size_plus_24_all_distinct():
    vals = [zst_compressed_size_plus_24(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_10 ---

def test_size_exceeds_10_minimal():
    assert zst_compressed_size_exceeds_10(_MINIMAL) is False


def test_size_exceeds_10_dict():
    assert zst_compressed_size_exceeds_10(_DICT) is True


def test_size_exceeds_10_block():
    assert zst_compressed_size_exceeds_10(_BLOCK) is True


def test_size_exceeds_10_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_10(_MINIMAL), bool)


def test_size_exceeds_10_true_case():
    assert zst_compressed_size_exceeds_10(_BLOCK) is True


def test_size_exceeds_10_false_case():
    assert zst_compressed_size_exceeds_10(_MINIMAL) is False

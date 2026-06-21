"""
Sprint r333: ZST analytics — zst_compressed_size_minus_24, zst_compressed_size_exceeds_40
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_minus_24,
    zst_compressed_size_exceeds_40,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → max(0,10-24)=0, >40=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → 74-24=50, >40=True
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → 131081-24=131057, >40=True


# --- zst_compressed_size_minus_24 ---

def test_size_minus_24_minimal():
    assert zst_compressed_size_minus_24(_MINIMAL) == 0


def test_size_minus_24_dict():
    assert zst_compressed_size_minus_24(_DICT) == 50


def test_size_minus_24_block():
    assert zst_compressed_size_minus_24(_BLOCK) == 131057


def test_size_minus_24_returns_int():
    assert isinstance(zst_compressed_size_minus_24(_MINIMAL), int)


def test_size_minus_24_nonnegative():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_minus_24(p) >= 0


def test_size_minus_24_all_distinct():
    vals = [zst_compressed_size_minus_24(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_40 ---

def test_size_exceeds_40_minimal():
    assert zst_compressed_size_exceeds_40(_MINIMAL) is False


def test_size_exceeds_40_dict():
    assert zst_compressed_size_exceeds_40(_DICT) is True


def test_size_exceeds_40_block():
    assert zst_compressed_size_exceeds_40(_BLOCK) is True


def test_size_exceeds_40_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_40(_MINIMAL), bool)


def test_size_exceeds_40_true_case():
    assert zst_compressed_size_exceeds_40(_BLOCK) is True


def test_size_exceeds_40_false_case():
    assert zst_compressed_size_exceeds_40(_MINIMAL) is False

"""
Sprint r328: ZST analytics — zst_compressed_size_minus_12, zst_compressed_size_exceeds_60
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_minus_12,
    zst_compressed_size_exceeds_60,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → minus_12=0, exceeds_60=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → minus_12=62, exceeds_60=True
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → minus_12=131069, exceeds_60=True


# --- zst_compressed_size_minus_12 ---

def test_size_minus_12_minimal():
    assert zst_compressed_size_minus_12(_MINIMAL) == 0


def test_size_minus_12_dict():
    assert zst_compressed_size_minus_12(_DICT) == 62


def test_size_minus_12_block():
    assert zst_compressed_size_minus_12(_BLOCK) == 131069


def test_size_minus_12_returns_int():
    assert isinstance(zst_compressed_size_minus_12(_MINIMAL), int)


def test_size_minus_12_nonnegative():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_minus_12(p) >= 0


def test_size_minus_12_all_distinct():
    vals = [zst_compressed_size_minus_12(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_60 ---

def test_size_exceeds_60_minimal():
    assert zst_compressed_size_exceeds_60(_MINIMAL) is False


def test_size_exceeds_60_dict():
    assert zst_compressed_size_exceeds_60(_DICT) is True


def test_size_exceeds_60_block():
    assert zst_compressed_size_exceeds_60(_BLOCK) is True


def test_size_exceeds_60_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_60(_MINIMAL), bool)


def test_size_exceeds_60_true_case():
    assert zst_compressed_size_exceeds_60(_BLOCK) is True


def test_size_exceeds_60_false_case():
    assert zst_compressed_size_exceeds_60(_MINIMAL) is False

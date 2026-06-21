"""
Sprint r335: ZST analytics — zst_compressed_size_minus_36, zst_compressed_size_exceeds_80
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_minus_36,
    zst_compressed_size_exceeds_80,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → max(0,10-36)=0, >80=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → 74-36=38, >80=False
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → 131081-36=131045, >80=True


# --- zst_compressed_size_minus_36 ---

def test_size_minus_36_minimal():
    assert zst_compressed_size_minus_36(_MINIMAL) == 0


def test_size_minus_36_dict():
    assert zst_compressed_size_minus_36(_DICT) == 38


def test_size_minus_36_block():
    assert zst_compressed_size_minus_36(_BLOCK) == 131045


def test_size_minus_36_returns_int():
    assert isinstance(zst_compressed_size_minus_36(_MINIMAL), int)


def test_size_minus_36_nonnegative():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_minus_36(p) >= 0


def test_size_minus_36_all_distinct():
    vals = [zst_compressed_size_minus_36(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_80 ---

def test_size_exceeds_80_minimal():
    assert zst_compressed_size_exceeds_80(_MINIMAL) is False


def test_size_exceeds_80_dict():
    assert zst_compressed_size_exceeds_80(_DICT) is False


def test_size_exceeds_80_block():
    assert zst_compressed_size_exceeds_80(_BLOCK) is True


def test_size_exceeds_80_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_80(_MINIMAL), bool)


def test_size_exceeds_80_true_case():
    assert zst_compressed_size_exceeds_80(_BLOCK) is True


def test_size_exceeds_80_false_case():
    assert zst_compressed_size_exceeds_80(_MINIMAL) is False

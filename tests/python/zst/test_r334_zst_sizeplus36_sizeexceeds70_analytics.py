"""
Sprint r334: ZST analytics — zst_compressed_size_plus_36, zst_compressed_size_exceeds_70
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_plus_36,
    zst_compressed_size_exceeds_70,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → +36=46, >70=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → +36=110, >70=True
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → +36=131117, >70=True


# --- zst_compressed_size_plus_36 ---

def test_size_plus_36_minimal():
    assert zst_compressed_size_plus_36(_MINIMAL) == 46


def test_size_plus_36_dict():
    assert zst_compressed_size_plus_36(_DICT) == 110


def test_size_plus_36_block():
    assert zst_compressed_size_plus_36(_BLOCK) == 131117


def test_size_plus_36_returns_int():
    assert isinstance(zst_compressed_size_plus_36(_MINIMAL), int)


def test_size_plus_36_positive():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_plus_36(p) > 0


def test_size_plus_36_all_distinct():
    vals = [zst_compressed_size_plus_36(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_70 ---

def test_size_exceeds_70_minimal():
    assert zst_compressed_size_exceeds_70(_MINIMAL) is False


def test_size_exceeds_70_dict():
    assert zst_compressed_size_exceeds_70(_DICT) is True


def test_size_exceeds_70_block():
    assert zst_compressed_size_exceeds_70(_BLOCK) is True


def test_size_exceeds_70_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_70(_MINIMAL), bool)


def test_size_exceeds_70_true_case():
    assert zst_compressed_size_exceeds_70(_BLOCK) is True


def test_size_exceeds_70_false_case():
    assert zst_compressed_size_exceeds_70(_MINIMAL) is False

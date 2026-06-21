"""
Sprint r331: ZST analytics — zst_compressed_size_plus_12, zst_compressed_size_exceeds_30
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_plus_12,
    zst_compressed_size_exceeds_30,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10 → +12=22, >30=False
_DICT    = _ZST / "dict-compressed.zst"    # size=74 → +12=86, >30=True
_BLOCK   = _ZST / "block-128k.zst"         # size=131081 → +12=131093, >30=True


# --- zst_compressed_size_plus_12 ---

def test_size_plus_12_minimal():
    assert zst_compressed_size_plus_12(_MINIMAL) == 22


def test_size_plus_12_dict():
    assert zst_compressed_size_plus_12(_DICT) == 86


def test_size_plus_12_block():
    assert zst_compressed_size_plus_12(_BLOCK) == 131093


def test_size_plus_12_returns_int():
    assert isinstance(zst_compressed_size_plus_12(_MINIMAL), int)


def test_size_plus_12_positive():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_plus_12(p) > 0


def test_size_plus_12_all_distinct():
    vals = [zst_compressed_size_plus_12(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_30 ---

def test_size_exceeds_30_minimal():
    assert zst_compressed_size_exceeds_30(_MINIMAL) is False


def test_size_exceeds_30_dict():
    assert zst_compressed_size_exceeds_30(_DICT) is True


def test_size_exceeds_30_block():
    assert zst_compressed_size_exceeds_30(_BLOCK) is True


def test_size_exceeds_30_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_30(_MINIMAL), bool)


def test_size_exceeds_30_true_case():
    assert zst_compressed_size_exceeds_30(_BLOCK) is True


def test_size_exceeds_30_false_case():
    assert zst_compressed_size_exceeds_30(_MINIMAL) is False

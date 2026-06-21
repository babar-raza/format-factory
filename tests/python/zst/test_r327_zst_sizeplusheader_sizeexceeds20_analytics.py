"""
Sprint r327: ZST analytics — zst_compressed_size_plus_header_size, zst_compressed_size_exceeds_20
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    zst_compressed_size_plus_header_size,
    zst_compressed_size_exceeds_20,
)

_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = _ZST / "minimal-synthetic.zst"   # size=10, header=6 → sum=16
_DICT    = _ZST / "dict-compressed.zst"    # size=74, header=6 → sum=80
_BLOCK   = _ZST / "block-128k.zst"         # size=131081, header=6 → sum=131087


# --- zst_compressed_size_plus_header_size ---

def test_size_plus_header_minimal():
    assert zst_compressed_size_plus_header_size(_MINIMAL) == 16


def test_size_plus_header_dict():
    assert zst_compressed_size_plus_header_size(_DICT) == 80


def test_size_plus_header_block():
    assert zst_compressed_size_plus_header_size(_BLOCK) == 131087


def test_size_plus_header_returns_int():
    assert isinstance(zst_compressed_size_plus_header_size(_MINIMAL), int)


def test_size_plus_header_positive():
    for p in (_MINIMAL, _DICT, _BLOCK):
        assert zst_compressed_size_plus_header_size(p) > 0


def test_size_plus_header_all_distinct():
    vals = [zst_compressed_size_plus_header_size(p) for p in (_MINIMAL, _DICT, _BLOCK)]
    assert len(set(vals)) == 3


# --- zst_compressed_size_exceeds_20 ---

def test_size_exceeds_20_minimal():
    assert zst_compressed_size_exceeds_20(_MINIMAL) is False


def test_size_exceeds_20_dict():
    assert zst_compressed_size_exceeds_20(_DICT) is True


def test_size_exceeds_20_block():
    assert zst_compressed_size_exceeds_20(_BLOCK) is True


def test_size_exceeds_20_returns_bool():
    assert isinstance(zst_compressed_size_exceeds_20(_MINIMAL), bool)


def test_size_exceeds_20_true_case():
    assert zst_compressed_size_exceeds_20(_BLOCK) is True


def test_size_exceeds_20_false_case():
    assert zst_compressed_size_exceeds_20(_MINIMAL) is False

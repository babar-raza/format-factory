"""Tests for ZST file stats extension functions in zst_file_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_file_stats import (
    zst_compressed_size_kb,
    zst_decompressed_size_kb,
    zst_has_space_savings,
    zst_ratio_below_half,
    zst_size_category,
    zst_is_ratio_above_one,
)

SAMPLES = Path("samples/by-format/zst/valid")
MINIMAL = SAMPLES / "minimal-synthetic.zst"   # compressed=10, decompressed=1 (expansion)
TEXT    = SAMPLES / "text-compressed.zst"     # compressed=272, decompressed=390 (savings)
RLE     = SAMPLES / "rle-first-block.zst"     # compressed=45, decompressed=1048576 (high ratio)


# --- zst_compressed_size_kb ---

def test_compressed_size_kb_minimal():
    result = zst_compressed_size_kb(MINIMAL)
    assert result == pytest.approx(10 / 1024.0)


def test_compressed_size_kb_text():
    result = zst_compressed_size_kb(TEXT)
    assert result == pytest.approx(272 / 1024.0)


def test_compressed_size_kb_returns_float():
    assert isinstance(zst_compressed_size_kb(MINIMAL), float)


# --- zst_decompressed_size_kb ---

def test_decompressed_size_kb_minimal():
    result = zst_decompressed_size_kb(MINIMAL)
    assert result == pytest.approx(1 / 1024.0)


def test_decompressed_size_kb_text():
    result = zst_decompressed_size_kb(TEXT)
    assert result == pytest.approx(390 / 1024.0)


def test_decompressed_size_kb_returns_float():
    assert isinstance(zst_decompressed_size_kb(MINIMAL), float)


# --- zst_has_space_savings ---

def test_has_space_savings_minimal():
    # compressed=10 > decompressed=1 → no savings
    assert zst_has_space_savings(MINIMAL) is False


def test_has_space_savings_text():
    # compressed=272 < decompressed=390 → has savings
    assert zst_has_space_savings(TEXT) is True


def test_has_space_savings_rle():
    assert zst_has_space_savings(RLE) is True


def test_has_space_savings_returns_bool():
    assert isinstance(zst_has_space_savings(MINIMAL), bool)


# --- zst_ratio_below_half ---

def test_ratio_below_half_minimal():
    # 10/1 = 10 → not below 0.5
    assert zst_ratio_below_half(MINIMAL) is False


def test_ratio_below_half_text():
    # 272/390 ≈ 0.7 → not below 0.5
    assert zst_ratio_below_half(TEXT) is False


def test_ratio_below_half_rle():
    # 45/1048576 ≈ 0.00004 → below 0.5
    assert zst_ratio_below_half(RLE) is True


def test_ratio_below_half_returns_bool():
    assert isinstance(zst_ratio_below_half(MINIMAL), bool)


# --- zst_size_category ---

def test_size_category_minimal():
    # decompressed=1 byte → tiny
    assert zst_size_category(MINIMAL) == "tiny"


def test_size_category_text():
    # decompressed=390 bytes → tiny
    assert zst_size_category(TEXT) == "tiny"


def test_size_category_rle():
    # decompressed=1048576 bytes = 1 MB → medium
    assert zst_size_category(RLE) == "medium"


def test_size_category_returns_str():
    assert isinstance(zst_size_category(MINIMAL), str)


# --- zst_is_ratio_above_one ---

def test_is_ratio_above_one_minimal():
    # compressed=10 > decompressed=1 → expansion
    assert zst_is_ratio_above_one(MINIMAL) is True


def test_is_ratio_above_one_text():
    # compressed=272 < decompressed=390 → no expansion
    assert zst_is_ratio_above_one(TEXT) is False


def test_is_ratio_above_one_rle():
    assert zst_is_ratio_above_one(RLE) is False


def test_is_ratio_above_one_returns_bool():
    assert isinstance(zst_is_ratio_above_one(MINIMAL), bool)

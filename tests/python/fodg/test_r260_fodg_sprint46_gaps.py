"""Tests for FODG Sprint 46 gap closure.

Closes:
  GAP-FODG-FOSS-FODG_FILE_SI-001  (Fodg File Size Bytes)
  GAP-FODG-FOSS-FODG_MIN_TEX-001  (Fodg Min Text Item Length)
  GAP-FODG-FOSS-FODG_UNIQUE_-001  (Fodg Unique Text Item Count)
  GAP-FODG-FOSS-FODG_TEXT_IT-001  (Fodg Text Item Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_bytes,
    fodg_min_text_item_length,
    fodg_unique_text_item_count,
    fodg_text_item_count,
)

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = str(_DIR / "empty-page.fodg")
_MINIMAL = str(_DIR / "minimal-drawing.fodg")
_SHAPES = str(_DIR / "shapes-basic.fodg")


class TestFodgFileSizeBytes:
    def test_return_type(self):
        assert isinstance(fodg_file_size_bytes(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        assert fodg_file_size_bytes(_EMPTY) == 1053

    def test_exact_1473_for_minimal(self):
        assert fodg_file_size_bytes(_MINIMAL) == 1473

    def test_exact_1628_for_shapes(self):
        assert fodg_file_size_bytes(_SHAPES) == 1628

    def test_positive(self):
        assert fodg_file_size_bytes(_EMPTY) > 0

    def test_consistent_across_calls(self):
        assert fodg_file_size_bytes(_EMPTY) == fodg_file_size_bytes(_EMPTY)


class TestFodgMinTextItemLength:
    def test_return_type(self):
        assert isinstance(fodg_min_text_item_length(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert fodg_min_text_item_length(_EMPTY) == 0

    def test_exact_9_for_minimal(self):
        assert fodg_min_text_item_length(_MINIMAL) == 9

    def test_exact_4_for_shapes(self):
        assert fodg_min_text_item_length(_SHAPES) == 4

    def test_nonnegative(self):
        assert fodg_min_text_item_length(_MINIMAL) >= 0


class TestFodgUniqueTextItemCount:
    def test_return_type(self):
        assert isinstance(fodg_unique_text_item_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert fodg_unique_text_item_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        assert fodg_unique_text_item_count(_MINIMAL) == 1

    def test_exact_2_for_shapes(self):
        assert fodg_unique_text_item_count(_SHAPES) == 2

    def test_nonnegative(self):
        assert fodg_unique_text_item_count(_MINIMAL) >= 0


class TestFodgTextItemCount:
    def test_return_type(self):
        assert isinstance(fodg_text_item_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert fodg_text_item_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        assert fodg_text_item_count(_MINIMAL) == 1

    def test_exact_2_for_shapes(self):
        assert fodg_text_item_count(_SHAPES) == 2

    def test_nonnegative(self):
        assert fodg_text_item_count(_MINIMAL) >= 0

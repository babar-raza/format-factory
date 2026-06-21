"""
test_r324_fodg_new_analytics.py
Sprint 60 — 5 new FODG analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    fodg_file_size_bytes,
    fodg_min_text_item_length,
    fodg_avg_text_item_length,
    fodg_unique_text_item_count,
    fodg_text_item_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_MINIMAL = str(_SAMPLES / "minimal-drawing.fodg")
_SHAPES = str(_SAMPLES / "shapes-basic.fodg")
_EMPTY = str(_SAMPLES / "empty-page.fodg")


# --- fodg_file_size_bytes ---

class TestFodgFileSizeBytes:
    def test_minimal_positive(self):
        assert fodg_file_size_bytes(_MINIMAL) > 0

    def test_shapes_positive(self):
        assert fodg_file_size_bytes(_SHAPES) > 0

    def test_empty_positive(self):
        assert fodg_file_size_bytes(_EMPTY) > 0

    def test_returns_int(self):
        assert isinstance(fodg_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert fodg_file_size_bytes(_MINIMAL) >= 50


# --- fodg_min_text_item_length ---

class TestFodgMinTextItemLength:
    def test_returns_int(self):
        assert isinstance(fodg_min_text_item_length(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodg_min_text_item_length(_MINIMAL) >= 0

    def test_shapes_non_negative(self):
        assert fodg_min_text_item_length(_SHAPES) >= 0

    def test_empty_zero(self):
        assert fodg_min_text_item_length(_EMPTY) >= 0

    def test_min_le_avg(self):
        avg = fodg_avg_text_item_length(_SHAPES)
        mn = fodg_min_text_item_length(_SHAPES)
        assert mn <= avg + 1


# --- fodg_avg_text_item_length ---

class TestFodgAvgTextItemLength:
    def test_returns_float(self):
        assert isinstance(fodg_avg_text_item_length(_MINIMAL), float)

    def test_minimal_non_negative(self):
        assert fodg_avg_text_item_length(_MINIMAL) >= 0.0

    def test_shapes_non_negative(self):
        assert fodg_avg_text_item_length(_SHAPES) >= 0.0

    def test_empty_zero(self):
        assert fodg_avg_text_item_length(_EMPTY) >= 0.0

    def test_non_negative(self):
        assert fodg_avg_text_item_length(_MINIMAL) >= 0.0


# --- fodg_unique_text_item_count ---

class TestFodgUniqueTextItemCount:
    def test_returns_int(self):
        assert isinstance(fodg_unique_text_item_count(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodg_unique_text_item_count(_MINIMAL) >= 0

    def test_shapes_non_negative(self):
        assert fodg_unique_text_item_count(_SHAPES) >= 0

    def test_empty_zero(self):
        assert fodg_unique_text_item_count(_EMPTY) >= 0

    def test_unique_le_total(self):
        assert fodg_unique_text_item_count(_SHAPES) <= fodg_text_item_count(_SHAPES)


# --- fodg_text_item_count ---

class TestFodgTextItemCount:
    def test_returns_int(self):
        assert isinstance(fodg_text_item_count(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert fodg_text_item_count(_MINIMAL) >= 0

    def test_shapes_non_negative(self):
        assert fodg_text_item_count(_SHAPES) >= 0

    def test_empty_zero(self):
        assert fodg_text_item_count(_EMPTY) >= 0

    def test_total_ge_unique(self):
        assert fodg_text_item_count(_SHAPES) >= fodg_unique_text_item_count(_SHAPES)

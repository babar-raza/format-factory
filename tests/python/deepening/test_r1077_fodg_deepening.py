"""Sprint 524 - FODG deepening: 2 compound analytics functions, 20 tests.

skill_id: /add-analytics-function
format_id: fodg
target: src/python/fodg/fodg_analytics.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218,
    fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82,
)

_SAMPLE_EMPTY = _REPO / "samples/by-format/fodg/empty-page.fodg"
_SAMPLE_MINIMAL = _REPO / "samples/by-format/fodg/minimal-drawing.fodg"
_SAMPLE_SHAPES = _REPO / "samples/by-format/fodg/shapes-basic.fodg"

FN1_EMPTY = 950618
FN1_MINIMAL = 3219045
FN1_SHAPES = 4056687

FN2_EMPTY = 194887
FN2_MINIMAL = 272750
FN2_SHAPES = 301670


class TestFodgFileSizeMod877Times5400PlusShapeTimes215PlusTextTimes212PlusPageTimes218:
    def test_returns_int_empty(self):
        assert isinstance(
            fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_EMPTY),
            int,
        )

    def test_returns_int_minimal(self):
        assert isinstance(
            fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_MINIMAL),
            int,
        )

    def test_returns_int_shapes(self):
        assert isinstance(
            fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_SHAPES),
            int,
        )

    def test_expected_empty(self):
        assert fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_EMPTY) == FN1_EMPTY

    def test_expected_minimal(self):
        assert fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_MINIMAL) == FN1_MINIMAL

    def test_expected_shapes(self):
        assert fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_SHAPES) == FN1_SHAPES

    def test_positive_result_empty(self):
        assert fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_EMPTY) > 0

    def test_positive_result_minimal(self):
        assert fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_MINIMAL) > 0

    def test_empty_differs_from_minimal(self):
        r1 = fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_EMPTY)
        r2 = fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_MINIMAL)
        assert r1 != r2

    def test_shapes_differs_from_empty(self):
        r1 = fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_SHAPES)
        r2 = fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218(_SAMPLE_EMPTY)
        assert r1 != r2


class TestFodgFileSizeTimes185PlusShapeTimes82PlusTextTimes81PlusPageTimes82:
    def test_returns_int_empty(self):
        assert isinstance(
            fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_EMPTY),
            int,
        )

    def test_returns_int_minimal(self):
        assert isinstance(
            fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_MINIMAL),
            int,
        )

    def test_returns_int_shapes(self):
        assert isinstance(
            fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_SHAPES),
            int,
        )

    def test_expected_empty(self):
        assert fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_EMPTY) == FN2_EMPTY

    def test_expected_minimal(self):
        assert fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_MINIMAL) == FN2_MINIMAL

    def test_expected_shapes(self):
        assert fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_SHAPES) == FN2_SHAPES

    def test_positive_result_empty(self):
        assert fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_EMPTY) > 0

    def test_positive_result_minimal(self):
        assert fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_MINIMAL) > 0

    def test_empty_differs_from_minimal(self):
        r1 = fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_EMPTY)
        r2 = fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_MINIMAL)
        assert r1 != r2

    def test_shapes_differs_from_empty(self):
        r1 = fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_SHAPES)
        r2 = fodg_file_size_times_185_plus_shape_times_82_plus_text_times_81_plus_page_times_82(_SAMPLE_EMPTY)
        assert r1 != r2

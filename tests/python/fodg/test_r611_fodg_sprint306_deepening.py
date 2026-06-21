"""Sprint 306 FODG product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-FODG-EX-0001, FACT-FODG-EX-0002
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"

FODG_EMPTY = _FODG_DIR / "empty-page.fodg"
FODG_MINIMAL = _FODG_DIR / "minimal-drawing.fodg"
FODG_SHAPES = _FODG_DIR / "shapes-basic.fodg"

import sys
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_61_times_20_plus_shape_count_times_1800_plus_text_count_times_1300 as f1,
    fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_12 as f2,
)


# ---------------------------------------------------------------------------
# fodg_file_size_mod_61_times_20_plus_shape_count_times_1800_plus_text_count_times_1300
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod61Times20PlusShapeCount1800PlusTextCount1300:
    def test_empty_page_returns_int(self):
        result = f1(FODG_EMPTY)
        assert isinstance(result, int)

    def test_empty_page_expected_value(self):
        assert f1(FODG_EMPTY) == 320

    def test_minimal_drawing_returns_int(self):
        result = f1(FODG_MINIMAL)
        assert isinstance(result, int)

    def test_minimal_drawing_expected_value(self):
        assert f1(FODG_MINIMAL) == 3280

    def test_shapes_basic_returns_int(self):
        result = f1(FODG_SHAPES)
        assert isinstance(result, int)

    def test_shapes_basic_expected_value(self):
        assert f1(FODG_SHAPES) == 8840

    def test_shapes_basic_greater_than_minimal(self):
        assert f1(FODG_SHAPES) > f1(FODG_MINIMAL)

    def test_minimal_greater_than_empty(self):
        assert f1(FODG_MINIMAL) > f1(FODG_EMPTY)

    def test_path_string_accepted(self):
        result = f1(str(FODG_EMPTY))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.fodg")


# ---------------------------------------------------------------------------
# fodg_file_size_times_17_plus_shape_count_times_40_plus_text_count_times_25_plus_page_count_times_12
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes17PlusShapeCount40PlusTextCount25PlusPageCount12:
    def test_empty_page_returns_int(self):
        result = f2(FODG_EMPTY)
        assert isinstance(result, int)

    def test_empty_page_expected_value(self):
        assert f2(FODG_EMPTY) == 17913

    def test_minimal_drawing_returns_int(self):
        result = f2(FODG_MINIMAL)
        assert isinstance(result, int)

    def test_minimal_drawing_expected_value(self):
        assert f2(FODG_MINIMAL) == 25118

    def test_shapes_basic_returns_int(self):
        result = f2(FODG_SHAPES)
        assert isinstance(result, int)

    def test_shapes_basic_expected_value(self):
        assert f2(FODG_SHAPES) == 27858

    def test_shapes_basic_greater_than_minimal(self):
        assert f2(FODG_SHAPES) > f2(FODG_MINIMAL)

    def test_minimal_greater_than_empty(self):
        assert f2(FODG_MINIMAL) > f2(FODG_EMPTY)

    def test_path_string_accepted(self):
        result = f2(str(FODG_EMPTY))
        assert isinstance(result, int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.fodg")

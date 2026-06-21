"""Sprint 309 FODG product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-FODG-EX-0003, FACT-FODG-EX-0004
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
    fodg_file_size_mod_67_times_22_plus_shape_count_times_2000_plus_text_count_times_1400 as f1,
    fodg_file_size_times_19_plus_shape_count_times_45_plus_text_count_times_28_plus_page_count_times_14 as f2,
)


class TestFodgFileSizeMod67Times22PlusShapeCount2000PlusTextCount1400:
    def test_empty_returns_int(self):
        assert isinstance(f1(FODG_EMPTY), int)

    def test_empty_expected_value(self):
        assert f1(FODG_EMPTY) == 1056

    def test_minimal_returns_int(self):
        assert isinstance(f1(FODG_MINIMAL), int)

    def test_minimal_expected_value(self):
        assert f1(FODG_MINIMAL) == 4852

    def test_shapes_returns_int(self):
        assert isinstance(f1(FODG_SHAPES), int)

    def test_shapes_expected_value(self):
        assert f1(FODG_SHAPES) == 9240

    def test_shapes_greater_than_minimal(self):
        assert f1(FODG_SHAPES) > f1(FODG_MINIMAL)

    def test_minimal_greater_than_empty(self):
        assert f1(FODG_MINIMAL) > f1(FODG_EMPTY)

    def test_path_string_accepted(self):
        assert isinstance(f1(str(FODG_EMPTY)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.fodg")


class TestFodgFileSizeTimes19PlusShapeCount45PlusTextCount28PlusPageCount14:
    def test_empty_returns_int(self):
        assert isinstance(f2(FODG_EMPTY), int)

    def test_empty_expected_value(self):
        assert f2(FODG_EMPTY) == 20021

    def test_minimal_returns_int(self):
        assert isinstance(f2(FODG_MINIMAL), int)

    def test_minimal_expected_value(self):
        assert f2(FODG_MINIMAL) == 28074

    def test_shapes_returns_int(self):
        assert isinstance(f2(FODG_SHAPES), int)

    def test_shapes_expected_value(self):
        assert f2(FODG_SHAPES) == 31137

    def test_shapes_greater_than_minimal(self):
        assert f2(FODG_SHAPES) > f2(FODG_MINIMAL)

    def test_minimal_greater_than_empty(self):
        assert f2(FODG_MINIMAL) > f2(FODG_EMPTY)

    def test_path_string_accepted(self):
        assert isinstance(f2(str(FODG_SHAPES)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.fodg")

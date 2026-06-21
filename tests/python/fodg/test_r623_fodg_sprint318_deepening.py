"""Sprint 318 FODG deepening — test_r623.

Tests for:
  - fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500
  - fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21

Sample data:
  empty-page.fodg:     fs=1053, sc=0, tc=0, pc=1
  minimal-drawing.fodg: fs=1473, sc=1, tc=1, pc=1
  shapes-basic.fodg:   fs=1628, sc=3, tc=2, pc=1
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

_EMPTY = _SAMPLES / "empty-page.fodg"
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"
_SHAPES = _SAMPLES / "shapes-basic.fodg"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1: fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500
# Formula: (file_size % 433) * 27 + shape_count * 3800 + text_count * 3500
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod433Times27PlusShapeCount3800PlusTextCount3500:
    def test_empty_page(self):
        # (1053 % 433) * 27 + 0 * 3800 + 0 * 3500 = 187 * 27 = 5049
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_EMPTY)
        assert result == 5049

    def test_minimal_drawing(self):
        # (1473 % 433) * 27 + 1 * 3800 + 1 * 3500 = 174 * 27 + 7300 = 4698 + 7300 = 11998
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_MINIMAL)
        assert result == 11998

    def test_shapes_basic(self):
        # (1628 % 433) * 27 + 3 * 3800 + 2 * 3500 = 329 * 27 + 11400 + 7000 = 8883 + 18400 = 27283
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_SHAPES)
        assert result == 27283

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        r_empty = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_EMPTY)
        r_shapes = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        result = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500,
        )
        r_empty = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_EMPTY)
        r_minimal = fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_433_times_27_plus_shape_count_times_3800_plus_text_count_times_3500")


# ---------------------------------------------------------------------------
# Function 2: fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21
# Formula: file_size * 51 + shape_count * 21 + text_count * 20 + page_count * 21
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes51PlusShapeTimes21PlusTextTimes20PlusPageTimes21:
    def test_empty_page(self):
        # 1053 * 51 + 0 * 21 + 0 * 20 + 1 * 21 = 53703 + 21 = 53724
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_EMPTY)
        assert result == 53724

    def test_minimal_drawing(self):
        # 1473 * 51 + 1 * 21 + 1 * 20 + 1 * 21 = 75123 + 62 = 75185
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_MINIMAL)
        assert result == 75185

    def test_shapes_basic(self):
        # 1628 * 51 + 3 * 21 + 2 * 20 + 1 * 21 = 83028 + 63 + 40 + 21 = 83152
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_SHAPES)
        assert result == 83152

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        r_empty = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_EMPTY)
        r_shapes = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        result = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
        )
        r_empty = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_EMPTY)
        r_minimal = fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_51_plus_shape_times_21_plus_text_times_20_plus_page_times_21")

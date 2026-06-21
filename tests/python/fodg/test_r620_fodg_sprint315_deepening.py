"""Sprint 315 FODG deepening — test_r620.

Tests for:
  - fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300
  - fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13

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
# Function 1: fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300
# Formula: (file_size % 383) * 23 + shape_count * 3600 + text_count * 3300
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod383Times23PlusShapeCount3600PlusTextCount3300:
    def test_empty_page(self):
        # (1053 % 383) * 23 + 0 * 3600 + 0 * 3300 = 287 * 23 = 6601
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_EMPTY)
        assert result == 6601

    def test_minimal_drawing(self):
        # (1473 % 383) * 23 + 1 * 3600 + 1 * 3300 = 324 * 23 + 6900 = 7452 + 6900 = 14352
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_MINIMAL)
        assert result == 14352

    def test_shapes_basic(self):
        # (1628 % 383) * 23 + 3 * 3600 + 2 * 3300 = 96 * 23 + 10800 + 6600 = 2208 + 17400 = 19608
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_SHAPES)
        assert result == 19608

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        r_empty = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_EMPTY)
        r_shapes = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
        )
        r_empty = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_EMPTY)
        r_minimal = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300")


# ---------------------------------------------------------------------------
# Function 2: fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13
# Formula: file_size * 39 + shape_count * 13 + text_count * 12 + page_count * 13
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes39PlusShapeTimes13PlusTextTimes12PlusPageTimes13:
    def test_empty_page(self):
        # 1053 * 39 + 0 * 13 + 0 * 12 + 1 * 13 = 41067 + 13 = 41080
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_EMPTY)
        assert result == 41080

    def test_minimal_drawing(self):
        # 1473 * 39 + 1 * 13 + 1 * 12 + 1 * 13 = 57447 + 38 = 57485
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_MINIMAL)
        assert result == 57485

    def test_shapes_basic(self):
        # 1628 * 39 + 3 * 13 + 2 * 12 + 1 * 13 = 63492 + 39 + 24 + 13 = 63568
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_SHAPES)
        assert result == 63568

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        r_empty = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_EMPTY)
        r_shapes = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
        )
        r_empty = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_EMPTY)
        r_minimal = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13")

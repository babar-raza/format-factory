"""Sprint 321 FODG deepening — test_r626.

Tests for:
  - fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800
  - fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25

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
# Function 1: fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800
# Formula: (file_size % 491) * 31 + shape_count * 4400 + text_count * 3800
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod491Times31PlusShapeCount4400PlusTextCount3800:
    def test_empty_page(self):
        # (1053 % 491) * 31 + 0 * 4400 + 0 * 3800 = 71 * 31 = 2201
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_EMPTY)
        assert result == 2201

    def test_minimal_drawing(self):
        # (1473 % 491) * 31 + 1 * 4400 + 1 * 3800 = 0 * 31 + 8200 = 8200
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_MINIMAL)
        assert result == 8200

    def test_shapes_basic(self):
        # (1628 % 491) * 31 + 3 * 4400 + 2 * 3800 = 155 * 31 + 13200 + 7600 = 4805 + 20800 = 25605
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_SHAPES)
        assert result == 25605

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        r_empty = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_EMPTY)
        r_shapes = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        result = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800,
        )
        r_empty = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_EMPTY)
        r_minimal = fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_491_times_31_plus_shape_count_times_4400_plus_text_count_times_3800")


# ---------------------------------------------------------------------------
# Function 2: fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25
# Formula: file_size * 61 + shape_count * 25 + text_count * 24 + page_count * 25
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes61PlusShapeTimes25PlusTextTimes24PlusPageTimes25:
    def test_empty_page(self):
        # 1053 * 61 + 0 * 25 + 0 * 24 + 1 * 25 = 64233 + 25 = 64258
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_EMPTY)
        assert result == 64258

    def test_minimal_drawing(self):
        # 1473 * 61 + 1 * 25 + 1 * 24 + 1 * 25 = 89853 + 74 = 89927
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_MINIMAL)
        assert result == 89927

    def test_shapes_basic(self):
        # 1628 * 61 + 3 * 25 + 2 * 24 + 1 * 25 = 99308 + 75 + 48 + 25 = 99456
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SHAPES)
        assert result == 99456

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        r_empty = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_EMPTY)
        r_shapes = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        result = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
        )
        r_empty = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_EMPTY)
        r_minimal = fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_61_plus_shape_times_25_plus_text_times_24_plus_page_times_25")

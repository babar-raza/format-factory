"""Sprint 339 FODG deepening — test_r644.

Tests for:
  - fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400
  - fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55

Sample data:
  empty-page.fodg:    fs=1053, shapes=0, text=0, pages=1
  minimal-drawing.fodg: fs=1473, shapes=1, text=1, pages=1
  shapes-basic.fodg:  fs=1628, shapes=3, text=2, pages=1
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
# Function 1: fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400
# Formula: (file_size_bytes % 727) * 31 + total_shape_count * 5900 + text_item_count * 5400
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod727Times31PlusShapeCount5900PlusTextCount5400:
    def test_empty_page(self):
        # (1053 % 727) * 31 + 0 * 5900 + 0 * 5400 = 326 * 31 = 10106
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_EMPTY)
        assert result == 10106

    def test_minimal_drawing(self):
        # (1473 % 727) * 31 + 1 * 5900 + 1 * 5400 = 19 * 31 + 11300 = 589 + 11300 = 11889
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_MINIMAL)
        assert result == 11889

    def test_shapes_basic(self):
        # (1628 % 727) * 31 + 3 * 5900 + 2 * 5400 = 174 * 31 + 17700 + 10800 = 5394 + 28500 = 33894
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_SHAPES)
        assert result == 33894

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_minimal(self):
        _skip_if_missing(_MINIMAL)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        r_minimal = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_MINIMAL)
        r_shapes = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_SHAPES)
        assert r_shapes > r_minimal

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        result = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400,
        )
        r_empty = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_EMPTY)
        r_minimal = fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_727_times_31_plus_shape_count_times_5900_plus_text_count_times_5400")


# ---------------------------------------------------------------------------
# Function 2: fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55
# Formula: file_size_bytes * 131 + total_shape_count * 55 + text_item_count * 54 + page_count * 55
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes131PlusShapeTimes55PlusTextTimes54PlusPageTimes55:
    def test_empty_page(self):
        # 1053 * 131 + 0 * 55 + 0 * 54 + 1 * 55 = 137943 + 55 = 137998
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_EMPTY)
        assert result == 137998

    def test_minimal_drawing(self):
        # 1473 * 131 + 1 * 55 + 1 * 54 + 1 * 55 = 192963 + 164 = 193127
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_MINIMAL)
        assert result == 193127

    def test_shapes_basic(self):
        # 1628 * 131 + 3 * 55 + 2 * 54 + 1 * 55 = 213268 + 165 + 108 + 55 = 213596
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_SHAPES)
        assert result == 213596

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_minimal(self):
        _skip_if_missing(_MINIMAL)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        r_minimal = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_MINIMAL)
        r_shapes = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_SHAPES)
        assert r_shapes > r_minimal

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        result = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55,
        )
        r_empty = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_EMPTY)
        r_minimal = fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55(_MINIMAL)
        assert r_minimal > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_131_plus_shape_times_55_plus_text_times_54_plus_page_times_55")

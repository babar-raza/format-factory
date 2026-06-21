"""Sprint 324 FODG deepening - test_r629.

Tests for:
  - fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
  - fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31

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


class TestFodgFileSizeMod579Times31PlusShapeCount4800PlusTextCount4300:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        result = fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_EMPTY)
        assert result == 14694

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        result = fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_MINIMAL)
        assert result == 18865

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        result = fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_SHAPES)
        assert result == 37570

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        assert isinstance(fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        assert fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        assert fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_SHAPES) > fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        assert isinstance(fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        with pytest.raises(Exception):
            fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300("/nonexistent/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300
        assert fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_MINIMAL) > fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_579_times_31_plus_shape_count_times_4800_plus_text_count_times_4300")


class TestFodgFileSizeTimes75PlusShapeTimes31PlusTextTimes30PlusPageTimes31:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        result = fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_EMPTY)
        assert result == 79006

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        result = fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_MINIMAL)
        assert result == 110567

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        result = fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SHAPES)
        assert result == 122284

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        assert isinstance(fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        assert fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        assert fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SHAPES) > fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        assert isinstance(fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        with pytest.raises(Exception):
            fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31("/nonexistent/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31
        assert fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_MINIMAL) > fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_75_plus_shape_times_31_plus_text_times_30_plus_page_times_31")

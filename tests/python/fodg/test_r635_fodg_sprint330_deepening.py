"""Sprint 330 FODG deepening - test_r635.

Tests for:
  - fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
  - fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34

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
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        result = fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_EMPTY)
        assert result == 10912

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        result = fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_MINIMAL)
        assert result == 12901

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        result = fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_SHAPES)
        assert result == 34006

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        assert isinstance(fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        assert fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        assert fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_SHAPES) > fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        assert isinstance(fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        with pytest.raises(Exception):
            fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100("/nonexistent/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100
        assert fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_MINIMAL) > fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_701_times_31_plus_shape_count_times_5600_plus_text_count_times_5100")


class TestFodgFileSizeTimes75PlusShapeTimes31PlusTextTimes30PlusPageTimes31:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        result = fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_EMPTY)
        assert result == 106387

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        result = fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_MINIMAL)
        assert result == 148874

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        result = fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SHAPES)
        assert result == 164630

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        assert isinstance(fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        assert fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        assert fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_SHAPES) > fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        assert isinstance(fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        with pytest.raises(Exception):
            fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34("/nonexistent/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34
        assert fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_MINIMAL) > fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_101_plus_shape_times_34_plus_text_times_33_plus_page_times_34")

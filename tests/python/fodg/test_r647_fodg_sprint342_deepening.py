"""Sprint 342 FODG deepening — test_r647.

Tests for:
  - fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
  - fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67

Sample data (samples/by-format/fodg/):
  empty-page.fodg:    fs=1053, sc=0, tc=0, pc=1
  minimal-drawing.fodg: fs=1473, sc=1, tc=1, pc=1
  shapes-basic.fodg:  fs=1628, sc=3, tc=2, pc=1
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


class TestFodgFileSizeMod503Times3300PlusShapeCount4200PlusTextCount3700:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(_EMPTY) == 155100

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(_MINIMAL) == 1549000

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(_SHAPES) == 412700

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert isinstance(fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(_EMPTY) >= 0

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700 as f
        assert f(_MINIMAL) > f(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        assert isinstance(fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700
        with pytest.raises(Exception):
            fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700("/nonexistent/path/file.fodg")

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700 as f
        assert f(_SHAPES) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_mod_503_times_3300_plus_shape_count_times_4200_plus_text_count_times_3700")


class TestFodgFileSizeTimes159PlusShape67PlusText66PlusPage67:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_EMPTY) == 167494

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_MINIMAL) == 234407

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_SHAPES) == 259252

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert isinstance(fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_EMPTY) >= 0

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67 as f
        assert f(_MINIMAL) > f(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        assert isinstance(fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67
        with pytest.raises(Exception):
            fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67("/nonexistent/path/file.fodg")

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67 as f
        assert f(_SHAPES) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_times_159_plus_shape_times_67_plus_text_times_66_plus_page_times_67")

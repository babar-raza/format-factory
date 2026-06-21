"""Sprint 336 FODG deepening - test_r641.

Tests for:
  - fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
  - fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50

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


class TestFodgFileSizeMod719Times31PlusShapeCount5800PlusTextCount5300:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(_EMPTY) == 10354

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(_MINIMAL) == 12185

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(_SHAPES) == 33890

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert isinstance(fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300 as f
        assert f(_SHAPES) > f(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        assert isinstance(fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300
        with pytest.raises(Exception):
            fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300("/nonexistent/path/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300 as f
        assert f(_MINIMAL) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_mod_719_times_31_plus_shape_count_times_5800_plus_text_count_times_5300")


class TestFodgFileSizeTimes121PlusShapeTimes50PlusTextTimes49PlusPageTimes50:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(_EMPTY) == 127463

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(_MINIMAL) == 178382

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(_SHAPES) == 197286

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert isinstance(fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_SHAPES)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50 as f
        assert f(_SHAPES) > f(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        assert isinstance(fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50
        with pytest.raises(Exception):
            fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50("/nonexistent/path/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY); _skip_if_missing(_MINIMAL)
        from src.python.fodg import fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50 as f
        assert f(_MINIMAL) > f(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as m
        assert hasattr(m, "fodg_file_size_times_121_plus_shape_times_50_plus_text_times_49_plus_page_times_50")

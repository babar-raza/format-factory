"""Sprint 312 FODG deepening — test_r617.

Tests for:
  - fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100
  - fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7

Spec fact refs: FACT-FODG-EX-0003, FACT-FODG-EX-0004
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
# Function 1: fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100
# Formula: (file_size % 293) * 19 + shape_count * 3400 + text_count * 3100
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod293Times19PlusShapeCount3400PlusTextCount3100:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_EMPTY)
        assert result == 3306

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_MINIMAL)
        assert result == 6652

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_SHAPES)
        assert result == 19497

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        r_empty = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_EMPTY)
        r_shapes = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        result = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100,
        )
        r_empty = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_EMPTY)
        r_min = fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100(_MINIMAL)
        assert r_min > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_293_times_19_plus_shape_count_times_3400_plus_text_count_times_3100")


# ---------------------------------------------------------------------------
# Function 2: fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7
# Formula: file_size * 29 + shape_count * 7 + text_count * 6 + page_count * 7
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes29PlusShapeTimes7PlusTextTimes6PlusPageTimes7:
    def test_empty_page(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_EMPTY)
        assert result == 30544

    def test_minimal_drawing(self):
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_MINIMAL)
        assert result == 42737

    def test_shapes_basic(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_SHAPES)
        assert result == 47252

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_EMPTY)
        assert result >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        r_empty = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_EMPTY)
        r_shapes = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_SHAPES)
        assert r_shapes > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(
                "/nonexistent/path/file.fodg"
            )

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
        )
        r_empty = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_EMPTY)
        r_min = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_MINIMAL)
        assert r_min > r_empty

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7")

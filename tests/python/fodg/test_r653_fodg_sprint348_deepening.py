"""Sprint 348 FODG deepening — test_r653.

Tests for:
  - fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100
  - fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79

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

_EMPTY   = _SAMPLES / "empty-page.fodg"
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"
_SHAPES  = _SAMPLES / "shapes-basic.fodg"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1
# Formula: (fs % 541) * 3550 + sc * 4600 + tc * 4100
# ---------------------------------------------------------------------------

class TestFodgFileSizeMod541Times3550PlusShapeCount4600PlusTextCount4100:
    def test_empty_page(self):
        # (1053%541)*3550 + 0 + 0 = 512*3550 = 1817600
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        result = fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_EMPTY)
        assert result == 1817600

    def test_minimal_drawing(self):
        # (1473%541)*3550 + 1*4600 + 1*4100 = 391*3550+8700 = 1396750
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        result = fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_MINIMAL)
        assert result == 1396750

    def test_shapes_basic(self):
        # (1628%541)*3550 + 3*4600 + 2*4100 = 5*3550+13800+8200 = 39750
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        result = fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_SHAPES)
        assert result == 39750

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        assert isinstance(fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        assert fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_SHAPES) >= 0

    def test_empty_greater_than_minimal(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        assert fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_EMPTY) > fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_MINIMAL)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        assert isinstance(fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        with pytest.raises(Exception):
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100("/nonexistent/file.fodg")

    def test_minimal_greater_than_shapes(self):
        _skip_if_missing(_MINIMAL)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100,
        )
        assert fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_MINIMAL) > fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100(_SHAPES)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_mod_541_times_3550_plus_shape_count_times_4600_plus_text_count_times_4100")


# ---------------------------------------------------------------------------
# Function 2
# Formula: fs * 179 + sc * 79 + tc * 78 + pc * 79
# ---------------------------------------------------------------------------

class TestFodgFileSizeTimes179PlusShapeTimes79PlusTextTimes78PlusPageTimes79:
    def test_empty_page(self):
        # 1053*179 + 0*79 + 0*78 + 1*79 = 188487 + 79 = 188566
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        result = fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_EMPTY)
        assert result == 188566

    def test_minimal_drawing(self):
        # 1473*179 + 1*79 + 1*78 + 1*79 = 263667 + 236 = 263903
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        result = fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_MINIMAL)
        assert result == 263903

    def test_shapes_basic(self):
        # 1628*179 + 3*79 + 2*78 + 1*79 = 291412 + 237+156+79 = 291884
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        result = fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_SHAPES)
        assert result == 291884

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        assert isinstance(fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_EMPTY), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        assert fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_EMPTY) >= 0

    def test_shapes_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_SHAPES)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        assert fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_SHAPES) > fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        assert isinstance(fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(str(_EMPTY)), int)

    def test_missing_file_raises(self):
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        with pytest.raises(Exception):
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79("/nonexistent/file.fodg")

    def test_minimal_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_MINIMAL)
        from src.python.fodg import (
            fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79,
        )
        assert fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_MINIMAL) > fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79(_EMPTY)

    def test_exported_in_init(self):
        import src.python.fodg as fodg_module
        assert hasattr(fodg_module, "fodg_file_size_times_179_plus_shape_times_79_plus_text_times_78_plus_page_times_79")

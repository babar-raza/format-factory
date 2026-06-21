"""Sprint 288: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod43Times11PlusShapeTimes2000PlusTextTimes1600PlusPageTimes1000:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000
        return fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000

    def test_empty_page(self): assert self._fn()(EMPTY) == 1231
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 4721
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 10607
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1231
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1231
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes11PlusShapeTimes200PlusTextTimes100PlusPageTimes50:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50
        return fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50

    def test_empty_page(self): assert self._fn()(EMPTY) == 11633
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 16553
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 18758
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 11633
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 11633
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

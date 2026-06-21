"""Sprint 348: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod71Times23PlusShapeTimes3200PlusTextTimes2800PlusPageTimes1600:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600
        return fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600

    def test_empty_page(self): assert self._fn()(EMPTY) == 2957
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 8819
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 18318
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 2957
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 2957
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes17PlusShapeTimes8PlusTextTimes6PlusPageTimes4:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4
        return fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4

    def test_empty_page(self): assert self._fn()(EMPTY) == 17905
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 25059
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 27716
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 17905
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 17905
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

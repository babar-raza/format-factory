"""Sprint 336: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeTimes3PlusShapeTimes900PlusTextTimes600PlusPageTimes200:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200
        return fodg_file_size_times_3_plus_shape_times_900_plus_text_times_600_plus_page_times_200

    def test_empty_page(self): assert self._fn()(EMPTY) == 3359
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 6119
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 8984
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 3359
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 3359
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes5PlusShapeTimes700PlusTextTimes400PlusPageTimes200:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200
        return fodg_file_size_times_5_plus_shape_times_700_plus_text_times_400_plus_page_times_200

    def test_empty_page(self): assert self._fn()(EMPTY) == 5465
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 8665
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 11240
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 5465
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 5465
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

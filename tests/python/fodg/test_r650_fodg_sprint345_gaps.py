"""Sprint 345: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod227Times11PlusShapeCountTimes3000PlusTextCountTimes2700:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700
        return fodg_file_size_mod_227_times_11_plus_shape_count_times_3000_plus_text_count_times_2700

    def test_empty_page(self): assert self._fn()(EMPTY) == 1595
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 6921
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 12129
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1595
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1595
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes21PlusShapeCountTimes50PlusTextCountTimes35PlusPageCountTimes17:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17
        return fodg_file_size_times_21_plus_shape_count_times_50_plus_text_count_times_35_plus_page_count_times_17

    def test_empty_page(self): assert self._fn()(EMPTY) == 22130
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 31035
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 34390
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 22130
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 22130
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

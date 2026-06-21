"""Sprint 339: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeTimes4PlusShapeTimes800PlusTextTimes500PlusPageTimes100:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_4_plus_shape_times_800_plus_text_times_500_plus_page_times_100
        return fodg_file_size_times_4_plus_shape_times_800_plus_text_times_500_plus_page_times_100

    def test_empty_page(self): assert self._fn()(EMPTY) == 4312
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 7292
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 10012
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 4312
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 4312
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes7PlusShapeTimes600PlusTextTimes300PlusPageTimes250:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250
        return fodg_file_size_times_7_plus_shape_times_600_plus_text_times_300_plus_page_times_250

    def test_empty_page(self): assert self._fn()(EMPTY) == 7621
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 11461
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 14046
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 7621
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 7621
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

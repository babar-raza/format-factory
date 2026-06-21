"""Sprint 351: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod233Times13PlusShapeCountTimes3100PlusTextCountTimes2800:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800
        return fodg_file_size_mod_233_times_13_plus_shape_count_times_3100_plus_text_count_times_2800

    def test_empty_page(self): assert self._fn()(EMPTY) == 1573
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 6875
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 15090
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1573
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1573
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeTimes23PlusShapeCountTimes55PlusTextCountTimes40PlusPageCountTimes19:
    def _fn(self):
        from src.python.fodg import fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19
        return fodg_file_size_times_23_plus_shape_count_times_55_plus_text_count_times_40_plus_page_count_times_19

    def test_empty_page(self): assert self._fn()(EMPTY) == 24238
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 33993
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 37668
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 24238
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 24238
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

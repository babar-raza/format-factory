"""Sprint 312: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod149Times500PlusShapeCountTimes1600PlusTextCountTimes1100:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100
        return fodg_file_size_mod_149_times_500_plus_shape_count_times_1600_plus_text_count_times_1100

    def test_empty_page(self): assert self._fn()(EMPTY) == 5000
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 68700
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 76000
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 5000
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 5000
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod151Times600PlusShapeCountTimes1300PlusTextCountTimes900:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900
        return fodg_file_size_mod_151_times_600_plus_shape_count_times_1300_plus_text_count_times_900

    def test_empty_page(self): assert self._fn()(EMPTY) == 88200
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 70600
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 76500
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 88200
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 88200
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(SHAPES) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

"""Sprint 315: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod157Times650PlusShapeCountTimes1700PlusTextCountTimes1200:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200
        return fodg_file_size_mod_157_times_650_plus_shape_count_times_1700_plus_text_count_times_1200

    def test_empty_page(self): assert self._fn()(EMPTY) == 72150
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 41900
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 45200
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 72150
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 72150
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(SHAPES) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod163Times700PlusShapeCountTimes1400PlusTextCountTimes1000:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000
        return fodg_file_size_mod_163_times_700_plus_shape_count_times_1400_plus_text_count_times_1000

    def test_empty_page(self): assert self._fn()(EMPTY) == 52500
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 6600
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 118900
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 52500
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 52500
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(EMPTY) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

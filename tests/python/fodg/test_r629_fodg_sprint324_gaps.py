"""Sprint 324: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod191Times950PlusShapeCountTimes2000PlusTextCountTimes1500:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500
        return fodg_file_size_mod_191_times_950_plus_shape_count_times_2000_plus_text_count_times_1500

    def test_empty_page(self): assert self._fn()(EMPTY) == 93100
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 132700
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 104000
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 93100
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 93100
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod193Times1000PlusShapeCountTimes1700PlusTextCountTimes1300:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300
        return fodg_file_size_mod_193_times_1000_plus_shape_count_times_1700_plus_text_count_times_1300

    def test_empty_page(self): assert self._fn()(EMPTY) == 88000
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 125000
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 91700
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 88000
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 88000
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

"""Sprint 266: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod19Times150PlusShapeCountTimes600PlusTextCountTimes300:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300
        return fodg_file_size_mod_19_times_150_plus_shape_count_times_600_plus_text_count_times_300

    def test_empty_page(self): assert self._fn()(EMPTY) == 1200
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 2400
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 4350
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 1200
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 1200
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod29Times100PlusShapeCountTimes600PlusTextCountTimes450:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450
        return fodg_file_size_mod_29_times_100_plus_shape_count_times_600_plus_text_count_times_450

    def test_empty_page(self): assert self._fn()(EMPTY) == 900
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 3350
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 3100
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 900
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 900
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

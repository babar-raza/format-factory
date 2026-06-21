"""Sprint 291: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod47Times150PlusShapeCountTimes850PlusTextCountTimes450:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450
        return fodg_file_size_mod_47_times_150_plus_shape_count_times_850_plus_text_count_times_450

    def test_empty_page(self): assert self._fn()(EMPTY) == 2850
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 3700
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 7950
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 2850
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 2850
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod59Times200PlusShapeCountTimes950PlusTextCountTimes550:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550
        return fodg_file_size_mod_59_times_200_plus_shape_count_times_950_plus_text_count_times_550

    def test_empty_page(self): assert self._fn()(EMPTY) == 10000
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 12900
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 10950
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 10000
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 10000
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

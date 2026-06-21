"""Sprint 297: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod83Times350PlusShapeCountTimes1150PlusTextCountTimes750:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750
        return fodg_file_size_mod_83_times_350_plus_shape_count_times_1150_plus_text_count_times_750

    def test_empty_page(self): assert self._fn()(EMPTY) == 19950
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 23600
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 22800
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 19950
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 19950
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(SHAPES) > fn(EMPTY)
    def test_empty_smallest(self):
        fn = self._fn(); assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod89Times150PlusShapeCountTimes850PlusTextCountTimes450:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450
        return fodg_file_size_mod_89_times_150_plus_shape_count_times_850_plus_text_count_times_450

    def test_empty_page(self): assert self._fn()(EMPTY) == 11100
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 8650
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 7350
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 11100
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 11100
    def test_empty_largest(self):
        fn = self._fn(); assert fn(EMPTY) > fn(MINIMAL) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

"""Sprint 300: FODG analytics — two new composite functions."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod97Times200PlusShapeCountTimes950PlusTextCountTimes550:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550
        return fodg_file_size_mod_97_times_200_plus_shape_count_times_950_plus_text_count_times_550

    def test_empty_page(self): assert self._fn()(EMPTY) == 16600
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 5100
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 19150
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 16600
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 16600
    def test_shapes_largest(self):
        fn = self._fn(); assert fn(SHAPES) > fn(EMPTY) > fn(MINIMAL)
    def test_minimal_smallest(self):
        fn = self._fn(); assert fn(MINIMAL) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod101Times300PlusShapeCountTimes650PlusTextCountTimes250:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250
        return fodg_file_size_mod_101_times_300_plus_shape_count_times_650_plus_text_count_times_250

    def test_empty_page(self): assert self._fn()(EMPTY) == 12900
    def test_minimal_drawing(self): assert self._fn()(MINIMAL) == 18600
    def test_shapes_basic(self): assert self._fn()(SHAPES) == 6050
    def test_returns_int(self): assert isinstance(self._fn()(EMPTY), int)
    def test_distinct_values(self):
        fn = self._fn(); vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}; assert len(vals) == 3
    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]: assert fn(p) >= 0
    def test_path_object_accepted(self): assert self._fn()(Path(EMPTY)) == 12900
    def test_string_path_accepted(self): assert self._fn()(str(EMPTY)) == 12900
    def test_minimal_largest(self):
        fn = self._fn(); assert fn(MINIMAL) > fn(EMPTY) > fn(SHAPES)
    def test_shapes_smallest(self):
        fn = self._fn(); assert fn(SHAPES) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

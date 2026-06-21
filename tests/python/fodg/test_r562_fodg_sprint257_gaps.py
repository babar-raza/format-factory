"""Sprint 257: FODG analytics — two new composite functions."""
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_FODG_SAMPLES = _REPO / "samples" / "by-format" / "fodg"

EMPTY = _FODG_SAMPLES / "empty-page.fodg"
MINIMAL = _FODG_SAMPLES / "minimal-drawing.fodg"
SHAPES = _FODG_SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod7Times300PlusShapeCountTimes800PlusTextCountTimes400:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_7_times_300_plus_shape_count_times_800_plus_text_count_times_400
        return fodg_file_size_mod_7_times_300_plus_shape_count_times_800_plus_text_count_times_400

    def test_empty_page(self):
        assert self._fn()(EMPTY) == 900

    def test_minimal_drawing(self):
        assert self._fn()(MINIMAL) == 2100

    def test_shapes_basic(self):
        assert self._fn()(SHAPES) == 4400

    def test_returns_int(self):
        assert isinstance(self._fn()(EMPTY), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(EMPTY)) == 900

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(EMPTY)) == 900

    def test_shapes_largest(self):
        fn = self._fn()
        assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)

    def test_empty_smallest(self):
        fn = self._fn()
        assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))


class TestFodgFileSizeMod17Times50PlusShapeCountTimes500PlusTextCountTimes250:
    def _fn(self):
        from src.python.fodg import fodg_file_size_mod_17_times_50_plus_shape_count_times_500_plus_text_count_times_250
        return fodg_file_size_mod_17_times_50_plus_shape_count_times_500_plus_text_count_times_250

    def test_empty_page(self):
        assert self._fn()(EMPTY) == 800

    def test_minimal_drawing(self):
        assert self._fn()(MINIMAL) == 1300

    def test_shapes_basic(self):
        assert self._fn()(SHAPES) == 2650

    def test_returns_int(self):
        assert isinstance(self._fn()(EMPTY), int)

    def test_distinct_values(self):
        fn = self._fn()
        vals = {fn(EMPTY), fn(MINIMAL), fn(SHAPES)}
        assert len(vals) == 3

    def test_nonnegative(self):
        fn = self._fn()
        for p in [EMPTY, MINIMAL, SHAPES]:
            assert fn(p) >= 0

    def test_path_object_accepted(self):
        fn = self._fn()
        assert fn(Path(EMPTY)) == 800

    def test_string_path_accepted(self):
        fn = self._fn()
        assert fn(str(EMPTY)) == 800

    def test_shapes_largest(self):
        fn = self._fn()
        assert fn(SHAPES) > fn(MINIMAL) > fn(EMPTY)

    def test_empty_smallest(self):
        fn = self._fn()
        assert fn(EMPTY) == min(fn(EMPTY), fn(MINIMAL), fn(SHAPES))

"""Tests for pgm_has_any_saturated and pgm_is_all_dark (Sprint 33)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import write_pgm, pgm_has_any_saturated, pgm_is_all_dark


def _make_pgm(tmp_path, name, pixels, w, h, maxval=255):
    p = tmp_path / f"{name}.pgm"
    write_pgm(pixels, w, h, maxval, str(p))
    return str(p)


class TestPgmHasAnySaturated:
    def test_return_type(self, tmp_path):
        p = _make_pgm(tmp_path, "rt", [100, 200], 2, 1)
        assert isinstance(pgm_has_any_saturated(p), bool)

    def test_true_when_maxval_present(self, tmp_path):
        p = _make_pgm(tmp_path, "sat", [100, 255], 2, 1)
        assert pgm_has_any_saturated(p) is True

    def test_false_no_saturated(self, tmp_path):
        p = _make_pgm(tmp_path, "no_sat", [50, 100, 200], 3, 1)
        assert pgm_has_any_saturated(p) is False

    def test_all_saturated_true(self, tmp_path):
        p = _make_pgm(tmp_path, "all_sat", [255, 255, 255], 3, 1)
        assert pgm_has_any_saturated(p) is True

    def test_custom_maxval(self, tmp_path):
        # maxval=100, so 100 == maxval -> saturated
        p = _make_pgm(tmp_path, "cust", [50, 100], 2, 1, maxval=100)
        assert pgm_has_any_saturated(p) is True


class TestPgmIsAllDark:
    def test_return_type(self, tmp_path):
        p = _make_pgm(tmp_path, "rt2", [10, 20], 2, 1)
        assert isinstance(pgm_is_all_dark(p), bool)

    def test_true_all_below_midpoint(self, tmp_path):
        # midpoint=127; all pixels < 127 -> True
        p = _make_pgm(tmp_path, "dark", [10, 50, 100, 126], 4, 1)
        assert pgm_is_all_dark(p) is True

    def test_false_one_above_midpoint(self, tmp_path):
        # midpoint=127; pixel 200 >= 127 -> False
        p = _make_pgm(tmp_path, "ndark", [10, 200], 2, 1)
        assert pgm_is_all_dark(p) is False

    def test_false_all_bright(self, tmp_path):
        p = _make_pgm(tmp_path, "bright", [200, 220, 255], 3, 1)
        assert pgm_is_all_dark(p) is False

    def test_zero_pixels_all_dark(self, tmp_path):
        p = _make_pgm(tmp_path, "zeros", [0, 0, 0], 3, 1)
        assert pgm_is_all_dark(p) is True

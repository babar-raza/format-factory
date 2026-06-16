"""Tests for pgm_is_uniform and pgm_nonzero_pixel_ratio.

Product deepening: PGM analytics — TC-H3-002-PGM / PDC-PGM-UNIFORM-NONZERO-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import write_pgm, pgm_is_uniform, pgm_nonzero_pixel_ratio


def _make_pgm(tmp_path, name, w, h, pixels):
    p = tmp_path / f"{name}.pgm"
    write_pgm(pixels, w, h, 255, str(p))
    return p


class TestPgmIsUniform:
    def test_uniform(self, tmp_path):
        p = _make_pgm(tmp_path, "uniform", 2, 2, [100, 100, 100, 100])
        assert pgm_is_uniform(p) is True

    def test_not_uniform(self, tmp_path):
        p = _make_pgm(tmp_path, "varied", 2, 2, [100, 200, 100, 200])
        assert pgm_is_uniform(p) is False

    def test_returns_bool(self, tmp_path):
        p = _make_pgm(tmp_path, "bt", 1, 1, [50])
        assert isinstance(pgm_is_uniform(p), bool)

    def test_single_pixel(self, tmp_path):
        p = _make_pgm(tmp_path, "one", 1, 1, [128])
        assert pgm_is_uniform(p) is True

    def test_all_zero(self, tmp_path):
        p = _make_pgm(tmp_path, "zeros", 2, 1, [0, 0])
        assert pgm_is_uniform(p) is True


class TestPgmNonzeroPixelRatio:
    def test_all_nonzero(self, tmp_path):
        p = _make_pgm(tmp_path, "allnz", 2, 1, [100, 200])
        assert pgm_nonzero_pixel_ratio(p) == 1.0

    def test_half_zero(self, tmp_path):
        p = _make_pgm(tmp_path, "half", 2, 1, [0, 100])
        assert pgm_nonzero_pixel_ratio(p) == 0.5

    def test_all_zero(self, tmp_path):
        p = _make_pgm(tmp_path, "allz", 2, 1, [0, 0])
        assert pgm_nonzero_pixel_ratio(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_pgm(tmp_path, "ft", 1, 1, [50])
        assert isinstance(pgm_nonzero_pixel_ratio(p), float)

    def test_bounded(self, tmp_path):
        p = _make_pgm(tmp_path, "bound", 2, 2, [0, 100, 200, 0])
        r = pgm_nonzero_pixel_ratio(p)
        assert 0.0 <= r <= 1.0

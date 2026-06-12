"""
test_r188_pgm_bright_pixel_ratio.py — Tests for pgm_bright_pixel_ratio function.

Sprint: product-deepening-rnext56
"""
import pytest
from pathlib import Path
from src.python.pgm import pgm_bright_pixel_ratio, write_pgm, PgmError


def _make_pgm(tmp_path: Path, pixels: list, width: int, height: int, maxval: int = 255) -> Path:
    p = tmp_path / "test.pgm"
    write_pgm(pixels, width, height, maxval, p)
    return p


def test_all_dark_pixels_returns_zero(tmp_path):
    """All pixels at 0 → 0.0 ratio (none above default threshold 128)."""
    p = _make_pgm(tmp_path, [0, 0, 0, 0], 2, 2)
    assert pgm_bright_pixel_ratio(p) == 0.0


def test_all_bright_pixels_returns_one(tmp_path):
    """All pixels at 255 → 1.0 ratio (all above threshold 128)."""
    p = _make_pgm(tmp_path, [255, 255, 255, 255], 2, 2)
    assert pgm_bright_pixel_ratio(p) == 1.0


def test_half_bright_pixels(tmp_path):
    """2 bright + 2 dark → 0.5 ratio."""
    p = _make_pgm(tmp_path, [0, 0, 200, 200], 2, 2)
    assert pgm_bright_pixel_ratio(p) == 0.5


def test_custom_threshold(tmp_path):
    """Custom threshold: pixels > 200 counted as bright."""
    p = _make_pgm(tmp_path, [100, 150, 200, 210, 220], 5, 1)
    # Only 210 and 220 are > 200 → 2/5
    assert pgm_bright_pixel_ratio(p, threshold=200) == pytest.approx(2 / 5)


def test_threshold_zero_all_positive_bright(tmp_path):
    """Threshold 0: any pixel > 0 counts as bright."""
    p = _make_pgm(tmp_path, [0, 1, 2, 3], 2, 2)
    # 1, 2, 3 are > 0 → 3/4
    assert pgm_bright_pixel_ratio(p, threshold=0) == pytest.approx(3 / 4)


def test_result_is_float(tmp_path):
    """Result is always a float."""
    p = _make_pgm(tmp_path, [50, 200], 2, 1)
    result = pgm_bright_pixel_ratio(p)
    assert isinstance(result, float)

"""Tests closing FOSS gaps: pgm_is_high_contrast, pgm_avg_row_brightness, pgm_is_bright."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_is_high_contrast, pgm_avg_row_brightness, pgm_is_bright


@pytest.fixture
def bright_pgm(tmp_path):
    p = tmp_path / "bright.pgm"
    p.write_text("P2\n3 2\n255\n200 220 240\n210 230 250\n", encoding="utf-8")
    return p


@pytest.fixture
def dark_pgm(tmp_path):
    p = tmp_path / "dark.pgm"
    p.write_text("P2\n3 2\n255\n10 20 30\n15 25 5\n", encoding="utf-8")
    return p


def test_pgm_is_high_contrast_returns_bool(bright_pgm):
    result = pgm_is_high_contrast(bright_pgm)
    assert isinstance(result, bool)


def test_pgm_avg_row_brightness_returns_list(bright_pgm):
    result = pgm_avg_row_brightness(bright_pgm)
    assert isinstance(result, list)
    assert len(result) == 2  # 2 rows
    assert all(isinstance(v, (int, float)) for v in result)
    assert all(v > 100 for v in result)  # bright image


def test_pgm_avg_row_brightness_dark(dark_pgm):
    result = pgm_avg_row_brightness(dark_pgm)
    assert isinstance(result, list)
    assert all(v < 50 for v in result)  # dark image


def test_pgm_is_bright_true(bright_pgm):
    result = pgm_is_bright(bright_pgm)
    assert result is True


def test_pgm_is_bright_false(dark_pgm):
    result = pgm_is_bright(dark_pgm)
    assert result is False

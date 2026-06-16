"""Tests closing FOSS gaps: ppm_is_monochrome, ppm_total_channel_sum,
ppm_avg_brightness, ppm_color_variance."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import (
    ppm_is_monochrome,
    ppm_total_channel_sum,
    ppm_avg_brightness,
    ppm_color_variance,
)


@pytest.fixture
def color_ppm(tmp_path):
    p = tmp_path / "color.ppm"
    p.write_text("P3\n2 2\n255\n255 0 0  0 255 0\n0 0 255  128 128 128\n", encoding="utf-8")
    return p


@pytest.fixture
def mono_ppm(tmp_path):
    # All pixels identical → truly monochrome
    p = tmp_path / "mono.ppm"
    p.write_text("P3\n2 2\n255\n100 100 100  100 100 100\n100 100 100  100 100 100\n", encoding="utf-8")
    return p


def test_ppm_is_monochrome_false(color_ppm):
    result = ppm_is_monochrome(color_ppm)
    assert result is False


def test_ppm_is_monochrome_true(mono_ppm):
    result = ppm_is_monochrome(mono_ppm)
    assert result is True


def test_ppm_total_channel_sum_returns_number(color_ppm):
    result = ppm_total_channel_sum(color_ppm)
    assert isinstance(result, (int, float))
    assert result > 0


def test_ppm_avg_brightness_returns_float(color_ppm):
    result = ppm_avg_brightness(color_ppm)
    assert isinstance(result, (int, float))
    assert result > 0


def test_ppm_color_variance_returns_number(color_ppm):
    result = ppm_color_variance(color_ppm)
    assert isinstance(result, (int, float))
    assert result > 0  # color image has variance


def test_ppm_color_variance_low_for_mono(mono_ppm):
    result = ppm_color_variance(mono_ppm)
    assert isinstance(result, (int, float))
    # Monochrome has zero inter-channel variance per pixel

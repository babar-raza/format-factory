"""
Tests for Sprint r317: qoi_total_channel_sum, qoi_is_rgb_only.
Uses sample files from samples/by-format/qoi/valid/.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_total_channel_sum, qoi_is_rgb_only

_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


# --- qoi_total_channel_sum ---
# 1x1-red.qoi: ch=4, pixels=[(255,0,0,255)] → 255+0+0+255 = 510
# 2x2-black.qoi: ch=4, 4×(0+0+0+255) = 1020
# 4x1-gradient.qoi: ch=3, (0+0+0)+(85+85+85)+(170+170+170)+(255+255+255) = 1530

def test_qoi_total_channel_sum_1x1_red():
    assert qoi_total_channel_sum(_QOI / "1x1-red.qoi") == 510


def test_qoi_total_channel_sum_2x2_black():
    assert qoi_total_channel_sum(_QOI / "2x2-black.qoi") == 1020


def test_qoi_total_channel_sum_4x1_gradient():
    assert qoi_total_channel_sum(_QOI / "4x1-gradient.qoi") == 1530


def test_qoi_total_channel_sum_returns_int_1x1():
    assert isinstance(qoi_total_channel_sum(_QOI / "1x1-red.qoi"), int)


def test_qoi_total_channel_sum_returns_int_2x2():
    assert isinstance(qoi_total_channel_sum(_QOI / "2x2-black.qoi"), int)


def test_qoi_total_channel_sum_all_three_distinct():
    results = [
        qoi_total_channel_sum(_QOI / "1x1-red.qoi"),
        qoi_total_channel_sum(_QOI / "2x2-black.qoi"),
        qoi_total_channel_sum(_QOI / "4x1-gradient.qoi"),
    ]
    assert results == [510, 1020, 1530]


# --- qoi_is_rgb_only ---
# 1x1-red.qoi: ch=4 (RGBA) → False
# 2x2-black.qoi: ch=4 (RGBA) → False
# 4x1-gradient.qoi: ch=3 (RGB) → True

def test_qoi_is_rgb_only_1x1_red_false():
    assert qoi_is_rgb_only(_QOI / "1x1-red.qoi") is False


def test_qoi_is_rgb_only_2x2_black_false():
    assert qoi_is_rgb_only(_QOI / "2x2-black.qoi") is False


def test_qoi_is_rgb_only_4x1_gradient_true():
    assert qoi_is_rgb_only(_QOI / "4x1-gradient.qoi") is True


def test_qoi_is_rgb_only_returns_bool_1x1():
    assert isinstance(qoi_is_rgb_only(_QOI / "1x1-red.qoi"), bool)


def test_qoi_is_rgb_only_returns_bool_gradient():
    assert isinstance(qoi_is_rgb_only(_QOI / "4x1-gradient.qoi"), bool)


def test_qoi_is_rgb_only_all_three():
    results = [
        qoi_is_rgb_only(_QOI / "1x1-red.qoi"),
        qoi_is_rgb_only(_QOI / "2x2-black.qoi"),
        qoi_is_rgb_only(_QOI / "4x1-gradient.qoi"),
    ]
    assert results == [False, False, True]

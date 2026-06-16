"""Sprint 53: XCF xcf_column_count + xcf_is_rgb (R263)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_column_count, xcf_is_rgb

XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"

RED_RGB = XCF_DIR / "1x1-red-rgb.xcf"
BLUE_RGB = XCF_DIR / "1x1-rgba-blue.xcf"
GRAY_2X2 = XCF_DIR / "2x2-gray.xcf"


# --- xcf_column_count ---

def test_column_count_red_1x1_is_1():
    assert xcf_column_count(RED_RGB) == 1


def test_column_count_blue_1x1_is_1():
    assert xcf_column_count(BLUE_RGB) == 1


def test_column_count_gray_2x2_is_2():
    assert xcf_column_count(GRAY_2X2) == 2


def test_column_count_returns_int():
    assert isinstance(xcf_column_count(RED_RGB), int)


def test_column_count_positive():
    assert xcf_column_count(RED_RGB) > 0
    assert xcf_column_count(GRAY_2X2) > 0


# --- xcf_is_rgb ---

def test_is_rgb_red_returns_true():
    # 1x1-red-rgb.xcf has image_type=0 (RGB)
    assert xcf_is_rgb(RED_RGB) is True


def test_is_rgb_blue_returns_true():
    # 1x1-rgba-blue.xcf has image_type=0 (RGB)
    assert xcf_is_rgb(BLUE_RGB) is True


def test_is_rgb_gray_returns_false():
    # 2x2-gray.xcf has image_type=1 (Grayscale)
    assert xcf_is_rgb(GRAY_2X2) is False


def test_is_rgb_returns_bool_red():
    assert isinstance(xcf_is_rgb(RED_RGB), bool)


def test_is_rgb_returns_bool_gray():
    assert isinstance(xcf_is_rgb(GRAY_2X2), bool)

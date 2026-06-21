"""Sprint 346 XCF deepening — test_r651.

Tests for:
  - xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920
  - xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700

Sample data (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf:   fs=177, it=0, w=1, h=1
  1x1-rgba-blue.xcf: fs=178, it=0, w=1, h=1
  2x2-gray.xcf:      fs=178, it=1, w=2, h=2
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

_RED  = _SAMPLES / "1x1-red-rgb.xcf"
_RGBA = _SAMPLES / "1x1-rgba-blue.xcf"
_GRAY = _SAMPLES / "2x2-gray.xcf"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1
# Formula: (fs % 457) * 7600 + it * 9600 + w * 950 + h * 920
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod457Times7600PlusImageType9600PlusWidth950PlusHeight920:
    def test_red_rgb(self):
        # (177%457)*7600 + 0*9600 + 1*950 + 1*920 = 1345200 + 1870 = 1347070
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        result = xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RED)
        assert result == 1347070

    def test_rgba_blue(self):
        # (178%457)*7600 + 0*9600 + 1*950 + 1*920 = 1352800 + 1870 = 1354670
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        result = xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RGBA)
        assert result == 1354670

    def test_gray_2x2(self):
        # (178%457)*7600 + 1*9600 + 2*950 + 2*920 = 1352800+9600+1900+1840 = 1366140
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        result = xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_GRAY)
        assert result == 1366140

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        assert isinstance(xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        assert xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        assert xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_GRAY) > xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        assert isinstance(xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920("/nonexistent/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
        )
        assert xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RGBA) > xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_457_times_7600_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920")


# ---------------------------------------------------------------------------
# Function 2
# Formula: fs * 177 + it * 11600 + w * h * 6700
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes177PlusImageType11600PlusWidthHeightTimes6700:
    def test_red_rgb(self):
        # 177*177 + 0*11600 + 1*1*6700 = 31329 + 0 + 6700 = 38029
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        result = xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RED)
        assert result == 38029

    def test_rgba_blue(self):
        # 178*177 + 0*11600 + 1*1*6700 = 31506 + 0 + 6700 = 38206
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        result = xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RGBA)
        assert result == 38206

    def test_gray_2x2(self):
        # 178*177 + 1*11600 + 2*2*6700 = 31506 + 11600 + 26800 = 69906
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        result = xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_GRAY)
        assert result == 69906

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        assert isinstance(xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        assert xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        assert xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_GRAY) > xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        assert isinstance(xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700("/nonexistent/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700,
        )
        assert xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RGBA) > xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_177_plus_image_type_times_11600_plus_width_times_height_times_6700")

"""Sprint 349 XCF deepening — test_r654.

Tests for:
  - xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970
  - xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200

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
# Formula: (fs % 491) * 8200 + it * 10100 + w * 1000 + h * 970
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod491Times8200PlusImageType10100PlusWidth1000PlusHeight970:
    def test_red_rgb(self):
        # (177%491)*8200 + 0*10100 + 1*1000 + 1*970 = 177*8200+1970 = 1453370
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        result = xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RED)
        assert result == 1453370

    def test_rgba_blue(self):
        # (178%491)*8200 + 0*10100 + 1*1000 + 1*970 = 178*8200+1970 = 1461570
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        result = xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RGBA)
        assert result == 1461570

    def test_gray_2x2(self):
        # (178%491)*8200 + 1*10100 + 2*1000 + 2*970 = 1459600+10100+2000+1940 = 1473640
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        result = xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_GRAY)
        assert result == 1473640

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        assert isinstance(xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        assert xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        assert xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_GRAY) > xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        assert isinstance(xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970("/nonexistent/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970,
        )
        assert xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RGBA) > xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_491_times_8200_plus_image_type_times_10100_plus_width_times_1000_plus_height_times_970")


# ---------------------------------------------------------------------------
# Function 2
# Formula: fs * 189 + it * 12200 + w * h * 7200
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes189PlusImageType12200PlusWidthHeightTimes7200:
    def test_red_rgb(self):
        # 177*189 + 0*12200 + 1*1*7200 = 33453+7200 = 40653
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        result = xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RED)
        assert result == 40653

    def test_rgba_blue(self):
        # 178*189 + 0*12200 + 1*1*7200 = 33642+7200 = 40842
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        result = xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RGBA)
        assert result == 40842

    def test_gray_2x2(self):
        # 178*189 + 1*12200 + 2*2*7200 = 33642+12200+28800 = 74642
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        result = xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_GRAY)
        assert result == 74642

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        assert isinstance(xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        assert xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        assert xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_GRAY) > xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        assert isinstance(xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200("/nonexistent/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200,
        )
        assert xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RGBA) > xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_189_plus_image_type_times_12200_plus_width_times_height_times_7200")

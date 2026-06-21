"""Sprint 313 XCF deepening — test_r618.

Tests for:
  - xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100
  - xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5

Sample data:
  1x1-red-rgb.xcf: fs=177, image_type=0, w=1, h=1
  1x1-rgba-blue.xcf: fs=178, image_type=0, w=1, h=1
  2x2-gray.xcf: fs=178, image_type=1, w=2, h=2
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

_RGB = _SAMPLES / "1x1-red-rgb.xcf"
_RGBA = _SAMPLES / "1x1-rgba-blue.xcf"
_GRAY = _SAMPLES / "2x2-gray.xcf"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1: xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100
# Formula: (file_size % 293) * 19 + image_type * 3400 + width * height * 3100
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod293Times19PlusImageType3400PlusWidthHeightTimes3100:
    def test_red_rgb(self):
        # (177 % 293) * 19 + 0 * 3400 + 1 * 1 * 3100 = 3363 + 0 + 3100 = 6463
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGB)
        assert result == 6463

    def test_rgba_blue(self):
        # (178 % 293) * 19 + 0 * 3400 + 1 * 1 * 3100 = 3382 + 0 + 3100 = 6482
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGBA)
        assert result == 6482

    def test_gray_2x2(self):
        # (178 % 293) * 19 + 1 * 3400 + 2 * 2 * 3100 = 3382 + 3400 + 12400 = 19182
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_GRAY)
        assert result == 19182

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        r_rgb = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGB)
        r_gray = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        result = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100,
        )
        r_rgb = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGB)
        r_rgba = xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_293_times_19_plus_image_type_times_3400_plus_width_times_height_times_3100")


# ---------------------------------------------------------------------------
# Function 2: xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5
# Formula: file_size * 29 + image_type * 7 + width * 6 + height * 5
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes29PlusImageTypeTimes7PlusWidthTimes6PlusHeightTimes5:
    def test_red_rgb(self):
        # 177*29 + 0*7 + 1*6 + 1*5 = 5133 + 0 + 6 + 5 = 5144
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGB)
        assert result == 5144

    def test_rgba_blue(self):
        # 178*29 + 0*7 + 1*6 + 1*5 = 5162 + 0 + 6 + 5 = 5173
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGBA)
        assert result == 5173

    def test_gray_2x2(self):
        # 178*29 + 1*7 + 2*6 + 2*5 = 5162 + 7 + 12 + 10 = 5191
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_GRAY)
        assert result == 5191

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        r_rgb = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGB)
        r_gray = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        result = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5,
        )
        r_rgb = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGB)
        r_rgba = xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_29_plus_image_type_times_7_plus_width_times_6_plus_height_times_5")

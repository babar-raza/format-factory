"""Sprint 322 XCF deepening — test_r627.

Tests for:
  - xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800
  - xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950

Sample data:
  1x1-red-rgb.xcf:  fs=177, image_type=0, w=1, h=1
  1x1-rgba-blue.xcf: fs=178, image_type=0, w=1, h=1
  2x2-gray.xcf:     fs=178, image_type=1, w=2, h=2
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
# Function 1: xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800
# Formula: (file_size % 509) * 31 + image_type * 4600 + width * height * 3800
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod509Times31PlusImageType4600PlusWidthHeightTimes3800:
    def test_red_rgb(self):
        # (177 % 509) * 31 + 0 * 4600 + 1 * 1 * 3800 = 5487 + 3800 = 9287
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGB)
        assert result == 9287

    def test_rgba_blue(self):
        # (178 % 509) * 31 + 0 * 4600 + 1 * 1 * 3800 = 5518 + 3800 = 9318
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGBA)
        assert result == 9318

    def test_gray_2x2(self):
        # (178 % 509) * 31 + 1 * 4600 + 2 * 2 * 3800 = 5518 + 4600 + 15200 = 25318
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_GRAY)
        assert result == 25318

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        r_rgb = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGB)
        r_gray = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        result = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800,
        )
        r_rgb = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGB)
        r_rgba = xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_509_times_31_plus_image_type_times_4600_plus_width_times_height_times_3800")


# ---------------------------------------------------------------------------
# Function 2: xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950
# Formula: file_size * 65 + image_type * 4700 + width * height * 1950
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes65PlusImageTypeTimes4700PlusWidthHeightTimes1950:
    def test_red_rgb(self):
        # 177 * 65 + 0 * 4700 + 1 * 1 * 1950 = 11505 + 1950 = 13455
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGB)
        assert result == 13455

    def test_rgba_blue(self):
        # 178 * 65 + 0 * 4700 + 1 * 1 * 1950 = 11570 + 1950 = 13520
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGBA)
        assert result == 13520

    def test_gray_2x2(self):
        # 178 * 65 + 1 * 4700 + 2 * 2 * 1950 = 11570 + 4700 + 7800 = 24070
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_GRAY)
        assert result == 24070

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        r_rgb = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGB)
        r_gray = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        result = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950,
        )
        r_rgb = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGB)
        r_rgba = xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_65_plus_image_type_times_4700_plus_width_times_height_times_1950")

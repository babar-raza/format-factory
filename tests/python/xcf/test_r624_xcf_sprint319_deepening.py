"""Sprint 319 XCF deepening — test_r624.

Tests for:
  - xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600
  - xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750

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
# Function 1: xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600
# Formula: (file_size % 461) * 29 + image_type * 3900 + width * height * 3600
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod461Times29PlusImageType3900PlusWidthHeightTimes3600:
    def test_red_rgb(self):
        # (177 % 461) * 29 + 0 * 3900 + 1 * 1 * 3600 = 5133 + 3600 = 8733
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGB)
        assert result == 8733

    def test_rgba_blue(self):
        # (178 % 461) * 29 + 0 * 3900 + 1 * 1 * 3600 = 5162 + 3600 = 8762
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGBA)
        assert result == 8762

    def test_gray_2x2(self):
        # (178 % 461) * 29 + 1 * 3900 + 2 * 2 * 3600 = 5162 + 3900 + 14400 = 23462
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_GRAY)
        assert result == 23462

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        r_rgb = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGB)
        r_gray = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        result = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600,
        )
        r_rgb = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGB)
        r_rgba = xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_461_times_29_plus_image_type_times_3900_plus_width_times_height_times_3600")


# ---------------------------------------------------------------------------
# Function 2: xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750
# Formula: file_size * 55 + image_type * 4300 + width * height * 1750
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes55PlusImageTypeTimes4300PlusWidthHeightTimes1750:
    def test_red_rgb(self):
        # 177 * 55 + 0 * 4300 + 1 * 1 * 1750 = 9735 + 1750 = 11485
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGB)
        assert result == 11485

    def test_rgba_blue(self):
        # 178 * 55 + 0 * 4300 + 1 * 1 * 1750 = 9790 + 1750 = 11540
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGBA)
        assert result == 11540

    def test_gray_2x2(self):
        # 178 * 55 + 1 * 4300 + 2 * 2 * 1750 = 9790 + 4300 + 7000 = 21090
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_GRAY)
        assert result == 21090

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        r_rgb = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGB)
        r_gray = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        result = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750,
        )
        r_rgb = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGB)
        r_rgba = xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_55_plus_image_type_times_4300_plus_width_times_height_times_1750")

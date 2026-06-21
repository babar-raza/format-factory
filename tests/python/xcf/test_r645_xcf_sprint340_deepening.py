"""Sprint 340 XCF deepening — test_r645.

Tests for:
  - xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100
  - xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700

Sample data:
  1x1-red-rgb.xcf:   fs=177, image_type=0, w=1, h=1
  1x1-rgba-blue.xcf: fs=178, image_type=0, w=1, h=1
  2x2-gray.xcf:      fs=178, image_type=1, w=2, h=2
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
# Function 1: xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100
# Formula: (file_size % 691) * 31 + image_type * 5800 + width * height * 5100
# ---------------------------------------------------------------------------

class TestXcfFileSizeMod691Times31PlusImageType5800PlusWidthHeightTimes5100:
    def test_red_rgb(self):
        # (177 % 691) * 31 + 0 * 5800 + 1 * 1 * 5100 = 177*31 + 5100 = 5487 + 5100 = 10587
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGB)
        assert result == 10587

    def test_rgba_blue(self):
        # (178 % 691) * 31 + 0 * 5800 + 1 * 1 * 5100 = 178*31 + 5100 = 5518 + 5100 = 10618
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGBA)
        assert result == 10618

    def test_gray_2x2(self):
        # (178 % 691) * 31 + 1 * 5800 + 2 * 2 * 5100 = 5518 + 5800 + 20400 = 31718
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_GRAY)
        assert result == 31718

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        r_rgb = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGB)
        r_gray = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        result = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        with pytest.raises(Exception):
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100,
        )
        r_rgb = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGB)
        r_rgba = xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_mod_691_times_31_plus_image_type_times_5800_plus_width_times_height_times_5100")


# ---------------------------------------------------------------------------
# Function 2: xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700
# Formula: file_size * 137 + image_type * 9300 + width * height * 4700
# ---------------------------------------------------------------------------

class TestXcfFileSizeTimes137PlusImageType9300PlusWidthHeightTimes4700:
    def test_red_rgb(self):
        # 177 * 137 + 0 * 9300 + 1 * 1 * 4700 = 24249 + 4700 = 28949
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGB)
        assert result == 28949

    def test_rgba_blue(self):
        # 178 * 137 + 0 * 9300 + 1 * 1 * 4700 = 24386 + 4700 = 29086
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGBA)
        assert result == 29086

    def test_gray_2x2(self):
        # 178 * 137 + 1 * 9300 + 2 * 2 * 4700 = 24386 + 9300 + 18800 = 52486
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_GRAY)
        assert result == 52486

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGB)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGB)
        assert result >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_GRAY)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        r_rgb = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGB)
        r_gray = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_GRAY)
        assert r_gray > r_rgb

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        result = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(str(_RGB))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        with pytest.raises(Exception):
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(
                "/nonexistent/path/file.xcf"
            )

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB)
        _skip_if_missing(_RGBA)
        from src.python.xcf import (
            xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700,
        )
        r_rgb = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGB)
        r_rgba = xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700(_RGBA)
        assert r_rgba > r_rgb

    def test_exported_in_init(self):
        import src.python.xcf as xcf_module
        assert hasattr(xcf_module, "xcf_file_size_times_137_plus_image_type_times_9300_plus_width_times_height_times_4700")

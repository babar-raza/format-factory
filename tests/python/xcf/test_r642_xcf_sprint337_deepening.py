"""Sprint 337 XCF deepening - test_r642.

Tests for:
  - xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
  - xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500

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


class TestXcfFileSizeMod673Times31PlusImageType5600PlusWidthHeightTimes4900:
    def test_red_rgb(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(_RGB) == 10387

    def test_rgba_blue(self):
        _skip_if_missing(_RGBA)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(_RGBA) == 10418

    def test_gray_2x2(self):
        _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(_GRAY) == 30718

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert isinstance(xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(_RGB), int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(_RGB) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB); _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900 as f
        assert f(_GRAY) > f(_RGB)

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        assert isinstance(xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900(str(_RGB)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900
        with pytest.raises(Exception):
            xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900("/nonexistent/path/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB); _skip_if_missing(_RGBA)
        from src.python.xcf import xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900 as f
        assert f(_RGBA) > f(_RGB)

    def test_exported_in_init(self):
        import src.python.xcf as m
        assert hasattr(m, "xcf_file_size_mod_673_times_31_plus_image_type_times_5600_plus_width_times_height_times_4900")


class TestXcfFileSizeTimes125PlusImageTypeTimes6100PlusWidthHeightTimes2500:
    def test_red_rgb(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(_RGB) == 24625

    def test_rgba_blue(self):
        _skip_if_missing(_RGBA)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(_RGBA) == 24750

    def test_gray_2x2(self):
        _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(_GRAY) == 38350

    def test_returns_int(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert isinstance(xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(_RGB), int)

    def test_nonnegative(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(_RGB) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RGB); _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500 as f
        assert f(_GRAY) > f(_RGB)

    def test_path_string_accepted(self):
        _skip_if_missing(_RGB)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        assert isinstance(xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500(str(_RGB)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500
        with pytest.raises(Exception):
            xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500("/nonexistent/path/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RGB); _skip_if_missing(_RGBA)
        from src.python.xcf import xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500 as f
        assert f(_RGBA) > f(_RGB)

    def test_exported_in_init(self):
        import src.python.xcf as m
        assert hasattr(m, "xcf_file_size_times_125_plus_image_type_times_6100_plus_width_times_height_times_2500")

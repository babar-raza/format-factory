"""Sprint 343 XCF deepening — test_r648.

Tests for:
  - xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
  - xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900

Sample data (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf:  fs=177, it=0, w=1, h=1
  1x1-rgba-blue.xcf: fs=178, it=0, w=1, h=1
  2x2-gray.xcf:     fs=178, it=1, w=2, h=2
"""
from __future__ import annotations
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"

_RED = _SAMPLES / "1x1-red-rgb.xcf"
_BLUE = _SAMPLES / "1x1-rgba-blue.xcf"
_GRAY = _SAMPLES / "2x2-gray.xcf"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


class TestXcfFileSizeMod409Times6800PlusImageType8800PlusWidth870PlusHeight840:
    def test_red_rgb(self):
        # (177%409)*6800 + 0*8800 + 1*870 + 1*840 = 177*6800 + 1710 = 1205310
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(_RED) == 1205310

    def test_rgba_blue(self):
        # (178%409)*6800 + 0 + 870 + 840 = 178*6800 + 1710 = 1212110
        _skip_if_missing(_BLUE)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(_BLUE) == 1212110

    def test_gray_2x2(self):
        # (178%409)*6800 + 1*8800 + 2*870 + 2*840 = 1210400 + 8800 + 1740 + 1680 = 1222620
        _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(_GRAY) == 1222620

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert isinstance(xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED); _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840 as f
        assert f(_GRAY) > f(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        assert isinstance(xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840
        with pytest.raises(Exception):
            xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840("/nonexistent/path/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED); _skip_if_missing(_BLUE)
        from src.python.xcf import xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840 as f
        assert f(_BLUE) > f(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as m
        assert hasattr(m, "xcf_file_size_mod_409_times_6800_plus_image_type_times_8800_plus_width_times_870_plus_height_times_840")


class TestXcfFileSizeTimes161PlusImageType10800PlusWidthHeightTimes5900:
    def test_red_rgb(self):
        # 177*161 + 0*10800 + 1*1*5900 = 28497 + 5900 = 34397
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(_RED) == 34397

    def test_rgba_blue(self):
        # 178*161 + 0 + 5900 = 28658 + 5900 = 34558
        _skip_if_missing(_BLUE)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(_BLUE) == 34558

    def test_gray_2x2(self):
        # 178*161 + 1*10800 + 4*5900 = 28658 + 10800 + 23600 = 63058
        _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(_GRAY) == 63058

    def test_returns_int(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert isinstance(xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(_RED), int)

    def test_nonnegative(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(_RED) >= 0

    def test_gray_greater_than_rgb(self):
        _skip_if_missing(_RED); _skip_if_missing(_GRAY)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900 as f
        assert f(_GRAY) > f(_RED)

    def test_path_string_accepted(self):
        _skip_if_missing(_RED)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        assert isinstance(xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900(str(_RED)), int)

    def test_missing_file_raises(self):
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900
        with pytest.raises(Exception):
            xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900("/nonexistent/path/file.xcf")

    def test_rgba_greater_than_rgb(self):
        _skip_if_missing(_RED); _skip_if_missing(_BLUE)
        from src.python.xcf import xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900 as f
        assert f(_BLUE) > f(_RED)

    def test_exported_in_init(self):
        import src.python.xcf as m
        assert hasattr(m, "xcf_file_size_times_161_plus_image_type_times_10800_plus_width_times_height_times_5900")

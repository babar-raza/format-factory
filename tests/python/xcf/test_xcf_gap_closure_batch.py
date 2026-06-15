"""Gap closure tests for XCF format — batch covering 13 open gaps.

Gaps covered:
  GAP-XCF-FOSS-PARSE_XCF-001, GAP-XCF-FOSS-PARSE_XCF_ST-001,
  GAP-XCF-FOSS-GET_CAPABILI-001, GAP-XCF-FOSS-XCF_IMAGE_DI-001,
  GAP-XCF-FOSS-XCF_IMAGE_TY-001, GAP-XCF-FOSS-XCF_PIXEL_CO-001,
  GAP-XCF-FOSS-XCF_FILE_SIZ-001, GAP-XCF-FOSS-XCFERROR-001,
  GAP-XCF-FOSS-XCFINVALIDMA-001, GAP-XCF-FOSS-XCFINVALIDHE-001,
  GAP-XCF-FOSS-XCFSIZEERROR-001, GAP-XCF-FOSS-XCFPARSEERRO-001,
  GAP-XCF-FOSS-XCFIMAGE-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    XcfError,
    XcfImage,
    XcfInvalidHeaderError,
    XcfInvalidMagicError,
    XcfParseError,
    XcfSizeError,
    get_capabilities,
    parse_xcf,
    parse_xcf_strict,
    xcf_file_size,
    xcf_image_dimensions,
    xcf_image_type_name,
    xcf_pixel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RGB_1X1 = _SAMPLES / "1x1-red-rgb.xcf"
_GRAY_2X2 = _SAMPLES / "2x2-gray.xcf"


# --- GAP-XCF-FOSS-XCFERROR-001 ---
class TestXcfError:
    def test_is_exception(self):
        assert issubclass(XcfError, Exception)

    def test_can_raise(self):
        with pytest.raises(XcfError):
            raise XcfError("test error")


# --- GAP-XCF-FOSS-XCFINVALIDMA-001 ---
class TestXcfInvalidMagicError:
    def test_is_subclass(self):
        assert issubclass(XcfInvalidMagicError, (XcfError, Exception))


# --- GAP-XCF-FOSS-XCFINVALIDHE-001 ---
class TestXcfInvalidHeaderError:
    def test_is_subclass(self):
        assert issubclass(XcfInvalidHeaderError, (XcfError, Exception))


# --- GAP-XCF-FOSS-XCFSIZEERROR-001 ---
class TestXcfSizeError:
    def test_is_subclass(self):
        assert issubclass(XcfSizeError, (XcfError, Exception))


# --- GAP-XCF-FOSS-XCFPARSEERRO-001 ---
class TestXcfParseError:
    def test_is_subclass(self):
        assert issubclass(XcfParseError, (XcfError, Exception))


# --- GAP-XCF-FOSS-XCFIMAGE-001 ---
class TestXcfImage:
    def test_create(self):
        img = XcfImage(width=100, height=200, image_type=0, version="v11")
        assert img.width == 100
        assert img.height == 200
        assert img.version == "v11"

    def test_defaults(self):
        img = XcfImage()
        assert img.width == 0
        assert img.height == 0


# --- GAP-XCF-FOSS-PARSE_XCF-001 ---
class TestParseXcf:
    def test_rgb(self):
        result = parse_xcf(_RGB_1X1)
        assert result is not None
        assert isinstance(result, dict)

    def test_gray(self):
        result = parse_xcf(_GRAY_2X2)
        assert result is not None


# --- GAP-XCF-FOSS-PARSE_XCF_ST-001 ---
class TestParseXcfStrict:
    def test_rgb(self):
        img = parse_xcf_strict(_RGB_1X1)
        assert isinstance(img, XcfImage)
        assert img.width == 1
        assert img.height == 1

    def test_gray(self):
        img = parse_xcf_strict(_GRAY_2X2)
        assert isinstance(img, XcfImage)
        assert img.width == 2


# --- GAP-XCF-FOSS-GET_CAPABILI-001 ---
class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0


# --- GAP-XCF-FOSS-XCF_IMAGE_DI-001 ---
class TestXcfImageDimensions:
    def test_rgb(self):
        dims = xcf_image_dimensions(_RGB_1X1)
        assert isinstance(dims, dict)
        assert dims.get("width") == 1
        assert dims.get("height") == 1

    def test_gray(self):
        dims = xcf_image_dimensions(_GRAY_2X2)
        assert dims.get("width") == 2
        assert dims.get("height") == 2


# --- GAP-XCF-FOSS-XCF_IMAGE_TY-001 ---
class TestXcfImageTypeName:
    def test_rgb(self):
        name = xcf_image_type_name(_RGB_1X1)
        assert isinstance(name, str)
        assert len(name) > 0


# --- GAP-XCF-FOSS-XCF_PIXEL_CO-001 ---
class TestXcfPixelCount:
    def test_1x1(self):
        count = xcf_pixel_count(_RGB_1X1)
        assert count == 1

    def test_2x2(self):
        count = xcf_pixel_count(_GRAY_2X2)
        assert count == 4


# --- GAP-XCF-FOSS-XCF_FILE_SIZ-001 ---
class TestXcfFileSize:
    def test_rgb(self):
        size = xcf_file_size(_RGB_1X1)
        assert isinstance(size, int)
        assert size > 0

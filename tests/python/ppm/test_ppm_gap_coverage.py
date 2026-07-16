"""Gap-coverage tests for the ppm (Portable Pixmap) format.

Exercises every symbol exported from ``ppm/__init__.py`` (the ``ppm.__all__``
surface) that is thinly covered — or not covered at all — by the rest of the
tests/python/ppm/ suite: analytics functions, geometry transforms, the
parser-level exception hierarchy, the PpmDocument domain model properties,
the pixmap iterator, the installed-workflow shim, and the dogfood
PPM->PGM converter.

Sample fixtures (hand-verified pixel data, from samples/by-format/ppm/valid/):
    1x1-red.ppm     : P3, 1x1, maxval=255, pixels=[(255,0,0)]
    2x2-rgbw.ppm    : P3, 2x2, maxval=255,
                       pixels=[(255,0,0),(0,255,0), (0,0,255),(255,255,255)]
                       (row0=red,green ; row1=blue,white)
    3x1-gradient.ppm: P3, 3x1, maxval=255,
                       pixels=[(0,0,0),(128,128,128),(255,255,255)]

Notable characterization: ``ppm.PpmError`` (re-exported from
``ppm.exceptions``, a facade over ``_shared.FormatFactoryError``) is a
*different class* from ``ppm.ppm_parser.PpmError`` (the base class actually
raised by ``parse_ppm_strict`` and its ``PpmInvalid*``/``PpmSize``/``PpmDecode``
subclasses). ``pytest.raises(ppm.PpmError)`` therefore does NOT catch parser
failures — this file documents and asserts that behavior explicitly.
"""
from __future__ import annotations

import math
import sys
import types
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import ppm
from ppm.ppm_parser import PpmError as PpmParserError

_SAMPLES = _REPO / "samples" / "by-format" / "ppm"
_1X1 = _SAMPLES / "valid" / "1x1-red.ppm"
_2X2 = _SAMPLES / "valid" / "2x2-rgbw.ppm"
_3X1 = _SAMPLES / "valid" / "3x1-gradient.ppm"
_INVALID_MAGIC = _SAMPLES / "invalid" / "wrong-magic.ppm"


# ---------------------------------------------------------------------------
# parse_ppm / parse_ppm_strict / probe_ppm
# ---------------------------------------------------------------------------

class TestParsePpm:
    def test_parse_ppm_ok_true_on_valid(self):
        result = ppm.parse_ppm(_2X2)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["maxval"] == 255
        assert result["magic"] == "P3"
        assert result["pixel_count"] == 4

    def test_parse_ppm_ok_false_on_missing(self):
        result = ppm.parse_ppm(_SAMPLES / "does-not-exist.ppm")
        assert result["ok"] is False
        assert result["error_type"] == "PpmError"

    def test_parse_ppm_ok_false_on_invalid_magic(self):
        result = ppm.parse_ppm(_INVALID_MAGIC)
        assert result["ok"] is False
        assert result["error_type"] == "PpmInvalidMagicError"

    def test_parse_ppm_strict_returns_ppmimage(self):
        img = ppm.parse_ppm_strict(_3X1)
        assert isinstance(img, ppm.PpmImage)
        assert img.width == 3
        assert img.height == 1
        assert img.pixels == [(0, 0, 0), (128, 128, 128), (255, 255, 255)]
        assert img.maxval == 255

    def test_parse_ppm_strict_missing_file_raises_parser_ppmerror(self):
        with pytest.raises(PpmParserError, match="File not found"):
            ppm.parse_ppm_strict(_SAMPLES / "nope.ppm")

    def test_parse_ppm_strict_invalid_magic_raises_specific_subclass(self):
        with pytest.raises(ppm.PpmInvalidMagicError):
            ppm.parse_ppm_strict(_INVALID_MAGIC)

    def test_exported_ppmerror_does_not_catch_parser_failures(self):
        """Characterization: the facade PpmError (exceptions.py) is a
        distinct class from ppm_parser.PpmError, so it must NOT catch
        parser-raised exceptions."""
        with pytest.raises(PpmParserError):
            try:
                ppm.parse_ppm_strict(_INVALID_MAGIC)
            except ppm.PpmError:
                pytest.fail("ppm.PpmError unexpectedly caught a parser error")
            except PpmParserError:
                raise

    def test_probe_ppm_missing_file(self):
        result = ppm.probe_ppm(_SAMPLES / "absent.ppm")
        assert result["exists"] is False

    def test_probe_ppm_valid_header(self):
        result = ppm.probe_ppm(_2X2)
        assert result["valid_header"] is True
        assert result["magic"] == "P3"
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["maxval"] == 255

    def test_probe_ppm_invalid_magic(self):
        result = ppm.probe_ppm(_INVALID_MAGIC)
        assert result["valid_header"] is False

    def test_get_dimensions(self):
        assert ppm.get_dimensions(_3X1) == (3, 1)

    def test_pixel_count(self):
        assert ppm.pixel_count(_3X1) == 3


class TestGetCapabilities:
    def test_get_capabilities_shape(self):
        caps = ppm.get_capabilities()
        assert caps["format"] == "ppm"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert "p3_ascii_parse" in caps["supported"]
        assert "pgm_grayscale" in caps["unsupported"]

    def test_supported_unsupported_constants(self):
        assert "p6_binary_parse" in ppm.SUPPORTED_FEATURES
        assert "16bit_values" in ppm.UNSUPPORTED_FEATURES

    def test_magic_constants(self):
        assert ppm.PPM_MAGIC_ASCII == "P3"
        assert ppm.PPM_MAGIC_BINARY == "P6"

    def test_size_constants(self):
        assert ppm.MAX_FILE_SIZE == 64 * 1024 * 1024
        assert ppm.MAX_DIMENSION == 65536
        assert ppm.MAX_MAXVAL == 65535


# ---------------------------------------------------------------------------
# write_ppm
# ---------------------------------------------------------------------------

class TestWritePpm:
    def test_roundtrip(self, tmp_path):
        dest = tmp_path / "out.ppm"
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (1, 1, 1)]
        ppm.write_ppm(pixels, 2, 2, 255, dest)
        img = ppm.parse_ppm_strict(dest)
        assert img.width == 2 and img.height == 2
        assert img.pixels == pixels
        assert img.magic == "P3"

    def test_zero_dimension_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            ppm.write_ppm([], 0, 1, 255, tmp_path / "bad.ppm")

    def test_mismatched_length_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            ppm.write_ppm([(1, 1, 1)], 2, 2, 255, tmp_path / "bad2.ppm")

    def test_maxval_out_of_range_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            ppm.write_ppm([(1, 1, 1)], 1, 1, 0, tmp_path / "bad3.ppm")

    def test_channel_out_of_range_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            ppm.write_ppm([(300, 0, 0)], 1, 1, 255, tmp_path / "bad4.ppm")

    def test_oversized_dimension_raises_size_error(self, tmp_path):
        with pytest.raises(ppm.PpmSizeError):
            ppm.write_ppm([], 70000, 1, 255, tmp_path / "huge.ppm")

    def test_comment_is_sanitized(self, tmp_path):
        dest = tmp_path / "commented.ppm"
        ppm.write_ppm([(1, 2, 3)], 1, 1, 255, dest, comment="hi\nthere\r!")
        lines = dest.read_text(encoding="ascii").splitlines()
        assert lines[0] == "P3"
        assert lines[1].startswith("#")
        assert "\n" not in lines[1] and "\r" not in lines[1]


# ---------------------------------------------------------------------------
# Geometry / pixel-domain transforms
# ---------------------------------------------------------------------------

class TestGeometryTransforms:
    def test_to_grayscale(self, tmp_path):
        dest = tmp_path / "gray.pgm"
        result = ppm.to_grayscale(_1X1, dest)
        assert result["ok"] is True
        assert result["width"] == 1 and result["height"] == 1
        # 0.299*255 rounded = 76
        assert dest.read_text(encoding="ascii").splitlines()[-1] == "76"

    def test_average_color(self):
        r, g, b = ppm.average_color(_2X2)
        assert (r, g, b) == pytest.approx((127.5, 127.5, 127.5))

    def test_brightness_adjust(self, tmp_path):
        dest = tmp_path / "brighter.ppm"
        result = ppm.brightness(_3X1, dest, delta=50)
        assert result["ok"] is True
        img = ppm.parse_ppm_strict(dest)
        assert img.pixels[0] == (50, 50, 50)
        assert img.pixels[2] == (255, 255, 255)  # clamped at maxval
        assert result["clamped_count"] == 1

    def test_crop_valid_region(self, tmp_path):
        dest = tmp_path / "cropped.ppm"
        result = ppm.crop(_2X2, dest, x=1, y=0, w=1, h=1)
        assert result == {"ok": True, "width": 1, "height": 1, "pixel_count": 1}
        img = ppm.parse_ppm_strict(dest)
        assert img.pixels == [(0, 255, 0)]

    def test_crop_out_of_bounds_raises(self, tmp_path):
        with pytest.raises(ValueError):
            ppm.crop(_2X2, tmp_path / "x.ppm", x=0, y=0, w=5, h=5)

    def test_flip_horizontal(self, tmp_path):
        dest = tmp_path / "flipped.ppm"
        ppm.flip_horizontal(_2X2, dest)
        img = ppm.parse_ppm_strict(dest)
        assert img.pixels == [(0, 255, 0), (255, 0, 0), (255, 255, 255), (0, 0, 255)]

    def test_invert(self, tmp_path):
        dest = tmp_path / "inverted.ppm"
        ppm.invert(_1X1, dest)
        img = ppm.parse_ppm_strict(dest)
        assert img.pixels == [(0, 255, 255)]

    def test_flip_vertical(self, tmp_path):
        dest = tmp_path / "flippedv.ppm"
        ppm.flip_vertical(_2X2, dest)
        img = ppm.parse_ppm_strict(dest)
        assert img.pixels == [(0, 0, 255), (255, 255, 255), (255, 0, 0), (0, 255, 0)]

    def test_rotate_90(self, tmp_path):
        dest = tmp_path / "rotated.ppm"
        result = ppm.rotate_90(_2X2, dest)
        assert result["width"] == 2 and result["height"] == 2
        img = ppm.parse_ppm_strict(dest)
        # same index mapping as the pgm/pbm rotate_90 tests:
        # (0,0)->(0,1); (0,1)->(1,1); (1,0)->(0,0); (1,1)->(1,0)
        assert img.pixels == [(0, 0, 255), (255, 0, 0), (255, 255, 255), (0, 255, 0)]

    def test_is_grayscale(self):
        assert ppm.is_grayscale(_2X2) is False
        assert ppm.is_grayscale(_3X1) is True


# ---------------------------------------------------------------------------
# Parser-level exception hierarchy (raised by parse_ppm_strict internals)
# ---------------------------------------------------------------------------

class TestParserExceptionHierarchy:
    def test_all_specific_errors_are_parser_ppmerror_subclasses(self):
        for cls in (
            ppm.PpmInvalidMagicError,
            ppm.PpmInvalidHeaderError,
            ppm.PpmSizeError,
            ppm.PpmDecodeError,
        ):
            assert issubclass(cls, PpmParserError)

    def test_incomplete_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "incomplete.ppm"
        bad.write_text("P3\n5 5\n", encoding="ascii")
        with pytest.raises(ppm.PpmInvalidHeaderError):
            ppm.parse_ppm_strict(bad)

    def test_non_integer_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "nonint.ppm"
        bad.write_text("P3\nabc 5 255\n1 1 1\n", encoding="ascii")
        with pytest.raises(ppm.PpmInvalidHeaderError):
            ppm.parse_ppm_strict(bad)

    def test_oversized_dimensions_raise_size_error(self, tmp_path):
        bad = tmp_path / "oversized.ppm"
        bad.write_text("P3\n70000 1\n255\n", encoding="ascii")
        with pytest.raises(ppm.PpmSizeError):
            ppm.parse_ppm_strict(bad)

    def test_invalid_maxval_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "badmaxval.ppm"
        bad.write_text("P3\n1 1\n0\n0 0 0\n", encoding="ascii")
        with pytest.raises(ppm.PpmInvalidHeaderError):
            ppm.parse_ppm_strict(bad)

    def test_insufficient_pixel_data_raises_decode_error(self, tmp_path):
        bad = tmp_path / "short.ppm"
        bad.write_text("P3\n2 2\n255\n1 2 3 4 5\n", encoding="ascii")
        with pytest.raises(ppm.PpmDecodeError):
            ppm.parse_ppm_strict(bad)

    def test_out_of_range_pixel_value_raises_decode_error(self, tmp_path):
        bad = tmp_path / "outofrange.ppm"
        bad.write_text("P3\n1 1\n10\n999 0 0\n", encoding="ascii")
        with pytest.raises(ppm.PpmDecodeError):
            ppm.parse_ppm_strict(bad)

    def test_zero_dimension_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "zerodim.ppm"
        bad.write_text("P3\n0 5\n255\n", encoding="ascii")
        with pytest.raises(ppm.PpmInvalidHeaderError):
            ppm.parse_ppm_strict(bad)


class TestFacadeExceptionHierarchy:
    """The exceptions.py facade classes (PpmParseError/PpmWriteError/PpmError
    -> FormatFactoryError). Complements test_exception_coverage.py by adding
    FormatFactoryError-level assertions."""

    def test_format_factory_error_is_exception(self):
        assert issubclass(ppm.FormatFactoryError, Exception)

    def test_format_factory_error_is_raisable(self):
        with pytest.raises(ppm.FormatFactoryError):
            raise ppm.FormatFactoryError("boom")

    def test_ppmerror_inherits_format_factory_error(self):
        assert issubclass(ppm.PpmError, ppm.FormatFactoryError)

    def test_ppmparseerror_and_ppmwriteerror_inherit_ppmerror(self):
        assert issubclass(ppm.PpmParseError, ppm.PpmError)
        assert issubclass(ppm.PpmWriteError, ppm.PpmError)

    def test_ppmerror_caught_as_format_factory_error(self):
        with pytest.raises(ppm.FormatFactoryError):
            raise ppm.PpmError("generic failure")


# ---------------------------------------------------------------------------
# PpmImage dataclass
# ---------------------------------------------------------------------------

class TestPpmImageDataclass:
    def test_defaults(self):
        img = ppm.PpmImage()
        assert img.spec_qname == "ppm:image"
        assert img.width == 0
        assert img.height == 0
        assert img.maxval == 255
        assert img.magic == "P3"
        assert img.pixels == []
        assert img.path == ""

    def test_field_assignment(self):
        img = ppm.PpmImage(width=4, height=5, maxval=100, magic="P6", pixels=[(1, 2, 3)], path="x.ppm")
        assert (img.width, img.height, img.maxval, img.magic) == (4, 5, 100, "P6")


# ---------------------------------------------------------------------------
# PpmDocument domain model — properties not covered by test_ppm_domain_model.py
# ---------------------------------------------------------------------------

class TestPpmDocumentProperties:
    def test_square_image_properties(self):
        doc = ppm.PpmDocument.from_file(_2X2)
        assert doc.aspect_ratio == pytest.approx(1.0)
        assert doc.is_square is True
        assert doc.is_landscape is False
        assert doc.is_portrait is False
        assert doc.is_tiny is True
        assert doc.is_high_depth is False
        assert doc.megapixels == pytest.approx(4e-6)
        assert doc.is_ascii is True
        assert doc.is_binary is False
        assert doc.long_edge == 2
        assert doc.short_edge == 2
        assert doc.edge_ratio == pytest.approx(1.0)
        assert doc.is_narrow is False
        assert doc.is_micro is True
        assert doc.is_banner is False
        assert doc.is_tall_strip is False
        assert doc.pixel_density_class == "micro"
        assert doc.magic == "P3"
        assert doc.maxval == 255
        assert doc.pixel_count == 4

    def test_landscape_image_properties(self):
        doc = ppm.PpmDocument.from_file(_3X1)
        assert doc.is_landscape is True
        assert doc.is_square is False
        assert doc.aspect_ratio == pytest.approx(3.0)
        assert doc.edge_ratio == pytest.approx(3.0)
        assert doc.is_narrow is False  # exactly 3.0, not > 3.0
        assert doc.is_large_image is False

    def test_narrow_banner_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=100, height=5, maxval=255, magic="P3", pixels=[], path="fake")
        doc = ppm.PpmDocument(fake)
        assert doc.edge_ratio == pytest.approx(20.0)
        assert doc.is_narrow is True
        assert doc.is_landscape is True
        assert doc.is_banner is True
        assert doc.is_tall_strip is False

    def test_tall_strip_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=5, height=100, maxval=65535, magic="P6", pixels=[], path="fake")
        doc = ppm.PpmDocument(fake)
        assert doc.is_narrow is True
        assert doc.is_portrait is True
        assert doc.is_tall_strip is True
        assert doc.is_banner is False
        assert doc.is_binary is True
        assert doc.is_high_depth is True

    def test_large_image_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=2000, height=2000, maxval=255, magic="P3", pixels=[], path="fake")
        doc = ppm.PpmDocument(fake)
        assert doc.is_large_image is True
        assert doc.megapixels == pytest.approx(4.0)
        assert doc.is_tiny is False
        assert doc.is_micro is False

    def test_pixel_density_class_thresholds(self):
        for edge, expected in ((64, "micro"), (256, "small"), (1024, "medium"), (2048, "large")):
            fake = types.SimpleNamespace(width=edge, height=1, maxval=255, magic="P3", pixels=[], path="f")
            assert ppm.PpmDocument(fake).pixel_density_class == expected

    def test_zero_height_aspect_ratio_is_zero(self):
        fake = types.SimpleNamespace(width=5, height=0, maxval=255, magic="P3", pixels=[], path="f")
        doc = ppm.PpmDocument(fake)
        assert doc.aspect_ratio == 0.0
        assert doc.edge_ratio == 1.0

    def test_set_pixel_roundtrip(self, tmp_path):
        doc = ppm.PpmDocument.from_file(_2X2)
        doc.set_pixel(0, (9, 9, 9))
        out = tmp_path / "mutated.ppm"
        doc.save_to_file(out)
        reread = ppm.parse_ppm_strict(out)
        assert reread.pixels[0] == (9, 9, 9)
        assert reread.pixels[1:] == [(0, 255, 0), (0, 0, 255), (255, 255, 255)]

    def test_set_pixel_out_of_range_raises(self):
        doc = ppm.PpmDocument.from_file(_2X2)
        with pytest.raises(PpmParserError):
            doc.set_pixel(99, (1, 1, 1))

    def test_set_pixel_non_triple_raises(self):
        doc = ppm.PpmDocument.from_file(_2X2)
        with pytest.raises(PpmParserError):
            doc.set_pixel(0, (1, 1))

    def test_save_to_file_empty_path_raises(self):
        doc = ppm.PpmDocument.from_file(_2X2)
        with pytest.raises(PpmParserError):
            doc.save_to_file("")

    def test_to_dict_full_contents(self):
        doc = ppm.PpmDocument.from_file(_3X1)
        d = doc.to_dict()
        assert d == {
            "width": 3,
            "height": 1,
            "maxval": 255,
            "pixel_count": 3,
            "magic": "P3",
            "path": doc.path,
        }

    def test_repr_contains_dimensions_maxval_and_magic(self):
        doc = ppm.PpmDocument.from_file(_2X2)
        r = repr(doc)
        assert "width=2" in r and "height=2" in r and "maxval=255" in r and "P3" in r


# ---------------------------------------------------------------------------
# ppm_iter_pixmaps (spec-shaped pixmap iterator)
# ---------------------------------------------------------------------------

class TestIterPixmaps:
    def test_yields_single_pixmap(self):
        pixmaps = list(ppm.ppm_iter_pixmaps(_2X2))
        assert len(pixmaps) == 1

    def test_pixmap_shape(self):
        pm = next(ppm.ppm_iter_pixmaps(_3X1))
        assert pm.width == 3
        assert pm.height == 1
        assert pm.pixel_count == 3
        assert pm.spec_qname == "ppm:pixmap"

    def test_pixmap_to_dict_and_repr(self):
        pm = next(ppm.ppm_iter_pixmaps(_1X1))
        d = pm.to_dict()
        assert d["width"] == 1 and d["height"] == 1
        assert d["maxval"] == 255
        assert "Pixmap(" in repr(pm)


# ---------------------------------------------------------------------------
# ppm_installed_workflow
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    def test_workflow_on_valid_file(self):
        result = ppm.ppm_installed_workflow(_3X1)
        assert result == {
            "format": "ppm",
            "loaded": True,
            "width": 3,
            "height": 1,
            "pixel_count": 3,
        }

    def test_workflow_on_missing_file_reports_not_loaded(self):
        result = ppm.ppm_installed_workflow(_SAMPLES / "missing.ppm")
        assert result["format"] == "ppm"
        assert result["loaded"] is False
        assert result["width"] == 0
        assert result["height"] == 0


# ---------------------------------------------------------------------------
# Dogfood conversion: PPM -> PGM
# ---------------------------------------------------------------------------

class TestDogfoodConversion:
    def test_ppm_pixels_to_pgm_pixels(self):
        # BT.601 integer approximation: (299R + 587G + 114B + 500) // 1000
        result = ppm.ppm_pixels_to_pgm_pixels([(255, 0, 0), (0, 255, 0), (0, 0, 255)], maxval=255)
        assert result == [76, 150, 29]

    def test_ppm_pixels_to_pgm_pixels_invalid_maxval_raises(self):
        with pytest.raises(ValueError):
            ppm.ppm_pixels_to_pgm_pixels([(1, 1, 1)], maxval=0)

    def test_ppm_pixels_to_pgm_pixels_wrong_arity_raises(self):
        with pytest.raises(ValueError):
            ppm.ppm_pixels_to_pgm_pixels([(1, 1)], maxval=255)

    def test_ppm_pixels_to_pgm_pixels_out_of_range_raises(self):
        with pytest.raises(ValueError):
            ppm.ppm_pixels_to_pgm_pixels([(300, 0, 0)], maxval=255)

    def test_convert_ppm_to_pgm(self, tmp_path):
        dest = tmp_path / "converted.pgm"
        result = ppm.convert_ppm_to_pgm(_3X1, dest)
        assert result["status"] == "success"
        assert result["dogfood"] is True
        assert result["width"] == 3 and result["height"] == 1

        import pgm as pgm_module
        pgm_img = pgm_module.parse_pgm_strict(dest)
        assert pgm_img.pixels == [0, 128, 255]


# ---------------------------------------------------------------------------
# P6 binary decode path (bundled samples are all P3 ASCII), including the
# 16-bit (maxval > 255, 2-byte samples) branch.
# ---------------------------------------------------------------------------

class TestBinaryP6Support:
    def test_p6_binary_roundtrips_same_pixels_as_ascii_equivalent(self, tmp_path):
        raw = b"P6\n2 2\n255\n" + bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255])
        dest = tmp_path / "binary.ppm"
        dest.write_bytes(raw)
        img = ppm.parse_ppm_strict(dest)
        assert img.magic == "P6"
        assert img.width == 2 and img.height == 2
        assert img.pixels == [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
        assert ppm.ppm_is_binary(dest) is True

    def test_p6_binary_16bit_samples(self, tmp_path):
        # maxval=300 (>255) forces 2-byte big-endian samples per channel.
        raw = b"P6\n1 1\n300\n" + bytes([0x01, 0x2C, 0x00, 0x0A, 0x00, 0x00])  # (300, 10, 0)
        dest = tmp_path / "wide.ppm"
        dest.write_bytes(raw)
        img = ppm.parse_ppm_strict(dest)
        assert img.maxval == 300
        assert img.pixels == [(300, 10, 0)]
        doc = ppm.PpmDocument.from_file(dest)
        assert doc.is_high_depth is True


# ---------------------------------------------------------------------------
# Analytics functions (color_image.py + ppm_image_analytics.py) — 1x1-red.ppm
# ---------------------------------------------------------------------------

class TestAnalytics1x1:
    """pixels=[(255,0,0)], width=1, height=1, maxval=255."""

    def test_red_channel_average(self):
        assert ppm.ppm_red_channel_average(_1X1) == pytest.approx(255.0)

    def test_green_and_blue_channel_average(self):
        assert ppm.ppm_green_channel_average(_1X1) == pytest.approx(0.0)
        assert ppm.ppm_blue_channel_average(_1X1) == pytest.approx(0.0)

    def test_unique_color_count(self):
        assert ppm.ppm_unique_color_count(_1X1) == 1

    def test_pixel_count(self):
        assert ppm.ppm_pixel_count(_1X1) == 1

    def test_is_binary(self):
        assert ppm.ppm_is_binary(_1X1) is False

    def test_is_grayscale(self):
        assert ppm.ppm_is_grayscale(_1X1) is False

    def test_dominant_channel(self):
        assert ppm.ppm_dominant_channel(_1X1) == "red"

    def test_is_dark(self):
        assert ppm.ppm_is_dark(_1X1) is True

    def test_has_pure_black_and_white(self):
        assert ppm.ppm_has_pure_black(_1X1) is False
        assert ppm.ppm_has_pure_white(_1X1) is False

    def test_is_monochrome_single_pixel(self):
        assert ppm.ppm_is_monochrome(_1X1) is True

    def test_max_and_min_channel_sum(self):
        assert ppm.ppm_max_channel_sum(_1X1) == 255
        assert ppm.ppm_min_channel_sum(_1X1) == 255

    def test_channel_balance(self):
        assert ppm.ppm_channel_balance(_1X1) == pytest.approx(0.0)

    def test_has_single_pixel_row_column(self):
        assert ppm.ppm_has_single_pixel(_1X1) is True
        assert ppm.ppm_has_single_row(_1X1) is True
        assert ppm.ppm_has_single_column(_1X1) is True

    def test_is_high_depth(self):
        assert ppm.ppm_is_high_depth(_1X1) is False

    def test_all_white_and_all_black(self):
        assert ppm.ppm_all_white(_1X1) is False
        assert ppm.ppm_all_black(_1X1) is False

    def test_max_channel_value_and_min_channel_value(self):
        assert ppm.ppm_max_channel_value(_1X1) == 255
        assert ppm.ppm_min_channel_value(_1X1) == 0

    def test_pixel_value_sum(self):
        assert ppm.ppm_pixel_value_sum(_1X1) == 255

    def test_channel_contrast_sum(self):
        assert ppm.ppm_channel_contrast_sum(_1X1) == 510

    def test_red_green_blue_ratio(self):
        assert ppm.ppm_red_ratio(_1X1) == pytest.approx(1.0)
        assert ppm.ppm_green_ratio(_1X1) == pytest.approx(0.0)
        assert ppm.ppm_blue_ratio(_1X1) == pytest.approx(0.0)

    def test_min_channel_avg(self):
        assert ppm.ppm_min_channel_avg(_1X1) == pytest.approx(0.0)

    def test_max_pixel_brightness(self):
        assert ppm.ppm_max_pixel_brightness(_1X1) == pytest.approx(85.0)

    def test_border_brightness(self):
        assert ppm.ppm_border_brightness(_1X1) == pytest.approx(85.0)

    def test_luminance_average(self):
        assert ppm.ppm_luminance_average(_1X1) == pytest.approx(76.245)

    def test_min_max_brightness(self):
        result = ppm.ppm_min_max_brightness(_1X1)
        assert result["min"] == pytest.approx(76.245)
        assert result["max"] == pytest.approx(76.245)

    def test_is_bright(self):
        assert ppm.ppm_is_bright(_1X1) is False

    def test_avg_brightness(self):
        assert ppm.ppm_avg_brightness(_1X1) == pytest.approx(85.0)

    def test_color_variance_single_pixel_is_zero(self):
        assert ppm.ppm_color_variance(_1X1) == 0.0

    def test_distinct_pixel_count(self):
        assert ppm.ppm_distinct_pixel_count(_1X1) == 1

    def test_width_height_maxval_magic(self):
        assert ppm.ppm_width(_1X1) == 1
        assert ppm.ppm_height(_1X1) == 1
        assert ppm.ppm_maxval(_1X1) == 255
        assert ppm.ppm_magic(_1X1) == "P3"

    def test_total_pixels(self):
        assert ppm.ppm_total_pixels(_1X1) == 1

    def test_is_standard_depth_and_ascii(self):
        assert ppm.ppm_is_standard_depth(_1X1) is True
        assert ppm.ppm_is_ascii(_1X1) is True
        # ppm_is_ascii_ppm / ppm_is_binary_ppm (ppm_stats.py) operate on the
        # neutral-model dict from parse_ppm(), not a file path.
        doc_dict = ppm.parse_ppm(_1X1)
        assert ppm.ppm_is_ascii_ppm(doc_dict) is True
        assert ppm.ppm_is_binary_ppm(doc_dict) is False

    def test_is_landscape_portrait_square(self):
        assert ppm.ppm_is_landscape(_1X1) is False
        assert ppm.ppm_is_portrait(_1X1) is False
        assert ppm.ppm_is_square(_1X1) is True

    def test_aspect_ratio(self):
        assert ppm.ppm_aspect_ratio(_1X1) == pytest.approx(1.0)
        assert ppm.ppm_aspect_ratio_from_doc({"width": 1, "height": 1}) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Analytics functions — 2x2-rgbw.ppm
# ---------------------------------------------------------------------------

class TestAnalytics2x2:
    """pixels=[(255,0,0),(0,255,0), (0,0,255),(255,255,255)], width=2, height=2."""

    def test_brightness_variance(self):
        assert ppm.ppm_brightness_variance(_2X2) == pytest.approx(5418.75)

    def test_aspect_ratio(self):
        assert ppm.ppm_aspect_ratio(_2X2) == pytest.approx(1.0)

    def test_dominant_channel_tie_breaks_to_red(self):
        assert ppm.ppm_dominant_channel(_2X2) == "red"

    def test_min_max_brightness(self):
        result = ppm.ppm_min_max_brightness(_2X2)
        assert result["min"] == pytest.approx(29.07)
        assert result["max"] == pytest.approx(255.0)

    def test_is_grayscale_false(self):
        assert ppm.ppm_is_grayscale(_2X2) is False

    def test_channel_range(self):
        assert ppm.ppm_channel_range(_2X2) == {"red": 255, "green": 255, "blue": 255}

    def test_saturation_estimate(self):
        assert ppm.ppm_saturation_estimate(_2X2) == pytest.approx(191.25)

    def test_is_dark(self):
        assert ppm.ppm_is_dark(_2X2) is True

    def test_red_green_blue_channel_sum(self):
        assert ppm.ppm_red_channel_sum(_2X2) == 510
        assert ppm.ppm_green_channel_sum(_2X2) == 510
        assert ppm.ppm_blue_channel_sum(_2X2) == 510

    def test_luminance_average(self):
        assert ppm.ppm_luminance_average(_2X2) == pytest.approx(127.5)

    def test_row_count_and_column_count(self):
        assert ppm.ppm_row_count(_2X2) == 2
        assert ppm.ppm_column_count(_2X2) == 2

    def test_perimeter(self):
        assert ppm.ppm_perimeter(_2X2) == 8

    def test_dimension_ratio(self):
        assert ppm.ppm_dimension_ratio(_2X2) == pytest.approx(1.0)

    def test_is_square_landscape(self):
        assert ppm.ppm_is_square(_2X2) is True
        assert ppm.ppm_is_landscape(_2X2) is False

    def test_max_dimension_min_dimension(self):
        assert ppm.ppm_max_dimension(_2X2) == 2
        assert ppm.ppm_min_dimension(_2X2) == 2

    def test_has_pure_black_and_white(self):
        assert ppm.ppm_has_pure_black(_2X2) is False
        assert ppm.ppm_has_pure_white(_2X2) is True

    def test_max_channel_sum_and_min_channel_sum(self):
        assert ppm.ppm_max_channel_sum(_2X2) == 765
        assert ppm.ppm_min_channel_sum(_2X2) == 255

    def test_megapixels(self):
        assert ppm.ppm_megapixels(_2X2) == pytest.approx(4e-6)

    def test_channel_balance(self):
        assert ppm.ppm_channel_balance(_2X2) == pytest.approx(1.0)

    def test_is_tall_and_portrait_false(self):
        assert ppm.ppm_is_tall(_2X2) is False
        assert ppm.ppm_is_portrait(_2X2) is False

    def test_diagonal(self):
        assert ppm.ppm_diagonal(_2X2) == pytest.approx(math.sqrt(8))

    def test_is_monochrome_false(self):
        assert ppm.ppm_is_monochrome(_2X2) is False

    def test_total_channel_sum(self):
        assert ppm.ppm_total_channel_sum(_2X2) == 1530

    def test_avg_brightness(self):
        assert ppm.ppm_avg_brightness(_2X2) == pytest.approx(127.5)

    def test_color_variance(self):
        assert ppm.ppm_color_variance(_2X2) == pytest.approx(5418.75)

    def test_distinct_pixel_count(self):
        assert ppm.ppm_distinct_pixel_count(_2X2) == 4

    def test_red_green_blue_ratio(self):
        assert ppm.ppm_red_ratio(_2X2) == pytest.approx(1 / 3)
        assert ppm.ppm_green_ratio(_2X2) == pytest.approx(1 / 3)
        assert ppm.ppm_blue_ratio(_2X2) == pytest.approx(1 / 3)

    def test_border_brightness(self):
        assert ppm.ppm_border_brightness(_2X2) == pytest.approx(127.5)

    def test_pixel_brightness_range(self):
        assert ppm.ppm_pixel_brightness_range(_2X2) == pytest.approx(170 / 255)

    def test_is_bright_false(self):
        assert ppm.ppm_is_bright(_2X2) is False

    def test_normalized_brightness(self):
        assert ppm.ppm_normalized_brightness(_2X2) == pytest.approx(0.5)

    def test_area(self):
        assert ppm.ppm_area(_2X2) == 4

    def test_min_channel_avg(self):
        assert ppm.ppm_min_channel_avg(_2X2) == pytest.approx(127.5)

    def test_max_pixel_brightness(self):
        assert ppm.ppm_max_pixel_brightness(_2X2) == pytest.approx(255.0)

    def test_max_channel_value_and_min_channel_value(self):
        assert ppm.ppm_max_channel_value(_2X2) == 255
        assert ppm.ppm_min_channel_value(_2X2) == 0

    def test_pixel_value_sum(self):
        assert ppm.ppm_pixel_value_sum(_2X2) == 1530

    def test_channel_contrast_sum(self):
        assert ppm.ppm_channel_contrast_sum(_2X2) == 1530

    def test_red_green_blue_channel_ratio(self):
        assert ppm.ppm_red_channel_ratio(_2X2) == pytest.approx(1 / 3)
        assert ppm.ppm_green_channel_ratio(_2X2) == pytest.approx(1 / 3)
        assert ppm.ppm_blue_channel_ratio(_2X2) == pytest.approx(1 / 3)

    def test_has_single_pixel_row_column_false(self):
        assert ppm.ppm_has_single_pixel(_2X2) is False
        assert ppm.ppm_has_single_row(_2X2) is False
        assert ppm.ppm_has_single_column(_2X2) is False

    def test_all_white_and_all_black_false(self):
        assert ppm.ppm_all_white(_2X2) is False
        assert ppm.ppm_all_black(_2X2) is False

    def test_is_standard_depth(self):
        assert ppm.ppm_is_standard_depth(_2X2) is True

    def test_pixel_density_is_positive_float(self):
        assert isinstance(ppm.ppm_pixel_density(_2X2), float)
        assert ppm.ppm_pixel_density(_2X2) > 0


# ---------------------------------------------------------------------------
# Analytics functions — 3x1-gradient.ppm (grayscale-valued RGB image)
# ---------------------------------------------------------------------------

class TestAnalytics3x1:
    """pixels=[(0,0,0),(128,128,128),(255,255,255)], width=3, height=1."""

    def test_is_grayscale_true(self):
        assert ppm.ppm_is_grayscale(_3X1) is True

    def test_has_pure_black_and_white(self):
        assert ppm.ppm_has_pure_black(_3X1) is True
        assert ppm.ppm_has_pure_white(_3X1) is True

    def test_all_white_and_all_black_false(self):
        assert ppm.ppm_all_white(_3X1) is False
        assert ppm.ppm_all_black(_3X1) is False

    def test_is_monochrome_false(self):
        assert ppm.ppm_is_monochrome(_3X1) is False

    def test_dominant_channel_tie(self):
        assert ppm.ppm_dominant_channel(_3X1) == "red"

    def test_max_channel_sum_and_min_channel_sum(self):
        assert ppm.ppm_max_channel_sum(_3X1) == 765
        assert ppm.ppm_min_channel_sum(_3X1) == 0

    def test_row_count_column_count(self):
        assert ppm.ppm_row_count(_3X1) == 1
        assert ppm.ppm_column_count(_3X1) == 3

    def test_is_landscape_and_has_single_row(self):
        assert ppm.ppm_is_landscape(_3X1) is True
        assert ppm.ppm_has_single_row(_3X1) is True
        assert ppm.ppm_has_single_column(_3X1) is False
        assert ppm.ppm_has_single_pixel(_3X1) is False

    def test_channel_contrast_sum_is_zero_for_grayscale(self):
        assert ppm.ppm_channel_contrast_sum(_3X1) == 0

    def test_saturation_estimate_is_zero_for_grayscale(self):
        assert ppm.ppm_saturation_estimate(_3X1) == pytest.approx(0.0)

    def test_channel_balance_is_perfect(self):
        assert ppm.ppm_channel_balance(_3X1) == pytest.approx(1.0)

    def test_is_dark(self):
        assert ppm.ppm_is_dark(_3X1) is True  # avg 127.667 < 128

    def test_luminance_average(self):
        assert ppm.ppm_luminance_average(_3X1) == pytest.approx(383 / 3)

    def test_min_max_brightness(self):
        result = ppm.ppm_min_max_brightness(_3X1)
        assert result["min"] == pytest.approx(0.0)
        assert result["max"] == pytest.approx(255.0)

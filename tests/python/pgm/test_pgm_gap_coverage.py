"""Gap-coverage tests for the pgm (Portable Graymap) format.

Exercises every symbol exported from ``pgm/__init__.py`` (the ``pgm.__all__``
surface) that is thinly covered — or not covered at all — by the rest of the
tests/python/pgm/ suite: analytics functions, geometry transforms, the
parser-level exception hierarchy, the PgmDocument domain model properties,
the graymap iterator, the installed-workflow shim, and the dogfood
PGM->PPM converter.

Sample fixtures (hand-verified pixel data, from samples/by-format/pgm/valid/):
    1x1-white.pgm   : P2, 1x1, maxval=255, pixels=[255]
    2x2-gradient.pgm: P2, 2x2, maxval=255, pixels=[0,85, 170,255]  (row0=[0,85], row1=[170,255])
    3x1-ramp.pgm    : P2, 3x1, maxval=255, pixels=[0,128,255]

Notable characterization: ``pgm.PgmError`` (re-exported from
``pgm.exceptions``, a facade over ``_shared.FormatFactoryError``) is a
*different class* from ``pgm.pgm_parser.PgmError`` (the base class actually
raised by ``parse_pgm_strict`` and its ``PgmInvalid*``/``PgmSize``/``PgmDecode``
subclasses). ``pytest.raises(pgm.PgmError)`` therefore does NOT catch parser
failures — this file documents and asserts that behavior explicitly.

Note: ``pgm/pgm_image_analytics.py`` defines a further set of ``pgm_*``
helpers (pgm_width, pgm_height, pgm_magic, pgm_is_single_pixel, ...) but that
module is never imported by ``pgm/__init__.py`` and so none of its names
reach ``pgm.__all__`` — it is intentionally out of scope here since this file
targets the *exported* API surface.
"""
from __future__ import annotations

import math
import sys
import types
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pgm
from pgm.pgm_parser import PgmError as PgmParserError

_SAMPLES = _REPO / "samples" / "by-format" / "pgm"
_1X1 = _SAMPLES / "valid" / "1x1-white.pgm"
_2X2 = _SAMPLES / "valid" / "2x2-gradient.pgm"
_3X1 = _SAMPLES / "valid" / "3x1-ramp.pgm"
_INVALID_MAGIC = _SAMPLES / "invalid" / "wrong-magic.pgm"


# ---------------------------------------------------------------------------
# parse_pgm / parse_pgm_strict / probe_pgm
# ---------------------------------------------------------------------------

class TestParsePgm:
    def test_parse_pgm_ok_true_on_valid(self):
        result = pgm.parse_pgm(_2X2)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["maxval"] == 255
        assert result["magic"] == "P2"
        assert result["pixel_count"] == 4

    def test_parse_pgm_ok_false_on_missing(self):
        result = pgm.parse_pgm(_SAMPLES / "does-not-exist.pgm")
        assert result["ok"] is False
        assert result["error_type"] == "PgmError"

    def test_parse_pgm_ok_false_on_invalid_magic(self):
        result = pgm.parse_pgm(_INVALID_MAGIC)
        assert result["ok"] is False
        assert result["error_type"] == "PgmInvalidMagicError"

    def test_parse_pgm_strict_returns_pgmimage(self):
        img = pgm.parse_pgm_strict(_3X1)
        assert isinstance(img, pgm.PgmImage)
        assert img.width == 3
        assert img.height == 1
        assert img.pixels == [0, 128, 255]
        assert img.maxval == 255

    def test_parse_pgm_strict_missing_file_raises_parser_pgmerror(self):
        with pytest.raises(PgmParserError, match="File not found"):
            pgm.parse_pgm_strict(_SAMPLES / "nope.pgm")

    def test_parse_pgm_strict_invalid_magic_raises_specific_subclass(self):
        with pytest.raises(pgm.PgmInvalidMagicError):
            pgm.parse_pgm_strict(_INVALID_MAGIC)

    def test_exported_pgmerror_does_not_catch_parser_failures(self):
        """Characterization: the facade PgmError (exceptions.py) is a
        distinct class from pgm_parser.PgmError, so it must NOT catch
        parser-raised exceptions."""
        with pytest.raises(PgmParserError):
            try:
                pgm.parse_pgm_strict(_INVALID_MAGIC)
            except pgm.PgmError:
                pytest.fail("pgm.PgmError unexpectedly caught a parser error")
            except PgmParserError:
                raise

    def test_probe_pgm_missing_file(self):
        result = pgm.probe_pgm(_SAMPLES / "absent.pgm")
        assert result["exists"] is False

    def test_probe_pgm_valid_header(self):
        result = pgm.probe_pgm(_2X2)
        assert result["valid_header"] is True
        assert result["magic"] == "P2"
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["maxval"] == 255

    def test_probe_pgm_invalid_magic(self):
        result = pgm.probe_pgm(_INVALID_MAGIC)
        assert result["valid_header"] is False

    def test_get_dimensions(self):
        assert pgm.get_dimensions(_3X1) == (3, 1)

    def test_pixel_count(self):
        assert pgm.pixel_count(_3X1) == 3

    def test_image_pixel_stats(self):
        stats = pgm.image_pixel_stats(_2X2)
        assert stats["ok"] is True
        assert stats["min_value"] == 0
        assert stats["max_value"] == 255
        assert stats["mean_approx"] == pytest.approx(127.5)
        assert stats["total_pixels"] == 4


class TestGetCapabilities:
    def test_get_capabilities_shape(self):
        caps = pgm.get_capabilities()
        assert caps["format"] == "pgm"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert "p2_ascii_parse" in caps["supported"]
        assert "ppm_color" in caps["unsupported"]

    def test_supported_unsupported_constants(self):
        assert "p5_binary_parse" in pgm.SUPPORTED_FEATURES
        assert "16bit_values" in pgm.UNSUPPORTED_FEATURES

    def test_magic_constants(self):
        assert pgm.PGM_MAGIC_ASCII == "P2"
        assert pgm.PGM_MAGIC_BINARY == "P5"

    def test_size_constants(self):
        assert pgm.MAX_FILE_SIZE == 64 * 1024 * 1024
        assert pgm.MAX_DIMENSION == 65536
        assert pgm.MAX_MAXVAL == 65535


# ---------------------------------------------------------------------------
# write_pgm
# ---------------------------------------------------------------------------

class TestWritePgm:
    def test_roundtrip(self, tmp_path):
        dest = tmp_path / "out.pgm"
        pgm.write_pgm([0, 85, 170, 255], 2, 2, 255, dest)
        img = pgm.parse_pgm_strict(dest)
        assert img.width == 2 and img.height == 2
        assert img.pixels == [0, 85, 170, 255]
        assert img.magic == "P2"

    def test_mismatched_length_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            pgm.write_pgm([1, 2], 2, 2, 255, tmp_path / "bad.pgm")

    def test_maxval_out_of_range_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            pgm.write_pgm([1], 1, 1, 0, tmp_path / "bad2.pgm")

    def test_oversized_dimension_raises_size_error(self, tmp_path):
        with pytest.raises(pgm.PgmSizeError):
            pgm.write_pgm([], 70000, 1, 255, tmp_path / "huge.pgm")

    def test_comment_is_sanitized(self, tmp_path):
        dest = tmp_path / "commented.pgm"
        pgm.write_pgm([1, 2], 2, 1, 255, dest, comment="hi\nthere\r!")
        lines = dest.read_text(encoding="ascii").splitlines()
        assert lines[0] == "P2"
        assert lines[1].startswith("#")
        assert "\n" not in lines[1] and "\r" not in lines[1]


# ---------------------------------------------------------------------------
# Geometry / pixel-domain transforms
# ---------------------------------------------------------------------------

class TestGeometryTransforms:
    def test_average_gray(self):
        assert pgm.average_gray(_2X2) == pytest.approx(127.5)

    def test_count_above_threshold(self):
        assert pgm.count_above_threshold(_2X2, 100) == 2

    def test_min_max_gray(self):
        assert pgm.min_max_gray(_2X2) == (0, 255)

    def test_flip_horizontal(self, tmp_path):
        dest = tmp_path / "flipped.pgm"
        result = pgm.flip_horizontal(_2X2, dest)
        assert result["ok"] is True
        img = pgm.parse_pgm_strict(dest)
        assert img.pixels == [85, 0, 255, 170]

    def test_normalize(self, tmp_path):
        dest = tmp_path / "normalized.pgm"
        result = pgm.normalize(_2X2, dest, new_maxval=100)
        assert result["ok"] is True
        assert result["old_maxval"] == 255
        assert result["new_maxval"] == 100
        img = pgm.parse_pgm_strict(dest)
        assert img.maxval == 100
        assert img.pixels[0] == 0
        assert img.pixels[3] == 100

    def test_normalize_invalid_maxval_raises(self, tmp_path):
        with pytest.raises(ValueError):
            pgm.normalize(_2X2, tmp_path / "x.pgm", new_maxval=0)

    def test_histogram(self):
        result = pgm.histogram(_2X2)
        assert result["ok"] is True
        assert result["unique_values"] == 4
        assert result["histogram"] == {0: 1, 85: 1, 170: 1, 255: 1}

    def test_threshold(self, tmp_path):
        dest = tmp_path / "thresholded.pgm"
        result = pgm.threshold(_2X2, dest, value=100)
        assert result["above_count"] == 2
        assert result["below_count"] == 2
        img = pgm.parse_pgm_strict(dest)
        assert img.maxval == 1
        assert img.pixels == [0, 0, 1, 1]

    def test_rotate_90(self, tmp_path):
        dest = tmp_path / "rotated.pgm"
        result = pgm.rotate_90(_2X2, dest)
        assert result["width"] == 2
        assert result["height"] == 2
        img = pgm.parse_pgm_strict(dest)
        # (row,col) -> (col, height-1-row): (0,0)->(0,1) 0; (0,1)->(1,1) 85;
        # (1,0)->(0,0) 170; (1,1)->(1,0) 255
        assert img.pixels == [170, 0, 255, 85]

    def test_grayscale_variance(self):
        # mean=127.5; variance = ((0-127.5)^2+(85-127.5)^2+(170-127.5)^2+(255-127.5)^2)/4
        assert pgm.grayscale_variance(_2X2) == pytest.approx(9031.25)


# ---------------------------------------------------------------------------
# Parser-level exception hierarchy (raised by parse_pgm_strict internals)
# ---------------------------------------------------------------------------

class TestParserExceptionHierarchy:
    def test_all_specific_errors_are_parser_pgmerror_subclasses(self):
        for cls in (
            pgm.PgmInvalidMagicError,
            pgm.PgmInvalidHeaderError,
            pgm.PgmSizeError,
            pgm.PgmDecodeError,
        ):
            assert issubclass(cls, PgmParserError)

    def test_incomplete_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "incomplete.pgm"
        bad.write_text("P2\n5 5\n", encoding="ascii")
        with pytest.raises(pgm.PgmInvalidHeaderError):
            pgm.parse_pgm_strict(bad)

    def test_non_integer_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "nonint.pgm"
        bad.write_text("P2\nabc 5 255\n1 1 1 1 1\n", encoding="ascii")
        with pytest.raises(pgm.PgmInvalidHeaderError):
            pgm.parse_pgm_strict(bad)

    def test_oversized_dimensions_raise_size_error(self, tmp_path):
        bad = tmp_path / "oversized.pgm"
        bad.write_text("P2\n70000 1\n255\n", encoding="ascii")
        with pytest.raises(pgm.PgmSizeError):
            pgm.parse_pgm_strict(bad)

    def test_invalid_maxval_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "badmaxval.pgm"
        bad.write_text("P2\n1 1\n0\n0\n", encoding="ascii")
        with pytest.raises(pgm.PgmInvalidHeaderError):
            pgm.parse_pgm_strict(bad)

    def test_insufficient_pixel_data_raises_decode_error(self, tmp_path):
        bad = tmp_path / "short.pgm"
        bad.write_text("P2\n2 2\n255\n1 2 3\n", encoding="ascii")
        with pytest.raises(pgm.PgmDecodeError):
            pgm.parse_pgm_strict(bad)

    def test_out_of_range_pixel_value_raises_decode_error(self, tmp_path):
        bad = tmp_path / "outofrange.pgm"
        bad.write_text("P2\n1 1\n10\n999\n", encoding="ascii")
        with pytest.raises(pgm.PgmDecodeError):
            pgm.parse_pgm_strict(bad)

    def test_zero_dimension_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "zerodim.pgm"
        bad.write_text("P2\n0 5\n255\n", encoding="ascii")
        with pytest.raises(pgm.PgmInvalidHeaderError):
            pgm.parse_pgm_strict(bad)


class TestFacadeExceptionHierarchy:
    """The exceptions.py facade classes (PgmParseError/PgmWriteError/PgmError
    -> FormatFactoryError). Complements test_exception_coverage.py by adding
    FormatFactoryError-level assertions."""

    def test_format_factory_error_is_exception(self):
        assert issubclass(pgm.FormatFactoryError, Exception)

    def test_format_factory_error_is_raisable(self):
        with pytest.raises(pgm.FormatFactoryError):
            raise pgm.FormatFactoryError("boom")

    def test_pgmerror_inherits_format_factory_error(self):
        assert issubclass(pgm.PgmError, pgm.FormatFactoryError)

    def test_pgmparseerror_and_pgmwriteerror_inherit_pgmerror(self):
        assert issubclass(pgm.PgmParseError, pgm.PgmError)
        assert issubclass(pgm.PgmWriteError, pgm.PgmError)

    def test_pgmerror_caught_as_format_factory_error(self):
        with pytest.raises(pgm.FormatFactoryError):
            raise pgm.PgmError("generic failure")


# ---------------------------------------------------------------------------
# PgmImage dataclass
# ---------------------------------------------------------------------------

class TestPgmImageDataclass:
    def test_defaults(self):
        img = pgm.PgmImage()
        assert img.spec_qname == "pgm:image"
        assert img.width == 0
        assert img.height == 0
        assert img.maxval == 255
        assert img.magic == "P2"
        assert img.pixels == []
        assert img.path == ""

    def test_field_assignment(self):
        img = pgm.PgmImage(width=4, height=5, maxval=100, magic="P5", pixels=[1, 0], path="x.pgm")
        assert (img.width, img.height, img.maxval, img.magic) == (4, 5, 100, "P5")


# ---------------------------------------------------------------------------
# PgmDocument domain model — properties not covered by test_pgm_domain_model.py
# ---------------------------------------------------------------------------

class TestPgmDocumentProperties:
    def test_square_image_properties(self):
        doc = pgm.PgmDocument.from_file(_2X2)
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
        assert doc.magic == "P2"
        assert doc.maxval == 255
        assert doc.pixel_count == 4

    def test_landscape_image_properties(self):
        doc = pgm.PgmDocument.from_file(_3X1)
        assert doc.is_landscape is True
        assert doc.is_square is False
        assert doc.aspect_ratio == pytest.approx(3.0)
        assert doc.edge_ratio == pytest.approx(3.0)
        assert doc.is_narrow is False  # exactly 3.0, not > 3.0
        assert doc.is_large_image is False

    def test_narrow_banner_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=100, height=5, maxval=255, magic="P2", pixels=[], path="fake")
        doc = pgm.PgmDocument(fake)
        assert doc.edge_ratio == pytest.approx(20.0)
        assert doc.is_narrow is True
        assert doc.is_landscape is True
        assert doc.is_banner is True
        assert doc.is_tall_strip is False

    def test_tall_strip_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=5, height=100, maxval=65535, magic="P5", pixels=[], path="fake")
        doc = pgm.PgmDocument(fake)
        assert doc.is_narrow is True
        assert doc.is_portrait is True
        assert doc.is_tall_strip is True
        assert doc.is_banner is False
        assert doc.is_binary is True
        assert doc.is_high_depth is True

    def test_large_image_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=2000, height=2000, maxval=255, magic="P2", pixels=[], path="fake")
        doc = pgm.PgmDocument(fake)
        assert doc.is_large_image is True
        assert doc.megapixels == pytest.approx(4.0)
        assert doc.is_tiny is False
        assert doc.is_micro is False

    def test_pixel_density_class_thresholds(self):
        for edge, expected in ((64, "micro"), (256, "small"), (1024, "medium"), (2048, "large")):
            fake = types.SimpleNamespace(width=edge, height=1, maxval=255, magic="P2", pixels=[], path="f")
            assert pgm.PgmDocument(fake).pixel_density_class == expected

    def test_zero_height_aspect_ratio_is_zero(self):
        fake = types.SimpleNamespace(width=5, height=0, maxval=255, magic="P2", pixels=[], path="f")
        doc = pgm.PgmDocument(fake)
        assert doc.aspect_ratio == 0.0
        assert doc.edge_ratio == 1.0

    def test_set_pixel_roundtrip(self, tmp_path):
        doc = pgm.PgmDocument.from_file(_2X2)
        doc.set_pixel(0, 50)
        out = tmp_path / "mutated.pgm"
        doc.save_to_file(out)
        reread = pgm.parse_pgm_strict(out)
        assert reread.pixels[0] == 50
        assert reread.pixels[1:] == [85, 170, 255]

    def test_set_pixel_out_of_range_raises(self):
        doc = pgm.PgmDocument.from_file(_2X2)
        with pytest.raises(PgmParserError):
            doc.set_pixel(99, 1)

    def test_save_to_file_empty_path_raises(self):
        doc = pgm.PgmDocument.from_file(_2X2)
        with pytest.raises(PgmParserError):
            doc.save_to_file("")

    def test_to_dict_full_contents(self):
        doc = pgm.PgmDocument.from_file(_3X1)
        d = doc.to_dict()
        assert d == {
            "width": 3,
            "height": 1,
            "maxval": 255,
            "pixel_count": 3,
            "magic": "P2",
            "path": doc.path,
        }

    def test_repr_contains_dimensions_maxval_and_magic(self):
        doc = pgm.PgmDocument.from_file(_2X2)
        r = repr(doc)
        assert "width=2" in r and "height=2" in r and "maxval=255" in r and "P2" in r


# ---------------------------------------------------------------------------
# pgm_iter_graymaps (spec-shaped graymap iterator)
# ---------------------------------------------------------------------------

class TestIterGraymaps:
    def test_yields_single_graymap(self):
        graymaps = list(pgm.pgm_iter_graymaps(_2X2))
        assert len(graymaps) == 1

    def test_graymap_shape(self):
        gm = next(pgm.pgm_iter_graymaps(_3X1))
        assert gm.width == 3
        assert gm.height == 1
        assert gm.pixel_count == 3
        assert gm.spec_qname == "pgm:graymap"

    def test_graymap_to_dict_and_repr(self):
        gm = next(pgm.pgm_iter_graymaps(_1X1))
        d = gm.to_dict()
        assert d["width"] == 1 and d["height"] == 1
        assert d["maxval"] == 255
        assert "Graymap(" in repr(gm)


# ---------------------------------------------------------------------------
# pgm_installed_workflow
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    def test_workflow_on_valid_file(self):
        result = pgm.pgm_installed_workflow(_3X1)
        assert result == {
            "format": "pgm",
            "loaded": True,
            "width": 3,
            "height": 1,
            "pixel_count": 3,
        }

    def test_workflow_on_missing_file_reports_not_loaded(self):
        result = pgm.pgm_installed_workflow(_SAMPLES / "missing.pgm")
        assert result["format"] == "pgm"
        assert result["loaded"] is False
        assert result["width"] == 0
        assert result["height"] == 0


# ---------------------------------------------------------------------------
# Dogfood conversion: PGM -> PPM
# ---------------------------------------------------------------------------

class TestDogfoodConversion:
    def test_pgm_pixels_to_ppm_pixels(self):
        result = pgm.pgm_pixels_to_ppm_pixels([0, 128, 255])
        assert result == [(0, 0, 0), (128, 128, 128), (255, 255, 255)]

    def test_pgm_pixels_to_ppm_pixels_invalid_maxval_raises(self):
        with pytest.raises(ValueError):
            pgm.pgm_pixels_to_ppm_pixels([1], maxval=0)

    def test_convert_pgm_to_ppm(self, tmp_path):
        dest = tmp_path / "converted.ppm"
        result = pgm.convert_pgm_to_ppm(_2X2, dest, maxval=255)
        assert result["status"] == "success"
        assert result["dogfood"] is True
        assert result["width"] == 2 and result["height"] == 2

        import ppm as ppm_module
        ppm_img = ppm_module.parse_ppm_strict(dest)
        assert ppm_img.pixels == [
            (0, 0, 0), (85, 85, 85),
            (170, 170, 170), (255, 255, 255),
        ]


# ---------------------------------------------------------------------------
# P5 binary decode path (bundled samples are all P2 ASCII), including the
# 16-bit (maxval > 255, 2-byte samples) branch.
# ---------------------------------------------------------------------------

class TestBinaryP5Support:
    def test_p5_binary_roundtrips_same_pixels_as_ascii_equivalent(self, tmp_path):
        raw = b"P5\n2 2\n255\n" + bytes([0, 85, 170, 255])
        dest = tmp_path / "binary.pgm"
        dest.write_bytes(raw)
        img = pgm.parse_pgm_strict(dest)
        assert img.magic == "P5"
        assert img.width == 2 and img.height == 2
        assert img.pixels == [0, 85, 170, 255]

    def test_p5_binary_16bit_samples(self, tmp_path):
        # maxval=300 (>255) forces 2-byte big-endian samples.
        raw = b"P5\n1 1\n300\n" + bytes([0x01, 0x2C])  # 0x012C == 300
        dest = tmp_path / "wide.pgm"
        dest.write_bytes(raw)
        img = pgm.parse_pgm_strict(dest)
        assert img.maxval == 300
        assert img.pixels == [300]
        doc = pgm.PgmDocument.from_file(dest)
        assert doc.is_high_depth is True


# ---------------------------------------------------------------------------
# Analytics functions (grayscale_image.py) — 1x1-white.pgm
# ---------------------------------------------------------------------------

class TestAnalytics1x1:
    """pixels=[255], width=1, height=1, maxval=255 (saturated single pixel)."""

    def test_bright_pixel_ratio(self):
        assert pgm.pgm_bright_pixel_ratio(_1X1) == pytest.approx(1.0)

    def test_dark_pixel_count(self):
        assert pgm.pgm_dark_pixel_count(_1X1) == 0

    def test_max_and_min_pixel_value(self):
        assert pgm.pgm_max_pixel_value(_1X1) == 255
        assert pgm.pgm_min_pixel_value(_1X1) == 255

    def test_average_brightness(self):
        assert pgm.pgm_average_brightness(_1X1) == pytest.approx(255.0)

    def test_contrast_range_zero_for_single_pixel(self):
        assert pgm.pgm_contrast_range(_1X1) == 0

    def test_is_uniform(self):
        assert pgm.pgm_is_uniform(_1X1) is True

    def test_has_any_saturated(self):
        assert pgm.pgm_has_any_saturated(_1X1) is True

    def test_is_all_bright(self):
        assert pgm.pgm_is_all_bright(_1X1) is True

    def test_is_all_dark(self):
        assert pgm.pgm_is_all_dark(_1X1) is False

    def test_is_bright(self):
        assert pgm.pgm_is_bright(_1X1) is True

    def test_midpoint_gray(self):
        assert pgm.pgm_midpoint_gray(_1X1) == 127

    def test_unique_value_count(self):
        assert pgm.pgm_unique_value_count(_1X1) == 1

    def test_zero_pixel_count(self):
        assert pgm.pgm_zero_pixel_count(_1X1) == 0

    def test_saturated_pixel_count(self):
        assert pgm.pgm_saturated_pixel_count(_1X1) == 1

    def test_edge_pixel_mean(self):
        assert pgm.pgm_edge_pixel_mean(_1X1) == pytest.approx(255.0)

    def test_shadow_pixel_count(self):
        assert pgm.pgm_shadow_pixel_count(_1X1) == 0

    def test_pixel_range(self):
        assert pgm.pgm_pixel_range(_1X1) == 0

    def test_pixel_median(self):
        assert pgm.pgm_pixel_median(_1X1) == 255

    def test_maxval(self):
        assert pgm.pgm_maxval(_1X1) == 255


# ---------------------------------------------------------------------------
# Analytics functions — 2x2-gradient.pgm
# ---------------------------------------------------------------------------

class TestAnalytics2x2:
    """pixels=[0,85, 170,255], width=2, height=2, maxval=255."""

    def test_median_pixel_value(self):
        assert pgm.pgm_median_pixel_value(_2X2) == 85

    def test_total_pixel_count(self):
        assert pgm.pgm_total_pixel_count(_2X2) == 4

    def test_brightness_quartiles(self):
        assert pgm.pgm_brightness_quartiles(_2X2) == {"q25": 85, "q50": 170, "q75": 255}

    def test_nonzero_pixel_ratio(self):
        assert pgm.pgm_nonzero_pixel_ratio(_2X2) == pytest.approx(0.75)

    def test_dynamic_range(self):
        assert pgm.pgm_dynamic_range(_2X2) == 255

    def test_pixel_sum(self):
        assert pgm.pgm_pixel_sum(_2X2) == 510

    def test_standard_deviation(self):
        assert pgm.pgm_standard_deviation(_2X2) == pytest.approx(math.sqrt(9031.25))

    def test_brightness_ratio(self):
        assert pgm.pgm_brightness_ratio(_2X2) == pytest.approx(0.5)

    def test_perimeter(self):
        assert pgm.pgm_perimeter(_2X2) == 8

    def test_unique_value_count(self):
        assert pgm.pgm_unique_value_count(_2X2) == 4

    def test_dimension_ratio(self):
        assert pgm.pgm_dimension_ratio(_2X2) == pytest.approx(1.0)

    def test_is_square(self):
        assert pgm.pgm_is_square(_2X2) is True

    def test_is_landscape(self):
        assert pgm.pgm_is_landscape(_2X2) is False

    def test_max_dimension(self):
        assert pgm.pgm_max_dimension(_2X2) == 2

    def test_has_any_zero(self):
        assert pgm.pgm_has_any_zero(_2X2) is True

    def test_diagonal(self):
        assert pgm.pgm_diagonal(_2X2) == pytest.approx(math.sqrt(8))

    def test_aspect_ratio(self):
        assert pgm.pgm_aspect_ratio(_2X2) == pytest.approx(1.0)

    def test_min_dimension(self):
        assert pgm.pgm_min_dimension(_2X2) == 2

    def test_brightness_range(self):
        assert pgm.pgm_brightness_range(_2X2) == 255

    def test_area(self):
        assert pgm.pgm_area(_2X2) == 4

    def test_mean_brightness(self):
        assert pgm.pgm_mean_brightness(_2X2) == pytest.approx(127.5)

    def test_megapixels(self):
        assert pgm.pgm_megapixels(_2X2) == pytest.approx(4e-6)

    def test_is_tall_and_wide_false(self):
        assert pgm.pgm_is_tall(_2X2) is False
        assert pgm.pgm_is_wide(_2X2) is False

    def test_column_count_and_row_count(self):
        assert pgm.pgm_column_count(_2X2) == 2
        assert pgm.pgm_row_count(_2X2) == 2

    def test_is_portrait_false(self):
        assert pgm.pgm_is_portrait(_2X2) is False

    def test_is_high_contrast(self):
        assert pgm.pgm_is_high_contrast(_2X2) is True

    def test_avg_row_brightness(self):
        assert pgm.pgm_avg_row_brightness(_2X2) == pytest.approx([42.5, 212.5])

    def test_dark_pixel_ratio(self):
        assert pgm.pgm_dark_pixel_ratio(_2X2) == pytest.approx(0.5)

    def test_row_brightness_variance(self):
        assert pgm.pgm_row_brightness_variance(_2X2) == pytest.approx(7225.0)

    def test_min_brightness(self):
        assert pgm.pgm_min_brightness(_2X2) == 0

    def test_is_bright_false(self):
        assert pgm.pgm_is_bright(_2X2) is False

    def test_brightness_histogram(self):
        assert pgm.pgm_brightness_histogram(_2X2) == [1, 1, 1, 1]

    def test_contrast_ratio(self):
        assert pgm.pgm_contrast_ratio(_2X2) == pytest.approx(1.0)

    def test_saturated_pixel_ratio(self):
        assert pgm.pgm_saturated_pixel_ratio(_2X2) == pytest.approx(0.25)

    def test_normalized_mean(self):
        assert pgm.pgm_normalized_mean(_2X2) == pytest.approx(0.5)

    def test_above_mean_ratio(self):
        assert pgm.pgm_above_mean_ratio(_2X2) == pytest.approx(0.5)

    def test_median_brightness(self):
        assert pgm.pgm_median_brightness(_2X2) == pytest.approx(127.5)

    def test_pixel_value_range(self):
        assert pgm.pgm_pixel_value_range(_2X2) == 255

    def test_pixel_range(self):
        assert pgm.pgm_pixel_range(_2X2) == 255

    def test_shadow_pixel_count(self):
        assert pgm.pgm_shadow_pixel_count(_2X2) == 1

    def test_pixel_median(self):
        assert pgm.pgm_pixel_median(_2X2) == pytest.approx(127.5)

    def test_edge_pixel_mean(self):
        assert pgm.pgm_edge_pixel_mean(_2X2) == pytest.approx(127.5)

    def test_row_intensity_variance(self):
        assert pgm.pgm_row_intensity_variance(_2X2) == pytest.approx(7225.0)

    def test_pixel_density_is_positive_float(self):
        assert isinstance(pgm.pgm_pixel_density(_2X2), float)
        assert pgm.pgm_pixel_density(_2X2) > 0


# ---------------------------------------------------------------------------
# Analytics functions — 3x1-ramp.pgm (single-row / landscape / wide case)
# ---------------------------------------------------------------------------

class TestAnalytics3x1:
    """pixels=[0,128,255], width=3, height=1, maxval=255."""

    def test_is_landscape(self):
        assert pgm.pgm_is_landscape(_3X1) is True

    def test_row_count_and_column_count(self):
        assert pgm.pgm_row_count(_3X1) == 1
        assert pgm.pgm_column_count(_3X1) == 3

    def test_dimension_ratio_and_aspect_ratio(self):
        assert pgm.pgm_dimension_ratio(_3X1) == pytest.approx(3.0)
        assert pgm.pgm_aspect_ratio(_3X1) == pytest.approx(3.0)

    def test_max_and_min_dimension(self):
        assert pgm.pgm_max_dimension(_3X1) == 3
        assert pgm.pgm_min_dimension(_3X1) == 1

    def test_is_tall_false(self):
        assert pgm.pgm_is_tall(_3X1) is False

    def test_is_wide_true(self):
        assert pgm.pgm_is_wide(_3X1) is True

    def test_avg_row_brightness_single_row(self):
        assert pgm.pgm_avg_row_brightness(_3X1) == pytest.approx([383 / 3])

    def test_row_brightness_variance_single_row_is_zero(self):
        assert pgm.pgm_row_brightness_variance(_3X1) == 0.0

    def test_row_intensity_variance_single_row_is_zero(self):
        assert pgm.pgm_row_intensity_variance(_3X1) == 0.0

    def test_perimeter(self):
        assert pgm.pgm_perimeter(_3X1) == 8

    def test_is_portrait_false(self):
        assert pgm.pgm_is_portrait(_3X1) is False

"""Gap-coverage tests for the pbm (Portable Bitmap) format.

Exercises every symbol exported from ``pbm/__init__.py`` (the ``pbm.__all__``
surface) that is thinly covered — or not covered at all — by the rest of the
tests/python/pbm/ suite: analytics functions, geometry transforms, the
parser-level exception hierarchy, the PbmDocument domain model properties,
the raster iterator, the installed-workflow shim, and the dogfood
PBM->PGM / PBM->PPM converters.

Sample fixtures (hand-verified pixel data, from samples/by-format/pbm/valid/):
    1x1-black.pbm   : P1, 1x1, pixels=[1]
    2x2-checker.pbm : P1, 2x2, pixels=[1,0, 0,1]   (row0=[1,0], row1=[0,1])
    3x2-pattern.pbm : P1, 3x2, pixels=[1,0,1, 0,1,0]

Notable characterization: ``pbm.PbmError`` (re-exported from
``pbm.exceptions``, a facade over ``_shared.FormatFactoryError``) is a
*different class* from ``pbm.pbm_parser.PbmError`` (the base class actually
raised by ``parse_pbm_strict`` and its ``PbmInvalid*``/``PbmSize``/``PbmDecode``
subclasses). ``pytest.raises(pbm.PbmError)`` therefore does NOT catch parser
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

import pbm
from pbm.pbm_parser import PbmError as PbmParserError

_SAMPLES = _REPO / "samples" / "by-format" / "pbm"
_1X1 = _SAMPLES / "valid" / "1x1-black.pbm"
_2X2 = _SAMPLES / "valid" / "2x2-checker.pbm"
_3X2 = _SAMPLES / "valid" / "3x2-pattern.pbm"
_INVALID_MAGIC = _SAMPLES / "invalid" / "wrong-magic.pbm"


# ---------------------------------------------------------------------------
# parse_pbm / parse_pbm_strict / probe_pbm
# ---------------------------------------------------------------------------

class TestParsePbm:
    def test_parse_pbm_ok_true_on_valid(self):
        result = pbm.parse_pbm(_2X2)
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["magic"] == "P1"
        assert result["pixel_count"] == 4

    def test_parse_pbm_ok_false_on_missing(self):
        result = pbm.parse_pbm(_SAMPLES / "does-not-exist.pbm")
        assert result["ok"] is False
        assert result["error_type"] == "PbmError"

    def test_parse_pbm_ok_false_on_invalid_magic(self):
        result = pbm.parse_pbm(_INVALID_MAGIC)
        assert result["ok"] is False
        assert result["error_type"] == "PbmInvalidMagicError"

    def test_parse_pbm_strict_returns_pbmimage(self):
        img = pbm.parse_pbm_strict(_3X2)
        assert isinstance(img, pbm.PbmImage)
        assert img.width == 3
        assert img.height == 2
        assert img.pixels == [1, 0, 1, 0, 1, 0]

    def test_parse_pbm_strict_missing_file_raises_parser_pbmerror(self):
        with pytest.raises(PbmParserError, match="File not found"):
            pbm.parse_pbm_strict(_SAMPLES / "nope.pbm")

    def test_parse_pbm_strict_invalid_magic_raises_specific_subclass(self):
        with pytest.raises(pbm.PbmInvalidMagicError):
            pbm.parse_pbm_strict(_INVALID_MAGIC)

    def test_parser_errors_catchable_via_package_error(self):
        """Healed hierarchy: exceptions.py is the single source of truth,
        so pbm_parser.PbmError (imported from .exceptions) IS pbm.PbmError
        -- parser-raised errors are now catchable via the package-level
        facade. See plans/.claude/quizzical-munching-gadget.md section 7."""
        assert PbmParserError is pbm.PbmError
        with pytest.raises(pbm.PbmError):
            pbm.parse_pbm_strict(_INVALID_MAGIC)

    def test_probe_pbm_missing_file(self):
        result = pbm.probe_pbm(_SAMPLES / "absent.pbm")
        assert result["exists"] is False

    def test_probe_pbm_valid_header(self):
        result = pbm.probe_pbm(_2X2)
        assert result["valid_header"] is True
        assert result["magic"] == "P1"
        assert result["width"] == 2
        assert result["height"] == 2

    def test_probe_pbm_invalid_magic(self):
        result = pbm.probe_pbm(_INVALID_MAGIC)
        assert result["valid_header"] is False

    def test_get_dimensions(self):
        assert pbm.get_dimensions(_3X2) == (3, 2)

    def test_pixel_count(self):
        assert pbm.pixel_count(_3X2) == 6

    def test_image_pixel_stats(self):
        stats = pbm.image_pixel_stats(_2X2)
        assert stats["ok"] is True
        assert stats["black_count"] == 2
        assert stats["white_count"] == 2
        assert stats["total_pixels"] == 4
        assert stats["black_density"] == 0.5


class TestGetCapabilities:
    def test_get_capabilities_shape(self):
        caps = pbm.get_capabilities()
        assert caps["format"] == "pbm"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert "p1_ascii_parse" in caps["supported"]
        assert "ppm_color" in caps["unsupported"]

    def test_supported_unsupported_constants(self):
        assert "p4_binary_parse" in pbm.SUPPORTED_FEATURES
        assert "run_length_encoding" in pbm.UNSUPPORTED_FEATURES

    def test_magic_constants(self):
        assert pbm.PBM_MAGIC_ASCII == "P1"
        assert pbm.PBM_MAGIC_BINARY == "P4"

    def test_size_constants(self):
        assert pbm.MAX_FILE_SIZE == 64 * 1024 * 1024
        assert pbm.MAX_DIMENSION == 65536


# ---------------------------------------------------------------------------
# write_pbm
# ---------------------------------------------------------------------------

class TestWritePbm:
    def test_roundtrip(self, tmp_path):
        dest = tmp_path / "out.pbm"
        pbm.write_pbm([1, 0, 1, 0], 2, 2, dest)
        img = pbm.parse_pbm_strict(dest)
        assert img.width == 2 and img.height == 2
        assert img.pixels == [1, 0, 1, 0]
        assert img.magic == "P1"

    def test_mismatched_length_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            pbm.write_pbm([1, 0], 2, 2, tmp_path / "bad.pbm")

    def test_oversized_dimension_raises_size_error(self, tmp_path):
        with pytest.raises(pbm.PbmSizeError):
            pbm.write_pbm([], 70000, 1, tmp_path / "huge.pbm")

    def test_comment_is_sanitized(self, tmp_path):
        dest = tmp_path / "commented.pbm"
        pbm.write_pbm([1, 0], 2, 1, dest, comment="hello\nworld\r!")
        text = dest.read_text(encoding="ascii")
        lines = text.splitlines()
        assert lines[0] == "P1"
        assert lines[1].startswith("#")
        assert "\n" not in lines[1] and "\r" not in lines[1]

    def test_nonzero_values_clamped_to_one(self, tmp_path):
        dest = tmp_path / "clamped.pbm"
        pbm.write_pbm([5, 0], 2, 1, dest)
        img = pbm.parse_pbm_strict(dest)
        assert img.pixels == [1, 0]


# ---------------------------------------------------------------------------
# Geometry transforms
# ---------------------------------------------------------------------------

class TestGeometryTransforms:
    def test_count_black_and_white(self):
        assert pbm.count_black(_3X2) == 3
        assert pbm.count_white(_3X2) == 3

    def test_flip_horizontal(self, tmp_path):
        dest = tmp_path / "flipped.pbm"
        result = pbm.flip_horizontal(_2X2, dest)
        assert result["ok"] is True
        img = pbm.parse_pbm_strict(dest)
        assert img.pixels == [0, 1, 1, 0]

    def test_invert(self, tmp_path):
        dest = tmp_path / "inverted.pbm"
        pbm.invert(_2X2, dest)
        img = pbm.parse_pbm_strict(dest)
        assert img.pixels == [0, 1, 1, 0]

    def test_crop_valid_region(self, tmp_path):
        dest = tmp_path / "cropped.pbm"
        result = pbm.crop(_3X2, dest, x=1, y=0, w=2, h=1)
        assert result == {"ok": True, "width": 2, "height": 1, "pixel_count": 2}
        img = pbm.parse_pbm_strict(dest)
        assert img.pixels == [0, 1]

    def test_crop_out_of_bounds_raises(self, tmp_path):
        with pytest.raises(ValueError):
            pbm.crop(_2X2, tmp_path / "x.pbm", x=0, y=0, w=5, h=5)

    def test_crop_negative_origin_raises(self, tmp_path):
        with pytest.raises(ValueError):
            pbm.crop(_2X2, tmp_path / "y.pbm", x=-1, y=0, w=1, h=1)

    def test_rotate_90(self, tmp_path):
        dest = tmp_path / "rotated.pbm"
        result = pbm.rotate_90(_3X2, dest)
        assert result["width"] == 2
        assert result["height"] == 3
        img = pbm.parse_pbm_strict(dest)
        assert img.width == 2 and img.height == 3
        assert img.pixels == [0, 1, 1, 0, 0, 1]

    def test_scale_nearest(self, tmp_path):
        dest = tmp_path / "scaled.pbm"
        result = pbm.scale_nearest(_2X2, dest, factor=2)
        assert result["width"] == 4
        assert result["height"] == 4
        assert result["pixel_count"] == 16
        assert pbm.count_black(dest) == 8

    def test_scale_nearest_invalid_factor_raises(self, tmp_path):
        with pytest.raises(ValueError):
            pbm.scale_nearest(_2X2, tmp_path / "z.pbm", factor=0)

    def test_aspect_ratio_toplevel(self):
        assert pbm.aspect_ratio(_3X2) == pytest.approx(1.5)

    def test_black_pixel_ratio_toplevel(self):
        assert pbm.black_pixel_ratio(_3X2) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Parser-level exception hierarchy (raised by parse_pbm_strict internals)
# ---------------------------------------------------------------------------

class TestParserExceptionHierarchy:
    def test_all_specific_errors_are_parser_pbmerror_subclasses(self):
        for cls in (
            pbm.PbmInvalidMagicError,
            pbm.PbmInvalidHeaderError,
            pbm.PbmSizeError,
            pbm.PbmDecodeError,
        ):
            assert issubclass(cls, PbmParserError)

    def test_incomplete_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "incomplete.pbm"
        bad.write_text("P1\n5\n", encoding="ascii")
        with pytest.raises(pbm.PbmInvalidHeaderError):
            pbm.parse_pbm_strict(bad)

    def test_non_integer_header_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "nonint.pbm"
        bad.write_text("P1\nabc 5\n1 1 1 1 1\n", encoding="ascii")
        with pytest.raises(pbm.PbmInvalidHeaderError):
            pbm.parse_pbm_strict(bad)

    def test_oversized_dimensions_raise_size_error(self, tmp_path):
        bad = tmp_path / "oversized.pbm"
        bad.write_text("P1\n70000 1\n", encoding="ascii")
        with pytest.raises(pbm.PbmSizeError):
            pbm.parse_pbm_strict(bad)

    def test_insufficient_pixel_data_raises_decode_error(self, tmp_path):
        bad = tmp_path / "short.pbm"
        bad.write_text("P1\n2 2\n1 0 0\n", encoding="ascii")
        with pytest.raises(pbm.PbmDecodeError):
            pbm.parse_pbm_strict(bad)

    def test_out_of_range_pixel_value_raises_decode_error(self, tmp_path):
        bad = tmp_path / "outofrange.pbm"
        bad.write_text("P1\n1 1\n2\n", encoding="ascii")
        with pytest.raises(pbm.PbmDecodeError):
            pbm.parse_pbm_strict(bad)

    def test_zero_dimension_raises_invalid_header_error(self, tmp_path):
        bad = tmp_path / "zerodim.pbm"
        bad.write_text("P1\n0 5\n", encoding="ascii")
        with pytest.raises(pbm.PbmInvalidHeaderError):
            pbm.parse_pbm_strict(bad)


class TestFacadeExceptionHierarchy:
    """The exceptions.py facade classes (PbmParseError/PbmWriteError/PbmError
    -> FormatFactoryError). Complements test_exception_coverage.py by adding
    FormatFactoryError-level assertions."""

    def test_format_factory_error_is_exception(self):
        assert issubclass(pbm.FormatFactoryError, Exception)

    def test_format_factory_error_is_raisable(self):
        with pytest.raises(pbm.FormatFactoryError):
            raise pbm.FormatFactoryError("boom")

    def test_pbmerror_inherits_format_factory_error(self):
        assert issubclass(pbm.PbmError, pbm.FormatFactoryError)

    def test_pbmparseerror_and_pbmwriteerror_inherit_pbmerror(self):
        assert issubclass(pbm.PbmParseError, pbm.PbmError)
        assert issubclass(pbm.PbmWriteError, pbm.PbmError)

    def test_pbmerror_caught_as_format_factory_error(self):
        with pytest.raises(pbm.FormatFactoryError):
            raise pbm.PbmError("generic failure")


# ---------------------------------------------------------------------------
# PbmImage dataclass
# ---------------------------------------------------------------------------

class TestPbmImageDataclass:
    def test_defaults(self):
        img = pbm.PbmImage()
        assert img.spec_qname == "pbm:image"
        assert img.width == 0
        assert img.height == 0
        assert img.magic == "P1"
        assert img.pixels == []
        assert img.path == ""

    def test_field_assignment(self):
        img = pbm.PbmImage(width=4, height=5, magic="P4", pixels=[1, 0], path="x.pbm")
        assert (img.width, img.height, img.magic) == (4, 5, "P4")


# ---------------------------------------------------------------------------
# PbmDocument domain model — properties not covered by test_pbm_domain_model.py
# ---------------------------------------------------------------------------

class TestPbmDocumentProperties:
    def test_square_image_properties(self):
        doc = pbm.PbmDocument.from_file(_2X2)
        assert doc.aspect_ratio == pytest.approx(1.0)
        assert doc.is_square is True
        assert doc.is_landscape is False
        assert doc.is_portrait is False
        assert doc.is_tiny is True
        assert doc.is_large_image is False
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
        assert doc.magic == "P1"
        assert doc.pixel_count == 4
        assert str(_2X2) in doc.path or doc.path.endswith("2x2-checker.pbm")

    def test_landscape_image_properties(self):
        doc = pbm.PbmDocument.from_file(_3X2)
        assert doc.is_landscape is True
        assert doc.is_square is False
        assert doc.aspect_ratio == pytest.approx(1.5)
        assert doc.edge_ratio == pytest.approx(1.5)
        assert doc.is_narrow is False

    def test_narrow_banner_via_synthetic_document(self):
        """Duck-typed stand-in for the parsed PbmImage — PbmDocument.__init__
        accepts Any, so a lightweight object with the required attributes
        exercises is_narrow/is_banner/is_tall_strip without needing a
        million-pixel fixture file."""
        fake = types.SimpleNamespace(width=100, height=5, magic="P1", pixels=[], path="fake")
        doc = pbm.PbmDocument(fake)
        assert doc.edge_ratio == pytest.approx(20.0)
        assert doc.is_narrow is True
        assert doc.is_landscape is True
        assert doc.is_banner is True
        assert doc.is_tall_strip is False

    def test_tall_strip_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=5, height=100, magic="P4", pixels=[], path="fake")
        doc = pbm.PbmDocument(fake)
        assert doc.is_narrow is True
        assert doc.is_portrait is True
        assert doc.is_tall_strip is True
        assert doc.is_banner is False
        assert doc.is_binary is True

    def test_large_image_via_synthetic_document(self):
        fake = types.SimpleNamespace(width=1000, height=1000, magic="P1", pixels=[], path="fake")
        doc = pbm.PbmDocument(fake)
        assert doc.is_large_image is True
        assert doc.megapixels == pytest.approx(1.0)
        assert doc.is_tiny is False
        assert doc.is_micro is False

    def test_pixel_density_class_thresholds(self):
        for edge, expected in ((64, "micro"), (256, "small"), (1024, "medium"), (2048, "large")):
            fake = types.SimpleNamespace(width=edge, height=1, magic="P1", pixels=[], path="f")
            assert pbm.PbmDocument(fake).pixel_density_class == expected

    def test_zero_height_aspect_ratio_is_zero(self):
        fake = types.SimpleNamespace(width=5, height=0, magic="P1", pixels=[], path="f")
        doc = pbm.PbmDocument(fake)
        assert doc.aspect_ratio == 0.0
        assert doc.edge_ratio == 1.0

    def test_set_pixel_roundtrip(self, tmp_path):
        doc = pbm.PbmDocument.from_file(_2X2)
        doc.set_pixel(0, 0)
        out = tmp_path / "mutated.pbm"
        doc.save_to_file(out)
        reread = pbm.parse_pbm_strict(out)
        assert reread.pixels[0] == 0
        assert reread.pixels[1:] == [0, 0, 1]

    def test_set_pixel_out_of_range_raises(self):
        doc = pbm.PbmDocument.from_file(_2X2)
        with pytest.raises(PbmParserError):
            doc.set_pixel(99, 1)

    def test_save_to_file_empty_path_raises(self):
        doc = pbm.PbmDocument.from_file(_2X2)
        with pytest.raises(PbmParserError):
            doc.save_to_file("")

    def test_to_dict_full_contents(self):
        doc = pbm.PbmDocument.from_file(_3X2)
        d = doc.to_dict()
        assert d == {
            "width": 3,
            "height": 2,
            "pixel_count": 6,
            "magic": "P1",
            "path": doc.path,
        }

    def test_repr_contains_dimensions_and_magic(self):
        doc = pbm.PbmDocument.from_file(_2X2)
        r = repr(doc)
        assert "width=2" in r and "height=2" in r and "P1" in r


# ---------------------------------------------------------------------------
# pbm_iter_rasters (spec-shaped raster iterator)
# ---------------------------------------------------------------------------

class TestIterRasters:
    def test_yields_single_raster(self):
        rasters = list(pbm.pbm_iter_rasters(_2X2))
        assert len(rasters) == 1

    def test_raster_shape_and_rows(self):
        raster = next(pbm.pbm_iter_rasters(_3X2))
        assert raster.width == 3
        assert raster.height == 2
        assert raster.pixel_count == 6
        assert raster.rows == [[1, 0, 1], [0, 1, 0]]
        assert raster.spec_qname == "pbm:raster"

    def test_raster_to_dict_and_repr(self):
        raster = next(pbm.pbm_iter_rasters(_1X1))
        d = raster.to_dict()
        assert d["width"] == 1 and d["height"] == 1
        assert "Raster(" in repr(raster)


# ---------------------------------------------------------------------------
# pbm_installed_workflow
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    def test_workflow_on_valid_file(self):
        result = pbm.pbm_installed_workflow(_3X2)
        assert result == {
            "format": "pbm",
            "loaded": True,
            "width": 3,
            "height": 2,
            "pixel_count": 6,
        }

    def test_workflow_on_missing_file_reports_not_loaded(self):
        result = pbm.pbm_installed_workflow(_SAMPLES / "missing.pbm")
        assert result["format"] == "pbm"
        assert result["loaded"] is False
        assert result["width"] == 0
        assert result["height"] == 0


# ---------------------------------------------------------------------------
# Dogfood conversions: PBM -> PGM, PBM -> PPM
# ---------------------------------------------------------------------------

class TestDogfoodConversions:
    def test_pbm_pixels_to_pgm_pixels(self):
        result = pbm.pbm_pixels_to_pgm_pixels([0, 1, 1, 0], maxval=100)
        assert result == [100, 0, 0, 100]

    def test_pbm_pixels_to_pgm_pixels_invalid_maxval_raises(self):
        with pytest.raises(ValueError):
            pbm.pbm_pixels_to_pgm_pixels([0, 1], maxval=0)

    def test_convert_pbm_to_pgm(self, tmp_path):
        dest = tmp_path / "converted.pgm"
        result = pbm.convert_pbm_to_pgm(_2X2, dest, maxval=255)
        assert result["dogfood_status"] == "IMPLEMENTED"
        assert result["width"] == 2 and result["height"] == 2

        import pgm as pgm_module
        pgm_img = pgm_module.parse_pgm_strict(dest)
        assert pgm_img.pixels == [0, 255, 255, 0]
        assert pgm_img.maxval == 255

    def test_pbm_pixels_to_ppm_pixels(self):
        result = pbm.pbm_pixels_to_ppm_pixels([0, 1], maxval=200)
        assert result == [(200, 200, 200), (0, 0, 0)]

    def test_pbm_pixels_to_ppm_pixels_invalid_maxval_raises(self):
        with pytest.raises(ValueError):
            pbm.pbm_pixels_to_ppm_pixels([0], maxval=0)

    def test_convert_pbm_to_ppm(self, tmp_path):
        dest = tmp_path / "converted.ppm"
        result = pbm.convert_pbm_to_ppm(_2X2, dest, maxval=255)
        assert result["status"] == "success"
        assert result["dogfood"] is True

        import ppm as ppm_module
        ppm_img = ppm_module.parse_ppm_strict(dest)
        assert ppm_img.pixels == [
            (0, 0, 0), (255, 255, 255),
            (255, 255, 255), (0, 0, 0),
        ]


# ---------------------------------------------------------------------------
# P4 binary decode path (bundled samples are all P1 ASCII)
# ---------------------------------------------------------------------------

class TestBinaryP4Support:
    def test_p4_binary_roundtrips_same_pixels_as_ascii_equivalent(self, tmp_path):
        # 2x2 checker: row0=[1,0] -> byte 0b10000000; row1=[0,1] -> byte 0b01000000
        raw = b"P4\n2 2\n" + bytes([0b10000000, 0b01000000])
        dest = tmp_path / "binary.pbm"
        dest.write_bytes(raw)
        img = pbm.parse_pbm_strict(dest)
        assert img.magic == "P4"
        assert img.width == 2 and img.height == 2
        assert img.pixels == [1, 0, 0, 1]
        assert pbm.pbm_is_binary(dest) is True


# ---------------------------------------------------------------------------
# Analytics functions (bitmap_image.py) — 1x1-black.pbm
# ---------------------------------------------------------------------------

class TestAnalytics1x1:
    """pixels=[1], width=1, height=1 (all-black single pixel)."""

    def test_white_pixel_ratio(self):
        assert pbm.pbm_white_pixel_ratio(_1X1) == 0.0

    def test_aspect_ratio(self):
        assert pbm.pbm_aspect_ratio(_1X1) == 1.0

    def test_white_pixel_count(self):
        assert pbm.pbm_white_pixel_count(_1X1) == 0

    def test_is_binary(self):
        assert pbm.pbm_is_binary(_1X1) is False

    def test_all_black(self):
        assert pbm.pbm_all_black(_1X1) is True
        assert pbm.pbm_is_all_black(_1X1) is True

    def test_all_white(self):
        assert pbm.pbm_all_white(_1X1) is False

    def test_is_uniform(self):
        assert pbm.pbm_is_uniform(_1X1) is True

    def test_perimeter(self):
        assert pbm.pbm_perimeter(_1X1) == 4

    def test_is_square(self):
        assert pbm.pbm_is_square(_1X1) is True

    def test_is_landscape_and_portrait(self):
        assert pbm.pbm_is_landscape(_1X1) is False
        assert pbm.pbm_is_portrait(_1X1) is False

    def test_max_row_black_count(self):
        assert pbm.pbm_max_row_black_count(_1X1) == 1

    def test_diagonal(self):
        assert pbm.pbm_diagonal(_1X1) == pytest.approx(math.sqrt(2))

    def test_min_row_black_count(self):
        assert pbm.pbm_min_row_black_count(_1X1) == 1

    def test_is_binary_balanced(self):
        assert pbm.pbm_is_binary_balanced(_1X1) is False

    def test_avg_row_density(self):
        assert pbm.pbm_avg_row_density(_1X1) == pytest.approx(1.0)

    def test_border_black_count(self):
        assert pbm.pbm_border_black_count(_1X1) == 1

    def test_row_density_variance_single_row_is_zero(self):
        assert pbm.pbm_row_density_variance(_1X1) == 0.0

    def test_is_checkerboard(self):
        assert pbm.pbm_is_checkerboard(_1X1) is False

    def test_column_density_variance_single_column_is_zero(self):
        assert pbm.pbm_column_density_variance(_1X1) == 0.0

    def test_diagonal_pixel_count(self):
        assert pbm.pbm_diagonal_pixel_count(_1X1) == 1

    def test_total_black_in_border(self):
        assert pbm.pbm_total_black_in_border(_1X1) == 1

    def test_center_black_ratio_too_small_returns_zero(self):
        assert pbm.pbm_center_black_ratio(_1X1) == 0.0

    def test_corner_pixel_sum(self):
        assert pbm.pbm_corner_pixel_sum(_1X1) == 4

    def test_checkerboard_score(self):
        assert pbm.pbm_checkerboard_score(_1X1) == 0.0

    def test_column_transition_count_single_row_is_zero(self):
        assert pbm.pbm_column_transition_count(_1X1) == 0

    def test_center_black_count_too_small_returns_zero(self):
        assert pbm.pbm_center_black_count(_1X1) == 0

    def test_row_transition_count_single_column_is_zero(self):
        assert pbm.pbm_row_transition_count(_1X1) == 0

    def test_max_black_run_length(self):
        assert pbm.pbm_max_black_run_length(_1X1) == 1

    def test_black_run_count(self):
        assert pbm.pbm_black_run_count(_1X1) == 1

    def test_row_black_ratio_variance_single_row_is_zero(self):
        assert pbm.pbm_row_black_ratio_variance(_1X1) == 0.0

    def test_edge_black_ratio(self):
        assert pbm.pbm_edge_black_ratio(_1X1) == pytest.approx(1.0)

    def test_isolation_score(self):
        assert pbm.pbm_isolation_score(_1X1) == pytest.approx(1.0)

    def test_width_height_magic(self):
        assert pbm.pbm_width(_1X1) == 1
        assert pbm.pbm_height(_1X1) == 1
        assert pbm.pbm_magic(_1X1) == "P1"

    def test_is_ascii_format(self):
        assert pbm.pbm_is_ascii_format(_1X1) is True

    def test_is_single_pixel(self):
        assert pbm.pbm_is_single_pixel(_1X1) is True


# ---------------------------------------------------------------------------
# Analytics functions — 2x2-checker.pbm
# ---------------------------------------------------------------------------

class TestAnalytics2x2:
    """pixels=[1,0, 0,1], width=2, height=2."""

    def test_row_black_counts(self):
        assert pbm.pbm_row_black_counts(_2X2) == [1, 1]

    def test_total_pixel_count(self):
        assert pbm.pbm_total_pixel_count(_2X2) == 4

    def test_black_pixel_ratio(self):
        assert pbm.pbm_black_pixel_ratio(_2X2) == pytest.approx(0.5)

    def test_dimensions_dict(self):
        assert pbm.pbm_dimensions(_2X2) == {"width": 2, "height": 2}

    def test_column_black_counts(self):
        assert pbm.pbm_column_black_counts(_2X2) == [1, 1]

    def test_white_density(self):
        assert pbm.pbm_white_density(_2X2) == pytest.approx(0.5)

    def test_row_count(self):
        assert pbm.pbm_row_count(_2X2) == 2

    def test_has_any_black_and_white(self):
        assert pbm.pbm_has_any_black(_2X2) is True
        assert pbm.pbm_has_any_white(_2X2) is True

    def test_black_pixel_count(self):
        assert pbm.pbm_black_pixel_count(_2X2) == 2

    def test_is_uniform_false_for_mixed(self):
        assert pbm.pbm_is_uniform(_2X2) is False

    def test_max_dimension_and_min_dimension(self):
        assert pbm.pbm_max_dimension(_2X2) == 2
        assert pbm.pbm_min_dimension(_2X2) == 2

    def test_black_density(self):
        assert pbm.pbm_black_density(_2X2) == pytest.approx(0.5)

    def test_area_and_column_count(self):
        assert pbm.pbm_area(_2X2) == 4
        assert pbm.pbm_column_count(_2X2) == 2

    def test_dimension_ratio(self):
        assert pbm.pbm_dimension_ratio(_2X2) == pytest.approx(1.0)

    def test_megapixels(self):
        assert pbm.pbm_megapixels(_2X2) == pytest.approx(4e-6)

    def test_is_tall_wide_portrait_false(self):
        assert pbm.pbm_is_tall(_2X2) is False
        assert pbm.pbm_is_wide(_2X2) is False
        assert pbm.pbm_is_portrait(_2X2) is False

    def test_is_binary_balanced(self):
        assert pbm.pbm_is_binary_balanced(_2X2) is True

    def test_border_black_count(self):
        assert pbm.pbm_border_black_count(_2X2) == 2

    def test_row_density_variance(self):
        assert pbm.pbm_row_density_variance(_2X2) == pytest.approx(0.0)

    def test_is_checkerboard_offset_pattern_is_false(self):
        # (0,0) is black(1) but the checkerboard formula expects white(0) there.
        assert pbm.pbm_is_checkerboard(_2X2) is False

    def test_column_density_variance(self):
        assert pbm.pbm_column_density_variance(_2X2) == pytest.approx(0.0)

    def test_diagonal_pixel_count(self):
        assert pbm.pbm_diagonal_pixel_count(_2X2) == 2

    def test_total_pixels(self):
        assert pbm.pbm_total_pixels(_2X2) == 4

    def test_is_all_black_false(self):
        assert pbm.pbm_is_all_black(_2X2) is False

    def test_total_black_in_border(self):
        assert pbm.pbm_total_black_in_border(_2X2) == 2

    def test_center_black_ratio_too_small(self):
        assert pbm.pbm_center_black_ratio(_2X2) == 0.0

    def test_corner_pixel_sum(self):
        assert pbm.pbm_corner_pixel_sum(_2X2) == 2

    def test_checkerboard_score(self):
        assert pbm.pbm_checkerboard_score(_2X2) == 0.0

    def test_column_transition_count(self):
        assert pbm.pbm_column_transition_count(_2X2) == 2

    def test_center_black_count_too_small(self):
        assert pbm.pbm_center_black_count(_2X2) == 0

    def test_row_transition_count(self):
        assert pbm.pbm_row_transition_count(_2X2) == 2

    def test_max_black_run_length(self):
        assert pbm.pbm_max_black_run_length(_2X2) == 1

    def test_black_run_count(self):
        assert pbm.pbm_black_run_count(_2X2) == 2

    def test_row_black_ratio_variance(self):
        assert pbm.pbm_row_black_ratio_variance(_2X2) == pytest.approx(0.0)

    def test_edge_black_ratio(self):
        assert pbm.pbm_edge_black_ratio(_2X2) == pytest.approx(0.5)

    def test_isolation_score(self):
        assert pbm.pbm_isolation_score(_2X2) == pytest.approx(1.0)

    def test_is_single_pixel_false(self):
        assert pbm.pbm_is_single_pixel(_2X2) is False

    def test_pixel_density_is_positive_float(self):
        assert isinstance(pbm.pbm_pixel_density(_2X2), float)
        assert pbm.pbm_pixel_density(_2X2) > 0


# ---------------------------------------------------------------------------
# Analytics functions — 3x2-pattern.pbm (rectangular / landscape case)
# ---------------------------------------------------------------------------

class TestAnalytics3x2:
    """pixels=[1,0,1, 0,1,0], width=3, height=2."""

    def test_aspect_ratio(self):
        assert pbm.pbm_aspect_ratio(_3X2) == pytest.approx(1.5)

    def test_row_black_counts(self):
        assert pbm.pbm_row_black_counts(_3X2) == [2, 1]

    def test_column_black_counts(self):
        assert pbm.pbm_column_black_counts(_3X2) == [1, 1, 1]

    def test_perimeter(self):
        assert pbm.pbm_perimeter(_3X2) == 10

    def test_is_landscape_true(self):
        assert pbm.pbm_is_landscape(_3X2) is True

    def test_is_square_false(self):
        assert pbm.pbm_is_square(_3X2) is False

    def test_max_row_black_count(self):
        assert pbm.pbm_max_row_black_count(_3X2) == 2

    def test_min_row_black_count(self):
        assert pbm.pbm_min_row_black_count(_3X2) == 1

    def test_max_dimension_min_dimension(self):
        assert pbm.pbm_max_dimension(_3X2) == 3
        assert pbm.pbm_min_dimension(_3X2) == 2

    def test_diagonal(self):
        assert pbm.pbm_diagonal(_3X2) == pytest.approx(math.sqrt(13))

    def test_dimension_ratio(self):
        assert pbm.pbm_dimension_ratio(_3X2) == pytest.approx(1.5)

    def test_is_tall_wide_portrait(self):
        assert pbm.pbm_is_tall(_3X2) is False
        assert pbm.pbm_is_wide(_3X2) is False
        assert pbm.pbm_is_portrait(_3X2) is False

    def test_is_binary_balanced_equal_counts(self):
        assert pbm.pbm_is_binary_balanced(_3X2) is True

    def test_avg_row_density(self):
        assert pbm.pbm_avg_row_density(_3X2) == pytest.approx(0.5)

    def test_is_all_black_false(self):
        assert pbm.pbm_is_all_black(_3X2) is False

    def test_center_black_ratio_too_narrow(self):
        assert pbm.pbm_center_black_ratio(_3X2) == 0.0

    def test_corner_pixel_sum(self):
        assert pbm.pbm_corner_pixel_sum(_3X2) == 2

    def test_checkerboard_score_all_mismatch(self):
        assert pbm.pbm_checkerboard_score(_3X2) == 0.0

    def test_column_transition_count(self):
        assert pbm.pbm_column_transition_count(_3X2) == 3

    def test_center_black_count_too_narrow(self):
        assert pbm.pbm_center_black_count(_3X2) == 0

    def test_row_transition_count(self):
        assert pbm.pbm_row_transition_count(_3X2) == 4

    def test_max_black_run_length(self):
        assert pbm.pbm_max_black_run_length(_3X2) == 1

    def test_black_run_count(self):
        assert pbm.pbm_black_run_count(_3X2) == 3

    def test_row_black_ratio_variance(self):
        assert pbm.pbm_row_black_ratio_variance(_3X2) == pytest.approx(1 / 36)

    def test_edge_black_ratio(self):
        assert pbm.pbm_edge_black_ratio(_3X2) == pytest.approx(0.5)

    def test_isolation_score(self):
        assert pbm.pbm_isolation_score(_3X2) == pytest.approx(1.0)

    def test_width_height_magic(self):
        assert pbm.pbm_width(_3X2) == 3
        assert pbm.pbm_height(_3X2) == 2
        assert pbm.pbm_magic(_3X2) == "P1"

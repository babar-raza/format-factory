"""Tests for nrrd_analytics.py — nrrd_axis_sizes, nrrd_is_compressed, nrrd_element_count.

Generated alongside the /format-feature-expansion invocation for taskcard
TC-PROLIB-NRRD-001 (transcript:
reports/skills-r1/skill-transcripts/format-feature-expansion-nrrd.json).

Tier notes:
  - TestAxisSizes / TestIsCompressed / TestElementCount        -> L2 (analytics correctness)
  - TestAxisSizesEdge / TestIsCompressedEdge / TestElementCountEdge -> L3 (malformed/boundary)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from nrrd.exceptions import NrrdParseError
from nrrd.nrrd_analytics import (
    nrrd_axis_sizes,
    nrrd_element_count,
    nrrd_is_compressed,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"

SYNTHETIC_1D = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n\x00\x01\x02\x03"
SYNTHETIC_3D = (
    b"NRRD0005\ntype: uint8\ndimension: 3\nsizes: 2 3 4\nencoding: raw\n\n"
    + b"\x00" * 24
)


class TestAxisSizes:
    """L2 — nrrd_axis_sizes returns correct list for valid input."""

    def test_returns_list_type(self):
        result = nrrd_axis_sizes(VALID_DIR / "1d-int8.nrrd")
        assert isinstance(result, list)

    def test_1d_int8_sizes(self):
        assert nrrd_axis_sizes(VALID_DIR / "1d-int8.nrrd") == [4]

    def test_2d_float32_sizes(self):
        assert nrrd_axis_sizes(VALID_DIR / "2d-float32.nrrd") == [2, 3]

    def test_gzip_encoded_sizes(self):
        assert nrrd_axis_sizes(VALID_DIR / "gzip-encoded.nrrd") == [4]

    def test_accepts_string_path(self):
        result = nrrd_axis_sizes(str(VALID_DIR / "1d-int8.nrrd"))
        assert result == [4]

    def test_accepts_path_object(self):
        result = nrrd_axis_sizes(Path(VALID_DIR / "1d-int8.nrrd"))
        assert result == [4]

    def test_accepts_bytes_source(self):
        assert nrrd_axis_sizes(SYNTHETIC_1D) == [4]

    def test_multi_axis_3d_synthetic(self):
        assert nrrd_axis_sizes(SYNTHETIC_3D) == [2, 3, 4]

    def test_all_elements_are_ints(self):
        result = nrrd_axis_sizes(VALID_DIR / "2d-float32.nrrd")
        assert all(isinstance(v, int) for v in result)


class TestIsCompressed:
    """L2 — nrrd_is_compressed returns correct value for valid input."""

    def test_returns_bool_type(self):
        result = nrrd_is_compressed(VALID_DIR / "1d-int8.nrrd")
        assert isinstance(result, bool)

    def test_raw_encoding_is_false(self):
        assert nrrd_is_compressed(VALID_DIR / "1d-int8.nrrd") is False

    def test_raw_2d_encoding_is_false(self):
        assert nrrd_is_compressed(VALID_DIR / "2d-float32.nrrd") is False

    def test_gzip_encoding_is_true(self):
        assert nrrd_is_compressed(VALID_DIR / "gzip-encoded.nrrd") is True

    def test_accepts_string_path(self):
        assert nrrd_is_compressed(str(VALID_DIR / "gzip-encoded.nrrd")) is True

    def test_accepts_path_object(self):
        assert nrrd_is_compressed(Path(VALID_DIR / "gzip-encoded.nrrd")) is True

    def test_accepts_bytes_source_raw(self):
        assert nrrd_is_compressed(SYNTHETIC_1D) is False

    def test_accepts_bytes_source_gzip(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: gzip\n\n\x00\x01\x02\x03"
        assert nrrd_is_compressed(data) is True


class TestElementCount:
    """L2 — nrrd_element_count returns correct product-of-sizes value."""

    def test_returns_int_type(self):
        result = nrrd_element_count(VALID_DIR / "1d-int8.nrrd")
        assert isinstance(result, int)

    def test_1d_int8_count(self):
        assert nrrd_element_count(VALID_DIR / "1d-int8.nrrd") == 4

    def test_2d_float32_count(self):
        assert nrrd_element_count(VALID_DIR / "2d-float32.nrrd") == 6

    def test_gzip_encoded_count(self):
        assert nrrd_element_count(VALID_DIR / "gzip-encoded.nrrd") == 4

    def test_accepts_string_path(self):
        assert nrrd_element_count(str(VALID_DIR / "2d-float32.nrrd")) == 6

    def test_accepts_path_object(self):
        assert nrrd_element_count(Path(VALID_DIR / "2d-float32.nrrd")) == 6

    def test_accepts_bytes_source(self):
        assert nrrd_element_count(SYNTHETIC_1D) == 4

    def test_3d_synthetic_count_is_product(self):
        assert nrrd_element_count(SYNTHETIC_3D) == 2 * 3 * 4

    def test_matches_manual_axis_sizes_product(self):
        sizes = nrrd_axis_sizes(VALID_DIR / "2d-float32.nrrd")
        expected = 1
        for s in sizes:
            expected *= s
        assert nrrd_element_count(VALID_DIR / "2d-float32.nrrd") == expected


class TestAxisSizesEdge:
    """L3 — nrrd_axis_sizes against malformed/boundary input."""

    def test_missing_sizes_field_returns_empty(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nencoding: raw\n\n\x00\x01\x02\x03"
        assert nrrd_axis_sizes(data) == []

    def test_zero_dimension_size(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 0\nencoding: raw\n\n"
        assert nrrd_axis_sizes(data) == [0]

    def test_invalid_source_raises(self):
        with pytest.raises(NrrdParseError):
            nrrd_axis_sizes(INVALID_DIR / "bad-magic.nrrd")

    def test_nonexistent_file_raises(self):
        with pytest.raises(NrrdParseError):
            nrrd_axis_sizes("/nonexistent/nrrd/file/path.nrrd")


class TestIsCompressedEdge:
    """L3 — nrrd_is_compressed against malformed/boundary input."""

    def test_missing_encoding_field_defaults_raw_false(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\n\n\x00\x01\x02\x03"
        assert nrrd_is_compressed(data) is False

    def test_unsupported_encoding_value_reported_true(self):
        # bzip2 is an UNSUPPORTED_FEATURE for the codec's write/decode paths,
        # but nrrd_is_compressed only inspects the declared header field.
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: bzip2\n\n\x00\x01\x02\x03"
        assert nrrd_is_compressed(data) is True

    def test_invalid_source_raises(self):
        with pytest.raises(NrrdParseError):
            nrrd_is_compressed(INVALID_DIR / "bad-magic.nrrd")


class TestElementCountEdge:
    """L3 — nrrd_element_count against malformed/boundary input."""

    def test_missing_sizes_returns_zero(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nencoding: raw\n\n\x00\x01\x02\x03"
        assert nrrd_element_count(data) == 0

    def test_single_dimension_size_one(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 1\nencoding: raw\n\n\x00"
        assert nrrd_element_count(data) == 1

    def test_zero_size_axis_makes_count_zero(self):
        data = b"NRRD0004\ntype: uint8\ndimension: 2\nsizes: 0 5\nencoding: raw\n\n"
        assert nrrd_element_count(data) == 0

    def test_invalid_source_raises(self):
        with pytest.raises(NrrdParseError):
            nrrd_element_count(INVALID_DIR / "bad-magic.nrrd")

"""Feature-completeness tests for the NRRD codec — real payload decode,
endianness byte-swapping, line/byte skip offset handling, kinds, space
orientation fields, and key/value pair parsing.

Audit finding: the pre-existing nrrd codec only extracted header text
metadata and a byte count — it never decoded the raw/gzip payload into
typed, shaped numeric values, ignored `endian`/`line skip`/`byte skip`,
and had no support for `kinds`/`space`/key:=value pairs. This test file
proves each fix with constructed NRRD byte fixtures and exact expected
values (not just "no exception raised").

Fact refs: FACT-NRRD-101 (payload decode), FACT-NRRD-102 (byteswap),
FACT-NRRD-103 (line/byte skip), FACT-NRRD-104 (kinds), FACT-NRRD-105
(space orientation), FACT-NRRD-106 (key:=value pairs).
"""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

import pytest

from nrrd.exceptions import NrrdParseError
from nrrd.models import NrrdDocument
from nrrd.nrrd_analytics import nrrd_kinds, nrrd_to_array
from nrrd.nrrd_codec import (
    byteswap_values,
    decode_nrrd_data,
    get_array,
    load_nrrd,
    reshape_nrrd_array,
    write_nrrd,
)
from nrrd.spec.header.header import Header

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "nrrd"
VALID_DIR = SAMPLES / "valid"

HOST_ORDER = sys.byteorder
NON_HOST_ORDER = "big" if HOST_ORDER == "little" else "little"


def _nrrd_bytes(header_lines: list[str], payload: bytes, version: int = 5) -> bytes:
    """Build raw NRRD file bytes: magic + header lines + blank line + payload."""
    text = f"NRRD000{version}\n" + "\n".join(header_lines) + "\n\n"
    return text.encode("ascii") + payload


# ---------------------------------------------------------------------------
# FACT-NRRD-101: real payload decode into typed, shaped values
# ---------------------------------------------------------------------------


class TestPayloadDecode:
    """decode_nrrd_data must produce real typed numeric values, not a byte count."""

    def test_1d_int8_sample_decodes_to_known_values(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        assert model["array"] == [1, 2, 3, 4]
        assert model["array_shape"] == [4]

    def test_2d_float32_sample_decodes_to_known_values(self):
        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        assert model["array"] == pytest.approx([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        assert model["array_shape"] == [2, 3]

    def test_gzip_encoded_sample_decodes_to_known_values(self):
        model = load_nrrd(VALID_DIR / "gzip-encoded.nrrd")
        assert model["array"] == [10, 20, 30, 40]

    def test_get_array_reshapes_2d_per_axis0_fastest(self):
        model = load_nrrd(VALID_DIR / "2d-float32.nrrd")
        nested = get_array(model)
        assert nested == [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]

    def test_nrrd_document_to_array(self):
        doc = NrrdDocument.from_file(str(VALID_DIR / "1d-int8.nrrd"))
        assert doc.to_array() == [1, 2, 3, 4]

    def test_nrrd_to_array_analytics_function(self):
        assert nrrd_to_array(VALID_DIR / "1d-int8.nrrd") == [1, 2, 3, 4]

    @pytest.mark.parametrize(
        "type_str,fmt_char,values",
        [
            ("int8", "b", [-5, 0, 5, 127]),
            ("uint8", "B", [0, 1, 200, 255]),
            ("int16", "h", [-1000, 0, 1000, 32000]),
            ("uint16", "H", [0, 1, 40000, 65535]),
            ("int32", "i", [-100000, 0, 100000, 2000000000]),
            ("uint32", "I", [0, 1, 3000000000, 4000000000]),
            ("float", "f", [1.5, -2.25, 0.0, 100.0]),
            ("double", "d", [1.5, -2.25, 0.0, 1e10]),
        ],
    )
    def test_all_required_types_decode_exact_values(self, type_str, fmt_char, values):
        payload = struct.pack(f"={len(values)}{fmt_char}", *values)
        decoded = decode_nrrd_data(type_str, [len(values)], payload, endian=HOST_ORDER)
        assert decoded == pytest.approx(list(values))

    def test_decode_ignores_trailing_garbage_bytes(self):
        values = [1, 2, 3, 4]
        payload = struct.pack("=4b", *values) + b"\xff\xff\xff"
        decoded = decode_nrrd_data("int8", [4], payload)
        assert decoded == values

    def test_decode_too_short_payload_raises(self):
        with pytest.raises(NrrdParseError):
            decode_nrrd_data("int32", [4], b"\x00\x01")

    def test_decode_unsupported_type_raises(self):
        with pytest.raises(NrrdParseError):
            decode_nrrd_data("block", [4], b"\x00\x01\x02\x03")

    def test_decode_zero_size_axis_returns_empty(self):
        assert decode_nrrd_data("uint8", [0], b"") == []

    def test_load_unsupported_type_leaves_array_none(self):
        data = _nrrd_bytes(["type: block", "dimension: 1", "sizes: 4", "encoding: raw"], b"\x00\x01\x02\x03")
        model = load_nrrd(data)
        assert model["array"] is None
        assert model["array_shape"] is None
        # legacy byte-count metadata must still be present (no regression)
        assert model["data_size"] == 4

    def test_reshape_1d_is_flat(self):
        assert reshape_nrrd_array([1, 2, 3], [3]) == [1, 2, 3]

    def test_reshape_3d(self):
        # sizes = [2, 2, 2]: axis0 fastest.
        flat = list(range(8))
        nested = reshape_nrrd_array(flat, [2, 2, 2])
        assert nested == [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]


# ---------------------------------------------------------------------------
# FACT-NRRD-102: endianness byte-swapping
# ---------------------------------------------------------------------------


class TestEndianByteSwap:
    """Multi-byte values must decode correctly regardless of host byte order."""

    def test_byteswap_values_reverses_int16(self):
        native_bytes = struct.pack("=h", 1)
        swapped_bytes = native_bytes[::-1]
        (wrong_value,) = struct.unpack("=h", swapped_bytes)
        assert byteswap_values([wrong_value], "h") == [1]

    def test_decode_int16_non_host_endian(self):
        # Encode 1 in the byte order OPPOSITE the host, declare that same
        # opposite order in the header, and confirm decode still returns 1
        # (i.e. it did NOT read it as raw host-order bytes, which would be
        # a large garbled value).
        pack_char = "<" if NON_HOST_ORDER == "little" else ">"
        payload = struct.pack(f"{pack_char}h", 1)
        decoded = decode_nrrd_data("int16", [1], payload, endian=NON_HOST_ORDER)
        assert decoded == [1]

    def test_decode_int16_host_endian_no_swap_needed(self):
        pack_char = "<" if HOST_ORDER == "little" else ">"
        payload = struct.pack(f"{pack_char}h", 1)
        decoded = decode_nrrd_data("int16", [1], payload, endian=HOST_ORDER)
        assert decoded == [1]

    def test_decode_float32_non_host_endian(self):
        pack_char = "<" if NON_HOST_ORDER == "little" else ">"
        payload = struct.pack(f"{pack_char}f", 3.5)
        decoded = decode_nrrd_data("float", [1], payload, endian=NON_HOST_ORDER)
        assert decoded == pytest.approx([3.5])

    def test_wrong_endian_without_swap_gives_different_bytes_reading(self):
        # Sanity check that byte order actually matters for this fixture
        # (guards against a false-positive test on palindromic byte patterns).
        pack_char = "<" if NON_HOST_ORDER == "little" else ">"
        payload = struct.pack(f"{pack_char}h", 4096)
        wrong_char = "<" if HOST_ORDER == "little" else ">"
        (misread,) = struct.unpack(f"{wrong_char}h", payload)
        assert misread != 4096

    def test_1_byte_types_never_need_swap(self):
        # int8/uint8 have no byte order ambiguity: declared endian must be
        # irrelevant to the decoded value.
        payload = struct.pack("=4b", 1, 2, 3, 4)
        decoded_a = decode_nrrd_data("int8", [4], payload, endian="little")
        decoded_b = decode_nrrd_data("int8", [4], payload, endian="big")
        assert decoded_a == decoded_b == [1, 2, 3, 4]

    def test_load_nrrd_applies_byteswap_end_to_end(self):
        pack_char = "<" if NON_HOST_ORDER == "little" else ">"
        payload = struct.pack(f"{pack_char}4h", 10, 20, 30, 40)
        data = _nrrd_bytes(
            ["type: int16", "dimension: 1", "sizes: 4", "encoding: raw", f"endian: {NON_HOST_ORDER}"],
            payload,
        )
        model = load_nrrd(data)
        assert model["array"] == [10, 20, 30, 40]


# ---------------------------------------------------------------------------
# FACT-NRRD-103: line skip / byte skip offset handling
# ---------------------------------------------------------------------------


class TestLineAndByteSkip:
    def test_byte_skip_positive_offsets_past_junk_bytes(self):
        junk = b"\xde\xad\xbe\xef"
        real_payload = struct.pack("=4b", 1, 2, 3, 4)
        data = _nrrd_bytes(
            ["type: int8", "dimension: 1", "sizes: 4", "encoding: raw", "byte skip: 4"],
            junk + real_payload,
        )
        model = load_nrrd(data)
        assert model["byte_skip"] == 4
        assert model["array"] == [1, 2, 3, 4]

    def test_byte_skip_bug_regression_without_skip_reads_garbage(self):
        # Proves the fix matters: without honoring byte skip, decode would
        # start reading from the junk bytes and NOT get [1, 2, 3, 4].
        junk = b"\xde\xad\xbe\xef"
        real_payload = struct.pack("=4b", 1, 2, 3, 4)
        raw_payload = junk + real_payload
        misdecoded = decode_nrrd_data("int8", [4], raw_payload)
        assert misdecoded != [1, 2, 3, 4]

    def test_line_skip_positive_skips_extra_lines(self):
        real_payload = struct.pack("=4b", 5, 6, 7, 8)
        junk_line = b"this is a skipped line of metadata\n"
        data = _nrrd_bytes(
            ["type: int8", "dimension: 1", "sizes: 4", "encoding: raw", "line skip: 1"],
            junk_line + real_payload,
        )
        model = load_nrrd(data)
        assert model["line_skip"] == 1
        assert model["array"] == [5, 6, 7, 8]

    def test_line_skip_multiple_lines(self):
        real_payload = struct.pack("=2b", 9, 10)
        junk = b"line one\nline two\n"
        data = _nrrd_bytes(
            ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw", "line skip: 2"],
            junk + real_payload,
        )
        model = load_nrrd(data)
        assert model["array"] == [9, 10]

    def test_byte_skip_negative_one_skips_to_expected_tail_size(self):
        # byte skip: -1 => skip len(file) - expected_data_size bytes, i.e.
        # keep exactly the trailing expected_data_size bytes as the payload.
        unknown_length_prefix = b"PROPRIETARY-HEADER-OF-UNKNOWN-LENGTH-1234567890"
        real_payload = struct.pack("=4b", 11, 12, 13, 14)
        data = _nrrd_bytes(
            ["type: int8", "dimension: 1", "sizes: 4", "encoding: raw", "byte skip: -1"],
            unknown_length_prefix + real_payload,
        )
        model = load_nrrd(data)
        assert model["byte_skip"] == -1
        assert model["array"] == [11, 12, 13, 14]

    def test_no_skip_fields_default_to_zero(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        assert model["line_skip"] == 0
        assert model["byte_skip"] == 0

    def test_byte_skip_and_line_skip_combined(self):
        real_payload = struct.pack("=2b", 21, 22)
        junk_line = b"skip-me\n"
        junk_bytes = b"XX"
        data = _nrrd_bytes(
            ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw", "line skip: 1", "byte skip: 2"],
            junk_line + junk_bytes + real_payload,
        )
        model = load_nrrd(data)
        assert model["array"] == [21, 22]


# ---------------------------------------------------------------------------
# FACT-NRRD-104: kinds field (domain vs range axis semantics)
# ---------------------------------------------------------------------------


class TestKinds:
    def test_load_parses_kinds_list(self):
        data = _nrrd_bytes(
            [
                "type: uint8", "dimension: 3", "sizes: 2 2 3", "encoding: raw",
                "kinds: domain domain RGB-color",
            ],
            bytes(range(12)),
        )
        model = load_nrrd(data)
        assert model["kinds"] == ["domain", "domain", "RGB-color"]

    def test_header_domain_and_range_axes_distinguish_channel_axis(self):
        header = {"kinds": "domain domain RGB-color"}
        h = Header(header)
        assert h.kinds == ["domain", "domain", "RGB-color"]
        assert h.domain_axes == [0, 1]
        assert h.range_axes == [2]

    def test_nrrd_document_kinds_properties(self):
        data = {"kinds": ["domain", "vector"]}
        doc = NrrdDocument(data)
        assert doc.kinds == ["domain", "vector"]
        assert doc.domain_axes == [0]
        assert doc.range_axes == [1]

    def test_missing_kinds_defaults_empty(self):
        h = Header({})
        assert h.kinds == []
        assert h.domain_axes == []
        assert h.range_axes == []

    def test_nrrd_kinds_analytics_function(self):
        data = _nrrd_bytes(
            ["type: uint8", "dimension: 1", "sizes: 3", "encoding: raw", "kinds: RGB-color"],
            b"\x01\x02\x03",
        )
        assert nrrd_kinds(data) == ["RGB-color"]

    def test_all_domain_kinds_recognized(self):
        h = Header({"kinds": "domain space time"})
        assert h.domain_axes == [0, 1, 2]
        assert h.range_axes == []


# ---------------------------------------------------------------------------
# FACT-NRRD-105: space / space directions / space origin
# ---------------------------------------------------------------------------


class TestSpaceOrientation:
    def test_load_parses_space_fields(self):
        data = _nrrd_bytes(
            [
                "type: uint8", "dimension: 3", "sizes: 2 2 2", "encoding: raw",
                "space: left-posterior-superior",
                "space directions: (1,0,0) (0,1,0) (0,0,1)",
                "space origin: (0,0,0)",
            ],
            bytes(range(8)),
        )
        model = load_nrrd(data)
        assert model["space"] == "left-posterior-superior"
        assert model["space_directions"] == [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        assert model["space_origin"] == (0.0, 0.0, 0.0)

    def test_header_space_properties(self):
        header = {
            "space": "left-posterior-superior",
            "space directions": "(1,0,0) (0,1,0) (0,0,1)",
            "space origin": "(0,0,0)",
        }
        h = Header(header)
        assert h.space == "left-posterior-superior"
        assert h.space_directions == [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        assert h.space_origin == (0.0, 0.0, 0.0)

    def test_nrrd_document_space_properties(self):
        data = {
            "space": "right-anterior-superior",
            "space_directions": [(2.0, 0.0, 0.0), None],
            "space_origin": (1.0, 1.0),
        }
        doc = NrrdDocument(data)
        assert doc.space == "right-anterior-superior"
        assert doc.space_directions == [(2.0, 0.0, 0.0), None]
        assert doc.space_origin == (1.0, 1.0)

    def test_space_directions_with_non_spatial_axis_marked_none(self):
        # A 4th axis (e.g. color channel) is marked "none" in space directions
        # per spec, distinguishing it from the 3 real spatial axes.
        header = {"space directions": "(1,0,0) (0,1,0) (0,0,1) none"}
        h = Header(header)
        assert h.space_directions == [
            (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), None,
        ]

    def test_missing_space_fields_default_empty(self):
        h = Header({})
        assert h.space == ""
        assert h.space_directions == []
        assert h.space_origin is None

    def test_load_missing_space_fields_default_empty(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        assert model["space"] == ""
        assert model["space_directions"] == []
        assert model["space_origin"] is None

    def test_space_origin_with_negative_and_float_values(self):
        header = {"space origin": "(-12.5,0.25,100)"}
        h = Header(header)
        assert h.space_origin == (-12.5, 0.25, 100.0)


# ---------------------------------------------------------------------------
# FACT-NRRD-106: key/value pair parsing (key:=value)
# ---------------------------------------------------------------------------


class TestKeyValuePairs:
    def test_single_key_value_pair_parses_correctly(self):
        data = _nrrd_bytes(
            ["type: uint8", "dimension: 1", "sizes: 2", "encoding: raw", "mykey:=myvalue"],
            b"\x01\x02",
        )
        model = load_nrrd(data)
        assert model["key_value_pairs"] == {"mykey": "myvalue"}

    def test_key_value_pair_not_polluting_fixed_header_dict(self):
        data = _nrrd_bytes(
            ["type: uint8", "dimension: 1", "sizes: 2", "encoding: raw", "mykey:=myvalue"],
            b"\x01\x02",
        )
        model = load_nrrd(data)
        assert "mykey" not in model["header"]

    def test_no_stray_equals_artifact(self):
        # The historical bug: generic partition(":") on "mykey:=myvalue"
        # would give value "=myvalue" (stray "=" prefix). Confirm it is gone.
        data = _nrrd_bytes(
            ["type: uint8", "dimension: 1", "sizes: 2", "encoding: raw", "mykey:=myvalue"],
            b"\x01\x02",
        )
        model = load_nrrd(data)
        assert model["key_value_pairs"]["mykey"] == "myvalue"
        assert not model["key_value_pairs"]["mykey"].startswith("=")

    def test_multiple_key_value_pairs(self):
        data = _nrrd_bytes(
            [
                "type: uint8", "dimension: 1", "sizes: 2", "encoding: raw",
                "patient_id:=12345", "modality:=MRI",
            ],
            b"\x01\x02",
        )
        model = load_nrrd(data)
        assert model["key_value_pairs"] == {"patient_id": "12345", "modality": "MRI"}

    def test_fixed_fields_still_parse_normally_alongside_kv_pairs(self):
        data = _nrrd_bytes(
            ["type: uint8", "dimension: 1", "sizes: 4", "encoding: raw", "custom:=field"],
            b"\x01\x02\x03\x04",
        )
        model = load_nrrd(data)
        assert model["header"]["type"] == "uint8"
        assert model["header"]["dimension"] == "1"
        assert model["key_value_pairs"] == {"custom": "field"}

    def test_nrrd_document_key_value_pairs_property(self):
        doc = NrrdDocument({"key_value_pairs": {"a": "b"}})
        assert doc.key_value_pairs == {"a": "b"}

    def test_no_key_value_pairs_defaults_empty_dict(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        assert model["key_value_pairs"] == {}

    def test_key_value_pair_survives_write_roundtrip(self):
        model = load_nrrd(VALID_DIR / "1d-int8.nrrd")
        model["key_value_pairs"] = {"acquired_by": "unit-test"}
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "kv-roundtrip.nrrd"
            write_nrrd(model, dest, data=struct.pack("=4b", 1, 2, 3, 4))
            reloaded = load_nrrd(dest)
            assert reloaded["key_value_pairs"] == {"acquired_by": "unit-test"}
            assert reloaded["array"] == [1, 2, 3, 4]

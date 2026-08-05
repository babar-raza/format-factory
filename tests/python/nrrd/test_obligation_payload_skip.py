"""NRRD-PAYLOAD-001 line/byte skip against the shipped namespace.

SAL-NRRD-OBL-DD537F7E8C81FDE6: line skip is applied before byte skip;
positive skips and raw byte-skip -1 (skip to the expected trailing size)
are implemented.

Its prior selectors (tests/python/nrrd/test_nrrd_feature_completeness.py,
class TestLineAndByteSkip) import the deprecated nrrd.* shadow package and
cannot count as shipped-namespace evidence under forbidden_progress_claims
(GAP-018) -- this file proves the same scenarios directly against
format_factory.nrrd instead of porting them by find-and-replace.
"""

from __future__ import annotations

import struct

import pytest

from format_factory.nrrd import NrrdParseError, loads


def _nrrd(fields: list[str], payload: bytes) -> bytes:
    lines = [b"NRRD0004"] + [field.encode("ascii") for field in fields]
    return b"\n".join(lines) + b"\n\n" + payload


def test_byte_skip_offsets_past_junk_bytes() -> None:
    junk = b"\xde\xad\xbe\xef"
    real_payload = struct.pack("=4b", 1, 2, 3, 4)
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 4", "encoding: raw", "byte skip: 4"],
        junk + real_payload,
    )

    document = loads(data)

    assert document.array == [1, 2, 3, 4]
    assert document.header.get("byte skip") == "4"


def test_line_skip_advances_past_whole_lines() -> None:
    real_payload = struct.pack("=2b", 9, 10)
    junk = b"line one\nline two\n"
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw", "line skip: 2"],
        junk + real_payload,
    )

    document = loads(data)

    assert document.array == [9, 10]


def test_no_skip_fields_default_to_zero() -> None:
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw"],
        struct.pack("=2b", 5, 6),
    )

    document = loads(data)

    assert document.array == [5, 6]
    assert "byte skip" not in document.header
    assert "line skip" not in document.header


def test_byte_skip_negative_one_skips_to_expected_tail_size() -> None:
    """"byte skip: -1 => skip len(file) - expected_data_size bytes, i.e. keep
    exactly the trailing expected_data_size bytes as the payload." The
    payload is prefixed with a header of a length this reader cannot know in
    advance -- exactly the scenario byte-skip -1 exists to handle."""
    unknown_length_prefix = b"PROPRIETARY-HEADER-OF-UNKNOWN-LENGTH-1234567890"
    real_payload = struct.pack("=4b", 11, 12, 13, 14)
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 4", "encoding: raw", "byte skip: -1"],
        unknown_length_prefix + real_payload,
    )

    document = loads(data)

    assert document.array == [11, 12, 13, 14]
    assert document.header.get("byte skip") == "-1"


def test_byte_skip_negative_one_is_refused_for_non_raw_encoding() -> None:
    """byte skip -1 depends on computing an expected byte count from the
    declared type/shape alone, which only raw encoding gives directly."""
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 2", "encoding: gzip", "byte skip: -1"],
        b"whatever",
    )

    with pytest.raises(NrrdParseError, match="raw"):
        loads(data)


def test_line_skip_is_applied_before_byte_skip() -> None:
    """Both fields can be declared together; line skip consumes whole lines
    first, then byte skip consumes a fixed count from what remains."""
    real_payload = struct.pack("=2b", 21, 22)
    junk_line = b"skip-me\n"
    junk_bytes = b"XX"
    data = _nrrd(
        [
            "type: int8",
            "dimension: 1",
            "sizes: 2",
            "encoding: raw",
            "line skip: 1",
            "byte skip: 2",
        ],
        junk_line + junk_bytes + real_payload,
    )

    document = loads(data)

    assert document.array == [21, 22]


def test_line_skip_beyond_available_lines_is_refused() -> None:
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw", "line skip: 5"],
        b"only one line\n",
    )

    with pytest.raises(NrrdParseError, match="line skip"):
        loads(data)


def test_byte_skip_beyond_payload_is_refused() -> None:
    data = _nrrd(
        ["type: int8", "dimension: 1", "sizes: 2", "encoding: raw", "byte skip: 100"],
        b"too short",
    )

    with pytest.raises(NrrdParseError, match="byte skip"):
        loads(data)

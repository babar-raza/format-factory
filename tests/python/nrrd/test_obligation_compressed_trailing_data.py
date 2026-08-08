"""NRRD-VALIDATE-001 -- trailing data after a complete compressed payload.

MUST (SAL-NRRD-OBL-9C262130232DCD09): validate declared payload size with
checked arithmetic; hostile headers must fail cheaply.

Before this slice, extra bytes appended after a complete, valid gzip or
bzip2 stream were silently ignored: zlib.decompressobj/bz2.BZ2Decompressor
both stop decoding once the compressed stream's own EOF marker is reached
and expose the leftover bytes via `.unused_data`, but decode_encoding()
never checked that attribute. Attached-raw payloads were already protected
by decode_binary()'s exact-length check downstream; compressed encodings
had no equivalent guard.

MUST (SAL-NRRD-OBL-2085AD256AFE6E96): "treat trailing payload per policy
with reporting." The rejection above happened only via a raised
NrrdParseError at load time, before `validate()` -- which accepted only an
already-loaded NrrdDocument/mapping -- could ever run on the offending
source. `validate()` now also accepts a raw source (bytes, path, or
stream) directly and reports this same rejection as a non-raising FATAL
Diagnostic, the same way every other check in `validate()` already works.
The rejection itself is unchanged and unweakened -- hostile trailing data
still fails; only how a caller learns about it changed.
"""

from __future__ import annotations

import bz2
import gzip

import pytest

from format_factory.nrrd import NrrdParseError, loads, validate

_HEADER = b"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: {}\n\n"


def _source(encoding: str, payload: bytes, *, trailing: bytes = b"") -> bytes:
    return _HEADER.replace(b"{}", encoding.encode()) + payload + trailing


def test_a_clean_gzip_payload_still_loads() -> None:
    payload = gzip.compress(b"\x01\x02")

    document = loads(_source("gzip", payload))

    assert document.encoding == "gzip"


def test_a_clean_bzip2_payload_still_loads() -> None:
    payload = bz2.compress(b"\x01\x02")

    document = loads(_source("bzip2", payload))

    assert document.encoding == "bzip2"


def test_trailing_bytes_after_a_complete_gzip_stream_are_rejected() -> None:
    payload = gzip.compress(b"\x01\x02")

    with pytest.raises(NrrdParseError, match="trailing data after gzip payload"):
        loads(_source("gzip", payload, trailing=b"EXTRA"))


def test_trailing_bytes_after_a_complete_bzip2_stream_are_rejected() -> None:
    payload = bz2.compress(b"\x01\x02")

    with pytest.raises(NrrdParseError, match="trailing data after bzip2 payload"):
        loads(_source("bzip2", payload, trailing=b"EXTRA"))


def test_a_second_concatenated_gzip_member_is_rejected_as_trailing_data() -> None:
    payload = gzip.compress(b"\x01\x02") + gzip.compress(b"\x03\x04")

    with pytest.raises(NrrdParseError, match="trailing data after gzip payload"):
        loads(_source("gzip", payload))


def test_validate_reports_trailing_gzip_data_as_a_fatal_diagnostic_not_a_raise() -> None:
    payload = gzip.compress(b"\x01\x02")
    source = _source("gzip", payload, trailing=b"EXTRA")

    report = validate(source)

    assert report.is_valid is False
    assert len(report.diagnostics) == 1
    diagnostic = report.diagnostics[0]
    assert diagnostic.code == "nrrd.source.unreadable"
    assert diagnostic.severity == "fatal"
    assert "trailing data after gzip payload" in diagnostic.message


def test_validate_reports_trailing_bzip2_data_as_a_fatal_diagnostic_not_a_raise() -> None:
    payload = bz2.compress(b"\x01\x02")
    source = _source("bzip2", payload, trailing=b"EXTRA")

    report = validate(source)

    assert report.is_valid is False
    diagnostic = report.diagnostics[0]
    assert diagnostic.code == "nrrd.source.unreadable"
    assert "trailing data after bzip2 payload" in diagnostic.message


def test_validate_still_accepts_a_clean_gzip_source_with_no_diagnostics() -> None:
    payload = gzip.compress(b"\x01\x02")

    report = validate(_source("gzip", payload))

    assert report.is_valid is True
    assert report.diagnostics == ()

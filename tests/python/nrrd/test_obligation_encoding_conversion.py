"""NRRD-CONVERT-001 -- encoding conversion (the "encoding" half of the
compound rule_text convert_dtype/convert_endian cover the other halves of;
see test_obligation_dtype_conversion.py).

POL-SCR-CONVERT-01 (SHOULD): "Convert dtype, encoding, attached/detached
form, and endian with explicit overflow/clipping/scaling/rounding policies
and a conversion report."

Encoding conversion is lossless by construction -- the writer already
recomputes payload bytes fresh from a document's own decoded `array` on
every dumps() call, never reading old payload bytes, so switching encodings
needs no overflow/clipping/rounding policy the way dtype conversion does.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdWriteError, convert_encoding, dumps, loads

_HEADER = b"NRRD0004\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n"
_PAYLOAD = bytes([10, 20, 30, 40])


def _document():
    return loads(_HEADER + _PAYLOAD)


@pytest.mark.parametrize("target", ["gzip", "bzip2", "ascii", "hex", "raw"])
def test_converting_to_every_supported_encoding_round_trips_the_same_values(target: str) -> None:
    document = _document()

    converted, report = convert_encoding(document, target)
    written = dumps(converted)
    reloaded = loads(written)

    assert reloaded.encoding == target
    assert reloaded.array == document.array
    assert report.source_encoding == "raw"
    assert report.target_encoding == target
    assert report.is_lossless is True


def test_convert_encoding_is_case_insensitive_on_the_target_name() -> None:
    document = _document()

    converted, report = convert_encoding(document, "GZIP")

    assert converted.encoding == "gzip"
    assert report.target_encoding == "gzip"


def test_convert_encoding_refuses_an_unsupported_encoding_name() -> None:
    document = _document()

    with pytest.raises(NrrdWriteError, match="unsupported NRRD encoding"):
        convert_encoding(document, "not-a-real-encoding")


def test_convert_encoding_does_not_mutate_the_source_document() -> None:
    document = _document()

    convert_encoding(document, "gzip")

    assert document.encoding == "raw"


def test_converting_to_the_same_encoding_is_a_no_op_round_trip() -> None:
    document = _document()

    converted, report = convert_encoding(document, "raw")

    assert converted.encoding == "raw"
    assert converted.array == document.array
    assert report.source_encoding == report.target_encoding == "raw"

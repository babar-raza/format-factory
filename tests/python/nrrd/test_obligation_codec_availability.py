"""NRRD-ENC-001 against the shipped namespace.

MUST (SAL-NRRD-OBL-09FD9B976DEEA254): "Read and write every specified
encoding using the correct container framing; expose codec availability;
fail explicitly when an optional codec is unavailable."

Before this slice: bz2 was imported unconditionally at module level, so
an interpreter built without libbz2 support (a real, documented CPython
possibility -- some minimal/container Python builds omit it) would fail
to import format_factory.nrrd at all, with no codec-availability API and
no explicit, targeted failure at the point of use. gzip and zlib are, for
all practical purposes, always present (required internally for zip/wheel
handling) and are not given this treatment.

This file proves the new available_encodings() function and the explicit
refusal path, using monkeypatch to simulate an interpreter where bz2 is
absent -- the same technique this session already used elsewhere to
simulate conditions the current environment cannot naturally produce.
"""

from __future__ import annotations

import bz2

import pytest

from format_factory.core import DEFAULT_LIMITS
from format_factory.nrrd import NrrdParseError, NrrdWriteError, available_encodings, loads
from format_factory.nrrd.codec import SUPPORTED_ENCODINGS
from format_factory.nrrd.codec import payload as payload_module


def _bzip2_document() -> bytes:
    header = (
        b"NRRD0004\ntype: int8\ndimension: 1\nsizes: 2\nencoding: bzip2\n\n"
    )
    return header + bz2.compress(bytes([7, 8]))


def test_available_encodings_matches_supported_encodings_when_bz2_is_present() -> None:
    assert available_encodings() == SUPPORTED_ENCODINGS


def test_a_bzip2_document_loads_normally_when_bz2_is_available() -> None:
    document = loads(_bzip2_document())

    assert document.array == [7, 8]


def test_available_encodings_excludes_bzip2_when_bz2_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(payload_module, "bz2", None)

    available = payload_module.available_encodings()

    assert "bzip2" not in available
    assert "bz2" not in available
    assert available == SUPPORTED_ENCODINGS - {"bzip2", "bz2"}
    assert "gzip" in available and "raw" in available


def test_decoding_bzip2_without_bz2_fails_explicitly_not_with_an_attribute_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(payload_module, "bz2", None)

    with pytest.raises(NrrdParseError, match="bz2 module"):
        loads(_bzip2_document())


def test_encoding_bzip2_without_bz2_fails_explicitly_not_with_an_attribute_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(payload_module, "bz2", None)

    with pytest.raises(NrrdWriteError, match="bz2 module"):
        payload_module.encode_encoding(
            bytes([1, 2]), [1, 2], "bzip2", limits=DEFAULT_LIMITS
        )


def test_gzip_is_unaffected_by_bz2_being_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only bz2 is guarded -- gzip/zlib must keep working regardless."""
    monkeypatch.setattr(payload_module, "bz2", None)

    encoded = payload_module.encode_encoding(
        bytes([3, 4]), [3, 4], "gzip", limits=DEFAULT_LIMITS
    )
    decoded = payload_module.decode_encoding(encoded, "gzip", limits=DEFAULT_LIMITS)

    assert decoded == bytes([3, 4])

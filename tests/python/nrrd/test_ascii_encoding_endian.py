"""TC-FF6-NRRD-ASCII-ENDIAN-001: `endian` is an encoding-scoped requirement.

`shared/sal-facts/nrrd.yaml` fact SAL-NRRD-00014 requires `endian` "whenever
the encoding exposes byte order and the element size exceeds one byte". The
textual encodings (`ascii`/`text`/`txt`) carry decimal text, not raw elements,
so they expose no byte order -- and Teem 1.12.0 (`unu`) reads such files
without an `endian` field.

These tests pin both halves of that rule: the textual encodings must not demand
`endian`, and every byte-order-exposing encoding must keep demanding it, so the
guarantee TC-FF6-NRRD-GOLDEN-SLICE-001 established cannot silently regress.

Obligations: SAL-NRRD-OBL-644276A28216DFC0, SAL-NRRD-OBL-5FAF36D205C887AD.
"""

from __future__ import annotations

import bz2
import gzip
import struct
from binascii import hexlify

import pytest

from format_factory.nrrd import (
    NrrdDocument,
    NrrdParseError,
    NrrdWriteError,
    dumps,
    loads,
)

TEXTUAL_ENCODINGS = ["ascii", "text", "txt"]
BYTE_ORDER_EXPOSING_ENCODINGS = ["raw", "gzip", "gz", "bzip2", "bz2", "hex"]


def _header(encoding: str, *, endian: str | None = None, nrrd_type: str = "uint16",
            sizes: str = "3", dimension: str = "1") -> bytes:
    lines = [
        b"NRRD0005",
        f"type: {nrrd_type}".encode("ascii"),
        f"dimension: {dimension}".encode("ascii"),
        f"sizes: {sizes}".encode("ascii"),
    ]
    if endian is not None:
        lines.append(f"endian: {endian}".encode("ascii"))
    lines.append(f"encoding: {encoding}".encode("ascii"))
    return b"\n".join(lines) + b"\n\n"


def _binary_payload(encoding: str, values: tuple[int, ...] = (1, 2, 3)) -> bytes:
    raw = struct.pack(f"<{len(values)}H", *values)
    if encoding == "raw":
        return raw
    if encoding in {"gzip", "gz"}:
        return gzip.compress(raw, mtime=0)
    if encoding in {"bzip2", "bz2"}:
        return bz2.compress(raw)
    if encoding == "hex":
        return hexlify(raw)
    raise AssertionError(f"unhandled encoding {encoding!r}")


# ── RED 1-2: textual encodings must read without an endian field ────────────


@pytest.mark.parametrize("encoding", TEXTUAL_ENCODINGS)
def test_textual_encoding_reads_without_endian(encoding: str) -> None:
    """Teem accepts this exact input; rejecting it is an interop defect."""
    document = loads(_header(encoding) + b"1 2 3\n")
    assert document.array == [1, 2, 3]


@pytest.mark.parametrize("nrrd_type,values", [
    ("int16", [258, -2, 7]),
    ("uint32", [16909060, 0, 5]),
    ("int64", [72623859790382856, -1, 3]),
    ("double", [1.5, -2.25, 0.0]),
])
def test_every_multibyte_type_reads_as_text_without_endian(
    nrrd_type: str, values: list[float]
) -> None:
    """The endian requirement is scoped by encoding, not by element width."""
    payload = " ".join(repr(v) for v in values).encode("ascii") + b"\n"
    document = loads(_header("ascii", nrrd_type=nrrd_type) + payload)
    assert document.array == values


# ── RED 3-4: textual encodings must write and round-trip without endian ─────


@pytest.mark.parametrize("encoding", TEXTUAL_ENCODINGS)
def test_textual_encoding_writes_without_endian(encoding: str) -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16", "dimension": "1", "sizes": "3", "encoding": encoding,
        },
        payload=b"",
        array=[1, 2, 3],
    )
    encoded = dumps(document)
    assert b"endian" not in encoded, "no byte order is exposed, so none is declared"
    assert loads(encoded).array == [1, 2, 3]


def test_textual_roundtrip_without_endian_is_stable() -> None:
    original = loads(_header("ascii") + b"1 2 3\n")
    replayed = loads(dumps(original))
    assert replayed.array == original.array == [1, 2, 3]


# ── RED 5: the golden slice's guarantee must not regress ────────────────────


@pytest.mark.parametrize("encoding", BYTE_ORDER_EXPOSING_ENCODINGS)
def test_byte_order_exposing_encoding_still_requires_endian(encoding: str) -> None:
    """The encoding dimension SAL-NRRD-OBL-644276A28216DFC0 actually asks for."""
    with pytest.raises(NrrdParseError, match="endian"):
        loads(_header(encoding) + _binary_payload(encoding))


@pytest.mark.parametrize("encoding", BYTE_ORDER_EXPOSING_ENCODINGS)
def test_byte_order_exposing_encoding_accepts_declared_endian(encoding: str) -> None:
    document = loads(
        _header(encoding, endian="little") + _binary_payload(encoding)
    )
    assert document.array == [1, 2, 3]


# ── RED 6-7: a declared endian is still honored and still validated ─────────


def test_declared_endian_on_textual_encoding_is_preserved() -> None:
    """Declaring it is legal and lossless even though it is not load-bearing."""
    encoded = dumps(loads(_header("ascii", endian="big") + b"1 2 3\n"))
    assert b"endian: big" in encoded


@pytest.mark.parametrize("bad_endian", ["middle", "LITTLE-ish", "0", "network"])
def test_invalid_endian_token_is_rejected_even_for_textual_encoding(
    bad_endian: str,
) -> None:
    """A declared value must be well-formed whether or not it is used."""
    with pytest.raises(NrrdParseError, match="endian"):
        loads(_header("ascii", endian=bad_endian) + b"1 2 3\n")


def test_one_byte_type_needs_no_endian_in_any_encoding() -> None:
    for encoding in TEXTUAL_ENCODINGS + ["raw"]:
        payload = b"1 2 3\n" if encoding in TEXTUAL_ENCODINGS else bytes([1, 2, 3])
        document = loads(_header(encoding, nrrd_type="uint8") + payload)
        assert document.array == [1, 2, 3], encoding


# ── RED 8: a write failure must surface as a write error ────────────────────


def test_missing_endian_on_binary_write_raises_write_error() -> None:
    """`dumps()` failing is a write failure, whatever helper detected it."""
    document = NrrdDocument(
        version=5,
        header={"type": "uint16", "dimension": "1", "sizes": "3", "encoding": "raw"},
        payload=b"",
        array=[1, 2, 3],
    )
    with pytest.raises(NrrdWriteError, match="endian"):
        dumps(document)


def test_invalid_endian_on_binary_write_raises_write_error() -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16", "dimension": "1", "sizes": "3",
            "encoding": "raw", "endian": "sideways",
        },
        payload=b"",
        array=[1, 2, 3],
    )
    with pytest.raises(NrrdWriteError, match="endian"):
        dumps(document)


@pytest.mark.parametrize("encoding", BYTE_ORDER_EXPOSING_ENCODINGS)
def test_write_requires_endian_for_every_byte_order_exposing_encoding(
    encoding: str,
) -> None:
    """The write half of the by-type-and-encoding matrix.

    The read half is covered above; without this, "endian is required" would be
    proven on output for `raw` only.
    """
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16", "dimension": "1", "sizes": "3", "encoding": encoding,
        },
        payload=b"",
        array=[1, 2, 3],
    )
    with pytest.raises(NrrdWriteError, match="endian"):
        dumps(document)


@pytest.mark.parametrize("encoding", TEXTUAL_ENCODINGS)
def test_write_needs_no_endian_for_textual_encoding(encoding: str) -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint16", "dimension": "1", "sizes": "3", "encoding": encoding,
        },
        payload=b"",
        array=[1, 2, 3],
    )
    assert loads(dumps(document)).array == [1, 2, 3]


# ── An explicitly empty endian value is a declaration of nothing ────────────


@pytest.mark.parametrize("encoding,payload", [
    ("raw", struct.pack("<3H", 1, 2, 3)),
    ("ascii", b"1 2 3\n"),
])
def test_explicitly_empty_endian_value_is_rejected_as_malformed(
    encoding: str, payload: bytes
) -> None:
    """A literal `endian:` line with no value, distinct from omitting the line.

    The golden slice's parametrized case *skips* this: it builds the header with
    `endian=bad or None`, so the empty string collapses into the omitted-field
    case and the "empty endian value" negative proof was never actually taken.

    An empty value is rejected as malformed header syntax -- a general rule
    covering every field, not endian semantics -- which is why it is rejected
    for the textual encoding too. Teem 1.12.0 rejects this same input for both
    encodings, so failing closed here matches the reference implementation
    rather than diverging from it.
    """
    header = (
        b"NRRD0005\ntype: uint16\ndimension: 1\nsizes: 3\n"
        b"endian: \n" + f"encoding: {encoding}\n".encode("ascii") + b"\n"
    )
    with pytest.raises(NrrdParseError, match="malformed header field"):
        loads(header + payload)

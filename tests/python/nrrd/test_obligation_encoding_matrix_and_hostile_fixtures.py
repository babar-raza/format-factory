"""NRRD-ENC-001 -- the exhaustive magic/type/encoding/endian/attachment
cross-product and hostile-fixture matrix.

MUST (SAL-NRRD-OBL-5A7992A6D1561C1D): "Test every magic version, every
type alias, every encoding, endian combinations, attached plus all
detached data-file forms, and hostile fixtures (decompression bombs,
overflow shapes, traversal paths, truncated payloads)."

Before this file: every one of these dimensions had SOME coverage, but
almost always in isolation -- every scalar type alias was tested, but
only with `encoding: raw`; every encoding was tested, but only with a
single fixed type; every magic version was tested, but only for
version-gating rules, never crossed with the encoding matrix at all;
detached forms (single/LIST/printf) were tested, but every one of their
own fixtures hardcoded `encoding: raw`. Two of the four named hostile
-fixture categories had a real, disclosed gap: a mid-stream-truncated
COMPRESSED payload (gzip or bzip2) had zero coverage (the existing
truncation tests only truncate a raw payload), and no test fed malformed
hex text at all. This file closes those specific, verified gaps.

Deliberately NOT attempted here, and not claimed: "independent oracle
runs" (this obligation's own proof_requirements name Teem/pynrrd
comparisons) -- investigated directly before writing this file and found
a genuine, unresolved blocker: this package's own top-level `nrrd`
distribution shares its exact import name with the real `pynrrd` package
(the `reference` optional extra already declared in pyproject.toml), so
installing pynrrd would shadow this project's own legacy `nrrd.*` shim
that ~17 other test files already import, breaking them. Resolving that
(a subprocess-isolated oracle, a renamed shim, or an aliased import
loader) is real, separate architectural work affecting at least nrrd and
safetensors identically -- not something to fold silently into a test
-matrix expansion. Not attempted here; disclosed, not force-built.
"""

from __future__ import annotations

import bz2
import gzip
from pathlib import Path

import pytest

from format_factory.core import ResourceLimitError
from format_factory.nrrd import (
    NrrdDocument,
    NrrdParseError,
    dump_detached,
    dump_multifile,
    dump_multifile_printf,
    dumps,
    load,
    loads,
)

# One representative alias per distinct byte width / kind the codec
# actually branches on (codec/payload.py::_DTYPE_ALIASES) -- not all 40
# aliases, since every alias already round-trips through `encoding: raw`
# via test_production_namespace.py::test_every_normative_scalar_type_alias_roundtrips
# (alias resolution is a separate, already-fully-covered concern from
# byte-width/endian-swap correctness, which is what crossing against
# encoding/endian actually exercises).
_REPRESENTATIVE_TYPES = ["int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "float", "double"]
_ENCODINGS = ["raw", "gzip", "bzip2", "hex", "ascii"]
#: Only encodings whose payload exposes no byte order at all (SAL-NRRD-00014)
#: skip endian -- hex is still byte-order-exposing (it hex-encodes the raw
#: bytes verbatim), unlike ascii's decimal text.
_TEXTUAL_ENCODINGS = {"ascii"}


def _values_for(nrrd_type: str, count: int) -> list[int | float]:
    if nrrd_type in ("float", "double"):
        return [float(i) + 0.5 for i in range(count)]
    return [i for i in range(count)]


def _document(nrrd_type: str, encoding: str, *, endian: str = "little") -> NrrdDocument:
    header = {
        "type": nrrd_type,
        "dimension": "1",
        "sizes": "4",
        "encoding": encoding,
    }
    if nrrd_type != "uint8" and nrrd_type != "int8" and encoding not in _TEXTUAL_ENCODINGS:
        header["endian"] = endian
    return NrrdDocument(version=5, header=header, payload=b"", array=_values_for(nrrd_type, 4))


# ── Type x encoding x endian cross product ───────────────────────────────


@pytest.mark.parametrize("nrrd_type", _REPRESENTATIVE_TYPES)
@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_representative_type_encoding_matrix_round_trips(nrrd_type: str, encoding: str) -> None:
    document = _document(nrrd_type, encoding)

    encoded = dumps(document)
    reloaded = loads(encoded)

    assert reloaded.array == document.array
    assert reloaded.header["type"] == nrrd_type
    assert reloaded.header["encoding"] == encoding


@pytest.mark.parametrize("nrrd_type", ["int16", "uint32", "int64", "double"])
@pytest.mark.parametrize("encoding", ["raw", "gzip", "bzip2", "hex"])
def test_representative_type_encoding_matrix_round_trips_big_endian(
    nrrd_type: str, encoding: str
) -> None:
    """Same cross product, opposite byte order -- big-endian was
    previously only exercised against a single fixed 3-element fixture
    (test_ascii_encoding_endian.py), never against this many distinct
    byte widths x encodings together."""
    document = _document(nrrd_type, encoding, endian="big")

    encoded = dumps(document)
    reloaded = loads(encoded)

    assert reloaded.array == document.array
    assert reloaded.header.get("endian") == "big"


# ── Magic version x encoding cross product ────────────────────────────────


@pytest.mark.parametrize("version", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_every_magic_version_round_trips_across_every_encoding(version: int, encoding: str) -> None:
    """Every prior encoding test hardcoded NRRD0004 or NRRD0005. type/
    dimension/sizes/encoding/endian are all baseline (version-independent)
    fields (SAL-NRRD-00010), so this crosses the full encoding matrix
    against every magic this package accepts, not just the newest one."""
    header_text = f"NRRD000{version}\ntype: uint16\ndimension: 1\nsizes: 3\nencoding: {encoding}\n"
    if encoding not in _TEXTUAL_ENCODINGS:
        header_text += "endian: little\n"
    header = header_text.encode() + b"\n"

    values = [10, 20, 30]
    payload_document = NrrdDocument(
        version=version,
        header={
            "type": "uint16",
            "dimension": "1",
            "sizes": "3",
            "encoding": encoding,
            **({} if encoding in _TEXTUAL_ENCODINGS else {"endian": "little"}),
        },
        payload=b"",
        array=values,
    )
    # Build the payload bytes the same way the writer would, independent
    # of the hand-written header above, then splice them together --
    # proves the reader accepts this encoding under this specific magic,
    # not merely that dumps()/loads() agree with themselves.
    full = dumps(payload_document)
    payload_bytes = full.split(b"\n\n", 1)[1]

    reloaded = loads(header + payload_bytes)
    assert reloaded.array == values


# ── Detached forms x encoding cross product ──────────────────────────────


@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_single_file_detached_form_across_every_encoding(encoding: str, tmp_path: Path) -> None:
    document = _document(encoding=encoding, nrrd_type="uint16")
    header_path = tmp_path / f"single-{encoding}.nhdr"
    payload_path = tmp_path / f"single-{encoding}.data"

    dump_detached(document, header_path, payload_path)
    reloaded = load(header_path)

    assert reloaded.array == document.array


@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_list_detached_form_across_every_encoding(encoding: str, tmp_path: Path) -> None:
    """A single-entry LIST -- proves the LIST detached FORM works under
    every encoding; even-split arithmetic across multiple LIST files is a
    separate, already-covered concern (test_obligation_multifile_writer.py)
    this test does not re-exercise."""
    document = _document(encoding=encoding, nrrd_type="uint16")
    header_path = tmp_path / f"list-{encoding}.nhdr"
    part = tmp_path / f"list-{encoding}-0.data"

    dump_multifile(document, header_path, [part])
    reloaded = load(header_path)

    assert reloaded.array == document.array


@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_printf_detached_form_across_every_encoding(encoding: str, tmp_path: Path) -> None:
    """A single-file printf sequence (file_count=1) -- proves the printf
    detached FORM works under every encoding, for the same reason
    test_list_detached_form_across_every_encoding above uses one file."""
    document = _document(encoding=encoding, nrrd_type="uint16")
    header_path = tmp_path / f"printf-{encoding}.nhdr"

    dump_multifile_printf(
        document, header_path, "part-%d.data", start=0, step=1, file_count=1
    )
    reloaded = load(header_path)

    assert reloaded.array == document.array


# ── Hostile fixtures: the two previously zero-coverage branches ─────────


def _minimal_header(encoding: str) -> bytes:
    return (
        f"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 64\nencoding: {encoding}\n\n"
    ).encode()


def test_mid_stream_truncated_gzip_payload_is_rejected() -> None:
    """codec/payload.py's own "truncated gzip payload" branch
    (decode_encoding, `if not gzip_decoder.eof`) had zero test coverage --
    every existing gzip truncation test truncates a RAW payload, not a
    compressed stream that is itself cut short mid-stream."""
    complete = gzip.compress(bytes(64))
    truncated = complete[: len(complete) - 4]

    with pytest.raises(NrrdParseError, match="truncated gzip payload"):
        loads(_minimal_header("gzip") + truncated)


def test_mid_stream_truncated_bzip2_payload_is_rejected() -> None:
    """The bzip2 sibling of the gzip case above -- codec/payload.py's own
    "truncated or oversized bzip2 payload" branch, also previously
    uncovered."""
    complete = bz2.compress(bytes(64))
    truncated = complete[: len(complete) - 4]

    with pytest.raises(NrrdParseError, match="truncated or oversized bzip2 payload"):
        loads(_minimal_header("bzip2") + truncated)


def test_malformed_hex_payload_is_rejected() -> None:
    """codec/payload.py's own "invalid hexadecimal payload" branch
    (bytes.fromhex ValueError) had zero test coverage -- no test fed
    odd-length or non-hex text through the hex decoder before this."""
    odd_length_hex = b"0" * 127  # 64 declared bytes needs exactly 128 hex chars

    with pytest.raises(NrrdParseError, match="invalid hexadecimal payload"):
        loads(_minimal_header("hex") + odd_length_hex)


def test_a_bzip2_bomb_disproportionate_to_the_declared_shape_fails_cheaply() -> None:
    """The bzip2 sibling of test_obligation_security_baseline.py's own
    gzip-bomb test -- SAL-NRRD-OBL-9C262130232DCD09 (NRRD-VALIDATE-001)
    applies identically to bzip2, but only gzip had a dedicated bomb test
    before this."""
    header = _minimal_header("bzip2").replace(b"sizes: 64", b"sizes: 10")
    bomb = bz2.compress(bytes(5 * 1024 * 1024))

    with pytest.raises(ResourceLimitError, match="decompression limit"):
        loads(header + bomb)


def test_list_entry_path_traversal_is_rejected(tmp_path: Path) -> None:
    """Existing traversal coverage (test_production_namespace.py,
    test_obligation_security_baseline.py, etc.) all target a single
    -file `data file:` declaration. A LIST entry naming a traversal path
    had no dedicated test."""
    header_path = tmp_path / "list-traversal.nhdr"
    header_path.write_bytes(
        b"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n"
        b"data file: LIST\n../escape.raw\n\n"
    )

    with pytest.raises(NrrdParseError):
        load(header_path)


def test_printf_expanded_path_traversal_is_rejected(tmp_path: Path) -> None:
    """The printf-sequence sibling of the LIST traversal case above."""
    header_path = tmp_path / "printf-traversal.nhdr"
    header_path.write_bytes(
        b"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n"
        b"data file: ../escape-%d.raw 0 0 1\n\n"
    )

    with pytest.raises(NrrdParseError):
        load(header_path)

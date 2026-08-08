"""NRRD-WRITE-001 against the shipped namespace.

MUST (SAL-NRRD-OBL-284E2438B08DA529): "Write required/conditional fields
correctly with version selection honoring used features; preserve optional
absence in lossless mode; deterministic field ordering and detached-partition
policies."

required_tests: "Version-selection fixtures; determinism byte-compare;
detached-partition round trips."

Version-selection fixtures already exist (test_obligation_version_selection.py,
mapped to the sibling NRRD-VERSION-001/NRRD-LIFECYCLE-001 obligations but
exercising this same writer). This file closes the two remaining, previously
unproven pieces of NRRD-WRITE-001's own required_tests directly:

Determinism byte-compare: `dumps()` in canonical mode must produce
byte-identical output across repeated calls on the same document -- proven
directly rather than assumed from the absence of any observed nondeterminism
(`_header_bytes` iterates a fixed `_FIELD_ORDER` tuple plus `sorted()` for
everything else, so this is a property of the implementation, not luck).

Detached-partition round trips: investigated directly rather than assumed
missing. `dump_multifile()` and `dump_multifile_printf()` (codec/writer/
writer.py, FF6-EVENT-000303/000305) already implement the multi-file
detached-partition writer this obligation's own missing_behavior text called
absent; NRRD-MULTIFILE-001 (SAL-NRRD-OBL-807586E5B4D0EDB2 /
SAL-NRRD-OBL-EBE5230D5204B4AD, both already `implemented`) already carries
extensive coverage of those two functions in their own right (uneven-split
refusal, cross-directory refusal, version-gate refusal, compressed payloads).
"No detached partition writer" was therefore stale text on THIS obligation's
own evidence entry, not a real product gap -- the capability exists under a
sibling obligation ID. This file adds a direct, freestanding round-trip proof
scoped to NRRD-WRITE-001 itself (exercising the writer functions directly,
not through NRRD-CONVERT-001's convert_to_detached_* wrapper layer) rather
than merely re-citing the sibling obligation's own tests as if they were this
obligation's.

Optional-field absence in canonical mode: proven directly. `_header_bytes`
iterates `document.header` (a plain `dict[str, str]`) and emits exactly the
keys present in it, in a fixed order -- a field absent from that dict at load
time is never synthesized on write, and a field present is always re-emitted
unchanged. This is the field-presence policy the writer itself owns; the
deeper question of whether an EXPLICIT default value and an ABSENT optional
field are modeled as distinguishable states in the first place is
NRRD-PRESERVE-001's own, separate, still-partial scope (SAL-NRRD-OBL-
ADAC45BDF110C59C) -- not duplicated or closed here.

Lossless-mode absence preservation needs no dedicated test here: `dumps(mode=
"lossless")` returns `document.source_bytes` verbatim (see writer.py's own
`dumps()`), so it is byte-identical to the original source by construction,
already covered by this format's existing round-trip/preservation test
suites.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from format_factory.nrrd import (
    NrrdDocument,
    dump_multifile,
    dump_multifile_printf,
    dumps,
    load,
    loads,
)


def _document(sizes: str = "2 2 2", payload: bytes = bytes(range(8))) -> NrrdDocument:
    header = f"NRRD0004\ntype: uint8\ndimension: 3\nsizes: {sizes}\nencoding: raw\n\n".encode()
    return loads(header + payload)


# ── Determinism ──────────────────────────────────────────────────────────────


def test_repeated_dumps_calls_on_the_same_document_are_byte_identical() -> None:
    document = _document()

    first = dumps(document)
    second = dumps(document)
    third = dumps(document)

    assert first == second == third


def test_field_order_is_stable_across_repeated_calls_regardless_of_dict_insertion() -> None:
    """`_header_bytes` orders fields by a fixed tuple plus `sorted()`, not by
    dict insertion order -- rebuilding an equivalent document from a
    differently-ordered header mapping still produces identical bytes."""
    header_a = "NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: raw\n\n"
    payload = bytes(range(8))
    document = loads(header_a.encode() + payload)

    reordered = NrrdDocument.from_mapping(
        {
            "version": document.version,
            "header": {
                "encoding": document.header["encoding"],
                "sizes": document.header["sizes"],
                "type": document.header["type"],
                "dimension": document.header["dimension"],
            },
            "array": document.array,
        }
    )

    assert dumps(document) == dumps(reordered)


# ── Detached-partition round trips (direct, not via convert.py's wrapper) ──


def test_dump_multifile_round_trips_directly(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"
    parts: list[str | PathLike[str]] = [tmp_path / "a.raw", tmp_path / "b.raw"]

    dump_multifile(document, header_path, parts)
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_dump_multifile_printf_round_trips_directly(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(
        document, header_path, "part%d.raw", start=0, step=1, file_count=2
    )
    reloaded = load(header_path)

    assert reloaded.array == document.array


# ── Optional-field absence in canonical mode ────────────────────────────────


def test_a_field_absent_from_the_loaded_header_is_not_synthesized_on_write() -> None:
    """"space origin" is optional; a document that never declared it must
    not gain one just because it was written out and back."""
    document = _document()
    assert "space origin" not in document.header

    written = dumps(document)

    assert b"space origin" not in written


def test_a_field_present_in_the_loaded_header_is_reemitted_unchanged() -> None:
    header = (
        "NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: raw\n"
        "space origin: (0,0,0)\nspace: right-anterior-superior\n\n"
    )
    document = loads(header.encode() + bytes(range(8)))
    assert "space origin" in document.header

    written = dumps(document)

    assert b"space origin: (0,0,0)" in written

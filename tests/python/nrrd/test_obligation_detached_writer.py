"""NRRD-PAYLOAD-001 -- writer support for detached (header + separate
payload file) output.

MUST (SAL-NRRD-OBL-9FFEE6E206F405F4; Teem NRRD Format Specification
Sections 1.2, 3, and 5): "Across NRRD0001 through NRRD0005, payload data
is either attached after the header blank line or stored in one detached
file named by the data file field."

Before this slice: writer.py only ever emitted attached payloads --
dumps()/dump() always embed the encoded payload directly after the
header's blank-line terminator, with no way to write a `data file:` field
and a separate payload file. dump_detached() closes this: the header
(carrying a `data file:` field naming the payload's path relative to the
header's own directory) and the encoded payload are written to two
separate destinations, round-tripping correctly through the existing
detached-read path (reader.py's _safe_detached_payload).

Scope, stated plainly: this writes the single-file detached form only
(matching the reader's most common detached case), not the multi-file
LIST/printf sequence forms -- those remain a genuinely separate, larger
feature (splitting one array's encoded bytes across multiple files),
correctly out of scope for this slice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import dump_detached, load, loads
from format_factory.nrrd.errors import NrrdWriteError


def _attached_source(payload: bytes = b"\x01\x02\x03\x04") -> bytes:
    return (
        f"NRRD0005\ntype: uint8\ndimension: 1\nsizes: {len(payload)}\n"
        "encoding: raw\n\n"
    ).encode() + payload


def test_detached_write_produces_a_header_with_a_data_file_field(
    tmp_path: Path,
) -> None:
    document = loads(_attached_source())
    header_path = tmp_path / "out.nhdr"
    payload_path = tmp_path / "out.raw"

    dump_detached(document, header_path, payload_path)

    header_text = header_path.read_bytes().decode("ascii")
    assert "data file: out.raw" in header_text
    assert payload_path.read_bytes() == b"\x01\x02\x03\x04"


def test_detached_write_round_trips_through_load(tmp_path: Path) -> None:
    document = loads(_attached_source(b"\xaa\xbb\xcc"))
    header_path = tmp_path / "d.nhdr"
    payload_path = tmp_path / "d.raw"

    dump_detached(document, header_path, payload_path)
    reloaded = load(header_path)

    assert reloaded.array == [170, 187, 204]


def test_detached_write_supports_a_payload_in_a_subdirectory(tmp_path: Path) -> None:
    document = loads(_attached_source())
    header_path = tmp_path / "d.nhdr"
    payload_path = tmp_path / "data" / "d.raw"
    payload_path.parent.mkdir()

    dump_detached(document, header_path, payload_path)
    reloaded = load(header_path)

    assert reloaded.array == [1, 2, 3, 4]
    header_text = header_path.read_bytes().decode("ascii")
    assert "data file: data/d.raw" in header_text


def test_detached_write_refuses_a_payload_outside_the_header_directory(
    tmp_path: Path,
) -> None:
    document = loads(_attached_source())
    header_dir = tmp_path / "header_dir"
    header_dir.mkdir()
    header_path = header_dir / "d.nhdr"
    escaping_payload = tmp_path / "escape.raw"

    with pytest.raises(NrrdWriteError, match="own directory"):
        dump_detached(document, header_path, escaping_payload)


def test_detached_write_preserves_the_document_header_fields(tmp_path: Path) -> None:
    document = loads(_attached_source())
    header_path = tmp_path / "d.nhdr"
    payload_path = tmp_path / "d.raw"

    dump_detached(document, header_path, payload_path)

    header_text = header_path.read_bytes().decode("ascii")
    assert "type: uint8" in header_text
    assert "dimension: 1" in header_text
    assert "encoding: raw" in header_text

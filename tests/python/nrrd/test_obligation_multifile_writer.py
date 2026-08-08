"""NRRD-MULTIFILE-001 -- writer support for multi-file detached (LIST form)
output.

MUST (SAL-NRRD-OBL-807586E5B4D0EDB2 / SAL-NRRD-OBL-EBE5230D5204B4AD):
"No multifile writer... Comprehensive sequence grammar edge cases and
writer support remain absent."

Before this slice, only dump_detached() existed (a single header + single
payload file). dump_multifile() closes the "no multifile writer" gap for
the LIST form specifically: the reader's own _safe_detached_payload
(codec/reader/reader.py) concatenates every listed file's raw bytes in
declared order with no per-file splitting logic of its own -- subdim is
parsed and range-validated but never used to determine byte distribution.
Writing the exact mirror of that (the full encoded payload split into N
equal consecutive chunks) is therefore both correct and the only
distribution the reader's own contract requires.

Scope, stated plainly: the printf numbered-sequence form is not covered
here -- LIST is the more general, caller-controls-every-filename form, and
a printf writer would need its own naming-pattern generation logic,
correctly left as a smaller, separate follow-up rather than folded in
silently.
"""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from format_factory.nrrd import dump_multifile, load, loads
from format_factory.nrrd.errors import NrrdWriteError


def _document(sizes: str = "2 2 2", payload: bytes = bytes(range(8))):
    header = f"NRRD0004\ntype: uint8\ndimension: 3\nsizes: {sizes}\nencoding: raw\n\n".encode()
    return loads(header + payload)


def test_a_multifile_write_round_trips_through_the_existing_reader(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"
    payload_paths = [tmp_path / "slice0.raw", tmp_path / "slice1.raw"]

    dump_multifile(document, header_path, payload_paths)
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_the_written_header_declares_a_list_form_with_relative_names(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"
    dump_multifile(document, header_path, [tmp_path / "a.raw", tmp_path / "b.raw"])

    text = header_path.read_text()

    assert "data file: LIST" in text
    assert "a.raw" in text
    assert "b.raw" in text


def test_payload_bytes_are_split_into_equal_consecutive_chunks_in_order(tmp_path: Path) -> None:
    document = _document(payload=bytes(range(8)))
    header_path = tmp_path / "volume.nhdr"
    paths = [tmp_path / "s0.raw", tmp_path / "s1.raw"]

    dump_multifile(document, header_path, paths)

    assert paths[0].read_bytes() == bytes(range(0, 4))
    assert paths[1].read_bytes() == bytes(range(4, 8))


def test_a_single_entry_list_is_a_valid_degenerate_case(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile(document, header_path, [tmp_path / "only.raw"])
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_a_compressed_payload_splits_and_reassembles_correctly(tmp_path: Path) -> None:
    payload = bytes(range(8))
    header = b"NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: gzip\n\n"
    document = loads(header + gzip.compress(payload))
    header_path = tmp_path / "volume.nhdr"

    dump_multifile(document, header_path, [tmp_path / "p0.raw", tmp_path / "p1.raw"])
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_an_uneven_split_is_refused_with_a_clear_reason(tmp_path: Path) -> None:
    document = _document(payload=bytes(range(8)))
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="does not split evenly"):
        dump_multifile(
            document, header_path, [tmp_path / "a.raw", tmp_path / "b.raw", tmp_path / "c.raw"]
        )


def test_a_payload_destination_outside_the_header_directory_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "sub" / "volume.nhdr"
    header_path.parent.mkdir()
    outside = tmp_path / "outside.raw"

    with pytest.raises(NrrdWriteError, match="own directory"):
        dump_multifile(document, header_path, [outside, tmp_path / "sub" / "b.raw"])


def test_an_older_profile_is_refused_because_list_needs_nrrd0004(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="NRRD0004 or newer"):
        dump_multifile(
            document, header_path, [tmp_path / "a.raw", tmp_path / "b.raw"], profile="NRRD0002"
        )


def test_at_least_one_payload_destination_is_required(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="at least one"):
        dump_multifile(document, header_path, [])

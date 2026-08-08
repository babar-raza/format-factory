"""NRRD-MULTIFILE-001 -- writer support for multi-file detached (printf
numbered-sequence form) output.

Sibling of test_obligation_multifile_writer.py's own dump_multifile()
(the LIST form). Named at FF6-EVENT-000303's own exact_next_action as the
smaller, separate follow-up its own missing_behavior deliberately did not
attempt: dump_multifile_printf() writes a `data file: <pattern> <start>
<stop> <step> [<subdim>]` declaration and generates filenames with the
exact same `pattern % item` expression the reader's own
_safe_detached_payload evaluates when reading a printf sequence back, so
a file this function writes is named exactly what the reader looks for.
"""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from format_factory.nrrd import dump_multifile_printf, load, loads
from format_factory.nrrd.errors import NrrdWriteError


def _document(payload: bytes = bytes(range(8))):
    header = b"NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: raw\n\n"
    return loads(header + payload)


def _data_file_line(header_path: Path) -> str:
    return next(line for line in header_path.read_text().splitlines() if line.startswith("data file"))


def test_a_printf_write_round_trips_through_the_existing_reader(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "slice%02d.raw", file_count=2)
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_generated_filenames_match_the_pattern_applied_to_each_index(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "slice%02d.raw", file_count=2)

    assert (tmp_path / "slice00.raw").exists()
    assert (tmp_path / "slice01.raw").exists()


def test_the_header_declares_pattern_start_stop_step(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "slice%02d.raw", file_count=2)

    assert _data_file_line(header_path) == "data file: slice%02d.raw 0 1 1"


def test_a_negative_step_generates_a_descending_sequence_and_round_trips(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "s%d.raw", start=5, step=-1, file_count=2)

    assert _data_file_line(header_path) == "data file: s%d.raw 5 4 -1"
    assert (tmp_path / "s5.raw").exists()
    assert (tmp_path / "s4.raw").exists()
    reloaded = load(header_path)
    assert reloaded.array == document.array


def test_an_explicit_subdim_is_appended_as_the_fifth_token(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "t%d.raw", file_count=2, subdim=2)

    assert _data_file_line(header_path) == "data file: t%d.raw 0 1 1 2"
    reloaded = load(header_path)
    assert reloaded.array == document.array


def test_payload_bytes_are_split_into_equal_consecutive_chunks_in_generated_order(
    tmp_path: Path,
) -> None:
    document = _document(payload=bytes(range(8)))
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "s%d.raw", file_count=2)

    assert (tmp_path / "s0.raw").read_bytes() == bytes(range(0, 4))
    assert (tmp_path / "s1.raw").read_bytes() == bytes(range(4, 8))


def test_a_compressed_payload_splits_and_reassembles_correctly(tmp_path: Path) -> None:
    payload = bytes(range(8))
    header = b"NRRD0004\ntype: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: gzip\n\n"
    document = loads(header + gzip.compress(payload))
    header_path = tmp_path / "volume.nhdr"

    dump_multifile_printf(document, header_path, "p%d.raw", file_count=2)
    reloaded = load(header_path)

    assert reloaded.array == document.array


def test_a_pattern_with_no_conversion_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="must contain exactly one"):
        dump_multifile_printf(document, header_path, "noformat.raw", file_count=2)


def test_a_pattern_with_a_path_separator_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="path separator"):
        dump_multifile_printf(document, header_path, "sub/s%d.raw", file_count=2)


def test_an_uneven_split_is_refused_with_a_clear_reason(tmp_path: Path) -> None:
    document = _document(payload=bytes(range(8)))
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="does not split evenly"):
        dump_multifile_printf(document, header_path, "s%d.raw", file_count=3)


def test_a_subdim_out_of_range_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="between 1 and 3"):
        dump_multifile_printf(document, header_path, "s%d.raw", file_count=2, subdim=99)


def test_an_older_profile_is_refused_because_printf_needs_nrrd0004(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="NRRD0004 or newer"):
        dump_multifile_printf(document, header_path, "s%d.raw", file_count=2, profile="NRRD0002")


def test_a_zero_step_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="step must not be zero"):
        dump_multifile_printf(document, header_path, "s%d.raw", step=0, file_count=2)


def test_a_file_count_below_one_is_refused(tmp_path: Path) -> None:
    document = _document()
    header_path = tmp_path / "volume.nhdr"

    with pytest.raises(NrrdWriteError, match="at least 1"):
        dump_multifile_printf(document, header_path, "s%d.raw", file_count=0)

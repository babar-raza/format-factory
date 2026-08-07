"""Installed-wheel tests for NRRD detached LIST and printf payload forms."""

from pathlib import Path

import pytest
from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.nrrd import load
from format_factory.nrrd.errors import NrrdParseError


def _header(data_file: str, *, magic: str = "NRRD0005") -> bytes:
    return (f"{magic}\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\ndata file: " + data_file + "\n\n").encode()


def test_list_and_printf_detached_payload_forms(tmp_path: Path) -> None:
    (tmp_path / "part-0.raw").write_bytes(b"\x01\x02")
    (tmp_path / "part-1.raw").write_bytes(b"\x03\x04")
    list_header = tmp_path / "list.nhdr"
    list_header.write_bytes(_header("LIST\npart-0.raw\npart-1.raw"))
    assert load(list_header).array == [1, 2, 3, 4]

    pattern_header = tmp_path / "pattern.nhdr"
    pattern_header.write_bytes(_header("part-%d.raw 0 1 1"))
    assert load(pattern_header).array == [1, 2, 3, 4]


def test_printf_sequence_file_count_is_bounded_before_allocation(tmp_path: Path) -> None:
    """A declared printf range's file count is checked against max_entries
    before any filename string is built or any file is opened -- a header
    claiming a billion-file sequence must fail fast, not attempt to allocate
    a billion-element list first. No backing files exist here on purpose:
    the rejection must happen before any of them would be needed."""
    pattern_header = tmp_path / "pathological.nhdr"
    pattern_header.write_bytes(_header("part-%d.raw 0 999999999 1"))

    with pytest.raises(ResourceLimitError, match="over the limit"):
        load(pattern_header, limits=ResourceLimits(max_entries=64))


def test_list_sequence_file_count_is_bounded_before_allocation(tmp_path: Path) -> None:
    """A declared LIST's file count is checked against max_entries before any
    file is opened, mirroring the printf sequence's own file-count bound --
    previously unenforced for LIST declarations specifically, confirmed
    genuinely exploitable by direct probing before this fix (200 declared
    names loaded successfully with max_entries=64 configured). No backing
    files exist here on purpose: the rejection must happen before any of
    them would be needed."""
    names = "\n".join(f"f{i}.raw" for i in range(10))
    list_header = tmp_path / "flood.nhdr"
    list_header.write_bytes(_header(f"LIST\n{names}"))

    with pytest.raises(ResourceLimitError, match="over the limit"):
        load(list_header, limits=ResourceLimits(max_entries=5))


def test_list_sequence_within_the_limit_still_loads(tmp_path: Path) -> None:
    (tmp_path / "part-0.raw").write_bytes(b"\x01\x02")
    (tmp_path / "part-1.raw").write_bytes(b"\x03\x04")
    list_header = tmp_path / "small-list.nhdr"
    list_header.write_bytes(_header("LIST\npart-0.raw\npart-1.raw"))

    assert load(list_header, limits=ResourceLimits(max_entries=5)).array == [1, 2, 3, 4]


def test_a_list_declaration_under_a_pre_nrrd0004_magic_is_rejected_at_read_time(tmp_path: Path) -> None:
    """"Starting with NRRD0004, the data file field can identify multiple
    payload files." A LIST declaration under an older magic was previously
    accepted silently at load() -- only a separate, caller-opted-in
    validate() call surfaced nrrd.version.insufficient. Confirmed genuinely
    unenforced at read time by direct probing before this fix."""
    (tmp_path / "part-0.raw").write_bytes(b"\x01\x02")
    (tmp_path / "part-1.raw").write_bytes(b"\x03\x04")
    list_header = tmp_path / "pre4-list.nhdr"
    list_header.write_bytes(_header("LIST\n./part-0.raw\n./part-1.raw", magic="NRRD0002"))

    with pytest.raises(NrrdParseError, match="NRRD0004 or newer"):
        load(list_header)


def test_a_printf_declaration_under_a_pre_nrrd0004_magic_is_rejected_at_read_time(tmp_path: Path) -> None:
    pattern_header = tmp_path / "pre4-printf.nhdr"
    pattern_header.write_bytes(_header("part-%d.raw 0 1 1", magic="NRRD0003"))

    with pytest.raises(NrrdParseError, match="NRRD0004 or newer"):
        load(pattern_header)


def test_a_list_declaration_at_exactly_nrrd0004_still_loads(tmp_path: Path) -> None:
    (tmp_path / "part-0.raw").write_bytes(b"\x01\x02")
    (tmp_path / "part-1.raw").write_bytes(b"\x03\x04")
    list_header = tmp_path / "at4-list.nhdr"
    list_header.write_bytes(_header("LIST\npart-0.raw\npart-1.raw", magic="NRRD0004"))

    assert load(list_header).array == [1, 2, 3, 4]


def test_a_single_detached_file_under_a_pre_nrrd0004_magic_is_unaffected(tmp_path: Path) -> None:
    """The NRRD0004 gate applies only to multi-file (LIST/printf)
    declarations -- a single detached file is valid in every profile and
    must not be caught by the same check."""
    (tmp_path / "single.raw").write_bytes(b"\x01\x02\x03\x04")
    single_header = tmp_path / "pre4-single.nhdr"
    single_header.write_bytes(_header("./single.raw", magic="NRRD0002"))

    assert load(single_header).array == [1, 2, 3, 4]

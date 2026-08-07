"""Installed-wheel tests for NRRD detached LIST and printf payload forms."""

from pathlib import Path

import pytest
from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.nrrd import load


def _header(data_file: str) -> bytes:
    return ("NRRD0005\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\ndata file: " + data_file + "\n\n").encode()


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

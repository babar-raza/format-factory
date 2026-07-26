"""Installed-wheel tests for NRRD detached LIST and printf payload forms."""

from pathlib import Path

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

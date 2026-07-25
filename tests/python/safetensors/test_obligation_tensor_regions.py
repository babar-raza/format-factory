from __future__ import annotations

import json
import mmap
import struct
from pathlib import Path

import pytest

from format_factory.safetensors import PayloadAccessMode, safe_open


def _write_two_tensor_file(path: Path) -> None:
    header = json.dumps(
        {
            "first": {
                "dtype": "U8",
                "shape": [4],
                "data_offsets": [0, 4],
            },
            "second": {
                "dtype": "U8",
                "shape": [6],
                "data_offsets": [4, 10],
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")
    path.write_bytes(struct.pack("<Q", len(header)) + header + b"abcdefghij")


def test_path_tensor_regions_are_read_only_mapped_views_without_copy(
    tmp_path: Path,
) -> None:
    path = tmp_path / "regions.safetensors"
    _write_two_tensor_file(path)

    with safe_open(path) as document:
        assert document.access.mode is PayloadAccessMode.MEMORY_MAPPED
        assert document.access.zero_copy
        assert document.access.region_reads
        assert not document.access.full_payload_read_required
        assert not document.access.full_decode_required

        first = document.tensor_region("first")
        selected = document.tensor_region("second", 1, 4)
        try:
            assert first.readonly
            assert selected.readonly
            assert isinstance(first.obj, mmap.mmap)
            assert selected.obj is first.obj
            assert bytes(first) == b"abcd"
            assert bytes(selected) == b"fgh"
        finally:
            selected.release()
            first.release()


@pytest.mark.parametrize(
    ("start", "stop"),
    [
        (-1, 0),
        (0, -1),
        (4, 3),
        (0, 7),
        (True, 1),
        (0, False),
        (0.0, 1),
        (0, 1.0),
    ],
)
def test_tensor_relative_region_bounds_fail_closed(
    tmp_path: Path,
    start: object,
    stop: object,
) -> None:
    path = tmp_path / "bounds.safetensors"
    _write_two_tensor_file(path)

    with safe_open(path) as document:
        with pytest.raises(
            ValueError,
            match=r"0 <= start <= stop <= 6",
        ):
            document.tensor_region("second", start, stop)  # type: ignore[arg-type]

from __future__ import annotations

import io
import json
import struct
import tracemalloc
from pathlib import Path
from typing import BinaryIO

import pytest
from format_factory.core import ResourceLimits
from format_factory.safetensors import (
    PayloadAccessMode,
    SafeTensorsParseError,
    load,
    read_header,
    safe_open,
)


class CountingReader:
    """Seekable binary wrapper that records actual bytes copied by read()."""

    def __init__(self, stream: BinaryIO) -> None:
        self.stream = stream
        self.bytes_read = 0

    def read(self, size: int = -1) -> bytes:
        chunk = self.stream.read(size)
        self.bytes_read += len(chunk)
        return chunk

    def tell(self) -> int:
        return self.stream.tell()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.stream.seek(offset, whence)


class NonSeekable(io.BytesIO):
    def seek(self, *_: object) -> int:
        raise OSError("not seekable")

    def tell(self) -> int:
        raise OSError("not seekable")


def _write_sparse_tensor(path: Path, payload_size: int) -> int:
    encoded = json.dumps(
        {
            "__metadata__": {"purpose": "bounded-memory-proof"},
            "large": {
                "dtype": "U8",
                "shape": [payload_size],
                "data_offsets": [0, payload_size],
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")
    with path.open("wb") as stream:
        stream.write(struct.pack("<Q", len(encoded)))
        stream.write(encoded)
        stream.seek(payload_size - 1, 1)
        stream.write(b"\0")
    return len(encoded)


def test_header_only_and_mapped_region_access_stay_bounded(tmp_path: Path) -> None:
    payload_size = 64 * 1024 * 1024
    path = tmp_path / "large.safetensors"
    header_size = _write_sparse_tensor(path, payload_size)
    limits = ResourceLimits(max_input_bytes=128 * 1024 * 1024)

    with path.open("rb") as raw_stream:
        stream = CountingReader(raw_stream)
        header = read_header(stream, limits=limits)
    assert stream.bytes_read == 8 + header_size
    assert header.payload_size == payload_size
    assert header.tensor_names == ("large",)
    assert header.access.mode is PayloadAccessMode.HEADER_ONLY
    assert not header.access.full_payload_read_required
    assert not header.access.full_decode_required

    tracemalloc.start()
    with safe_open(path, limits=limits) as document:
        assert document.access.mode is PayloadAccessMode.MEMORY_MAPPED
        assert document.access.zero_copy
        assert document.access.region_reads
        assert not document.access.full_payload_read_required
        assert not document.access.full_decode_required
        tail = document.tensor_region("large", payload_size - 16, payload_size)
        assert tail.readonly
        assert bytes(tail) == bytes(16)
        tail.release()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 4 * 1024 * 1024


def test_stream_buffering_is_disclosed_and_header_only_requires_seek() -> None:
    encoded = b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}'
    raw = struct.pack("<Q", len(encoded)) + encoded + b"\0"

    with load(io.BytesIO(raw)) as document:
        assert document.access.mode is PayloadAccessMode.BUFFERED_STREAM
        assert document.access.full_payload_read_required
        assert not document.access.full_decode_required

    with pytest.raises(SafeTensorsParseError, match="seekable"):
        read_header(NonSeekable(raw))

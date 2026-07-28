from __future__ import annotations

import struct

import pytest

from format_factory.safetensors import (
    SafeTensorsDocument,
    SafeTensorsParseError,
    dumps,
    loads,
)


def test_exact_eight_byte_little_endian_prefix_is_accepted() -> None:
    encoded = struct.pack("<Q", 2) + b"{}"
    with loads(encoded) as document:
        assert document.tensor_names == ()
        assert document.header_size == 2


def test_big_endian_prefix_is_not_misinterpreted_as_little_endian() -> None:
    encoded = struct.pack(">Q", 2) + b"{}"
    with pytest.raises(SafeTensorsParseError, match="header length.*exceeds"):
        loads(encoded)


def test_prefix_shorter_than_eight_bytes_is_rejected() -> None:
    with pytest.raises(SafeTensorsParseError, match="shorter than the 8-byte"):
        loads(b"\x02\0\0\0")


def test_writer_prefix_equals_exact_padded_json_header_extent() -> None:
    with SafeTensorsDocument(tensors={}) as document:
        encoded = dumps(document)

    header_size = struct.unpack("<Q", encoded[:8])[0]
    assert len(encoded[:8]) == 8
    assert header_size == len(encoded) - 8
    assert encoded[8:].rstrip() == b"{}"

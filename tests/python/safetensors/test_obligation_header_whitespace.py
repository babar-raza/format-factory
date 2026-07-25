from __future__ import annotations

import struct

import pytest

from format_factory.safetensors import dumps, loads

_HEADER = b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}'


@pytest.mark.parametrize(
    "header",
    [
        b"   " + _HEADER,
        _HEADER + b"   ",
        b"\r\n\t" + _HEADER + b" \n",
    ],
    ids=["leading", "trailing", "both"],
)
def test_whitespace_padded_header_roundtrips_semantically(header: bytes) -> None:
    encoded = struct.pack("<Q", len(header)) + header + b"\x07"

    with loads(encoded) as document:
        assert bytes(document.tensor_bytes("x")) == b"\x07"
        rebuilt = dumps(document)

    rebuilt_header_size = struct.unpack("<Q", rebuilt[:8])[0]
    assert rebuilt_header_size % 8 == 0
    with loads(rebuilt) as reloaded:
        assert reloaded.tensors["x"].shape == (1,)
        assert bytes(reloaded.tensor_bytes("x")) == b"\x07"

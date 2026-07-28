from __future__ import annotations

import json
import struct
from io import BytesIO
from pathlib import Path

import pytest

from format_factory.safetensors import (
    SafeTensorsParseError,
    dump,
    dumps,
    load,
    loads,
    probe,
    validate,
)


def _file(header: dict[str, object], payload: bytes = b"") -> bytes:
    encoded = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded + payload


def _sample() -> bytes:
    return _file(
        {
            "value": {
                "dtype": "U8",
                "shape": [3],
                "data_offsets": [0, 3],
            }
        },
        b"\x01\x02\x03",
    )


def test_path_stream_and_bytes_lifecycle(tmp_path: Path) -> None:
    raw = _sample()
    assert probe(raw)
    assert validate(raw)

    destination = tmp_path / "lifecycle.safetensors"
    stream = BytesIO()
    with loads(raw) as from_bytes:
        assert bytes(from_bytes.tensor_bytes("value")) == b"\x01\x02\x03"
        serialized = dumps(from_bytes)
        dump(from_bytes, destination)
        dump(from_bytes, stream)

    with load(destination) as from_path:
        assert bytes(from_path.tensor_bytes("value")) == b"\x01\x02\x03"
    with load(BytesIO(stream.getvalue())) as from_stream:
        assert bytes(from_stream.tensor_bytes("value")) == b"\x01\x02\x03"
    with loads(serialized) as reloaded:
        assert bytes(reloaded.tensor_bytes("value")) == b"\x01\x02\x03"


def test_strict_preservation_and_excluded_recovery_modes() -> None:
    duplicate = (
        b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},'
        b'"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}'
    )
    invalid = struct.pack("<Q", len(duplicate)) + duplicate + b"\x00"
    with pytest.raises(SafeTensorsParseError, match="duplicate"):
        loads(invalid, mode="strict")

    preserved = _file(
        {
            "x": {
                "dtype": "U8",
                "shape": [1],
                "data_offsets": [0, 1],
                "vendor": {"revision": 2},
            }
        },
        b"\x07",
    )
    with loads(preserved, mode="preservation") as document:
        rebuilt = dumps(document)
    with loads(rebuilt, mode="preservation") as reloaded:
        assert reloaded.tensors["x"].unknown_fields == {
            "vendor": {"revision": 2}
        }

    with pytest.raises(ValueError, match="strict.*preservation"):
        loads(preserved, mode="recovery")

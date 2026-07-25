from __future__ import annotations

import struct

import pytest

from format_factory.safetensors import SafeTensorsParseError, loads


@pytest.mark.parametrize(
    ("encoded", "message"),
    [
        (struct.pack("<Q", 1), "declared header extends beyond the input"),
        (struct.pack("<Q", 1) + b"\xff", "invalid UTF-8 JSON header"),
        (struct.pack("<Q", 1) + b"{", "invalid UTF-8 JSON header"),
    ],
    ids=["declared-extent", "malformed-utf8", "malformed-json"],
)
def test_declared_extent_utf8_and_json_fail_closed(
    encoded: bytes,
    message: str,
) -> None:
    with pytest.raises(SafeTensorsParseError, match=message):
        loads(encoded)

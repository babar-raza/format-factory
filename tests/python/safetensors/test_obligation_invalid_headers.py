from __future__ import annotations

import json
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


@pytest.mark.parametrize(
    "root",
    [[1, 2, 3], "not an object", 42, None],
    ids=["array", "string", "number", "null"],
)
def test_non_object_header_root_is_rejected(root: object) -> None:
    """"its top-level object maps tensor-name keys to tensor entries" -- valid
    UTF-8 JSON that decodes to anything other than an object is not a header,
    regardless of how well-formed the JSON itself is."""
    encoded = json.dumps(root).encode("utf-8")
    with pytest.raises(SafeTensorsParseError, match="header must be a JSON object"):
        loads(struct.pack("<Q", len(encoded)) + encoded)

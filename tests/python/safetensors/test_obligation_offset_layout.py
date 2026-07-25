from __future__ import annotations

import json
import struct

import pytest

from format_factory.safetensors import SafeTensorsParseError, loads


def _file(header: dict[str, object], payload: bytes) -> bytes:
    encoded = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded + payload


def test_contiguous_non_overlapping_offsets_are_accepted() -> None:
    raw = _file(
        {
            "first": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
            "second": {"dtype": "U8", "shape": [2], "data_offsets": [2, 4]},
        },
        b"\x01\x02\x03\x04",
    )
    with loads(raw) as document:
        assert bytes(document.tensor_bytes("first")) == b"\x01\x02"
        assert bytes(document.tensor_bytes("second")) == b"\x03\x04"


@pytest.mark.parametrize(
    ("second_offsets", "payload", "message"),
    [
        ((3, 5), b"\x01\x02\x00\x03\x04", "leaves a hole"),
        ((1, 3), b"\x01\x02\x03", "overlaps"),
    ],
)
def test_gap_and_overlap_are_rejected(
    second_offsets: tuple[int, int],
    payload: bytes,
    message: str,
) -> None:
    raw = _file(
        {
            "first": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
            "second": {
                "dtype": "U8",
                "shape": [2],
                "data_offsets": list(second_offsets),
            },
        },
        payload,
    )
    with pytest.raises(SafeTensorsParseError, match=message):
        loads(raw)


def test_unindexed_trailing_bytes_are_rejected() -> None:
    raw = _file(
        {"only": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]}},
        b"\x01\x02trailing",
    )
    with pytest.raises(SafeTensorsParseError, match=r"offsets cover 2 of 10"):
        loads(raw)

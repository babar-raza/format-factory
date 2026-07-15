"""SafeTensors header safety validation.

Single responsibility: reject malformed or unsafe SafeTensors headers before
`load_safetensors` hands back a model — overlapping `data_offsets` ranges,
out-of-bounds ranges, and gaps in data-buffer coverage (FACT-SAFETENSORS-104),
plus duplicate tensor-name keys in the header JSON (FACT-SAFETENSORS-105).

Spec reference: SafeTensors' safety design intent (vs. pickle) is that a
reader can trust the header's byte layout without executing any code — that
guarantee only holds if malformed offsets and duplicate keys are rejected
rather than silently accepted.
"""

from __future__ import annotations

from typing import Any

from safetensors.exceptions import SafetensorsParseError


def detect_duplicate_tensor_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """`json.loads(..., object_pairs_hook=...)` hook that rejects duplicate keys.

    Standard `json.loads` silently collapses duplicate JSON object keys into
    the last-seen value. This hook receives every JSON object's raw (key,
    value) pairs *before* that collapse happens, so it can raise on the first
    duplicate tensor-name key found anywhere in the header (FACT-SAFETENSORS-105).
    """
    seen: set[str] = set()
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise SafetensorsParseError(f"Duplicate tensor key in header JSON: {key!r}")
        seen.add(key)
        result[key] = value
    return result


def _validate_offset_pair(offsets: list[int], data_len: int, name: str) -> tuple[int, int]:
    """Validate one tensor's `data_offsets` pair against the data buffer length."""
    if not isinstance(offsets, (list, tuple)) or len(offsets) != 2:
        raise SafetensorsParseError(f"Tensor {name!r} has malformed data_offsets: {offsets!r}")
    start, end = offsets
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        raise SafetensorsParseError(f"Tensor {name!r} data_offsets must be integers: {offsets!r}")
    if start < 0 or end < start:
        raise SafetensorsParseError(f"Tensor {name!r} has an invalid data_offsets range: {offsets!r}")
    if end > data_len:
        raise SafetensorsParseError(
            f"Tensor {name!r} data_offsets end {end} exceeds data buffer length {data_len}"
        )
    return start, end


def slice_tensor_bytes(data: bytes, offsets: list[int], name: str) -> bytes:
    """Return `data[start:end]` for a tensor, raising if offsets are unsafe."""
    start, end = _validate_offset_pair(offsets, len(data), name)
    return data[start:end]


def validate_tensor_offsets(tensors: dict[str, Any], data_len: int) -> None:
    """Validate FACT-SAFETENSORS-104: no overlaps, no out-of-bounds, no holes.

    SafeTensors' safety guarantee depends on `data_offsets` exactly and safely
    describing the data buffer: ranges must not overlap, must not extend past
    the buffer, and together must cover the buffer with no gaps ("cannot
    contain holes").
    """
    if not tensors:
        if data_len != 0:
            raise SafetensorsParseError(
                f"Header declares no tensors but the data buffer has "
                f"{data_len} byte(s) of unexplained data"
            )
        return

    spans: list[tuple[int, int, str]] = []
    for name, info in tensors.items():
        offsets = info.get("data_offsets", [0, 0])
        start, end = _validate_offset_pair(offsets, data_len, name)
        spans.append((start, end, name))

    spans.sort(key=lambda span: span[0])

    prev_end = 0
    for start, end, name in spans:
        if start < prev_end:
            raise SafetensorsParseError(
                f"Tensor {name!r} data_offsets [{start}, {end}] overlaps the "
                f"preceding tensor's range (ends at {prev_end})"
            )
        if start > prev_end:
            raise SafetensorsParseError(
                f"Gap of {start - prev_end} byte(s) in the data buffer before "
                f"tensor {name!r} — data_offsets must cover the buffer with no holes"
            )
        prev_end = end

    if prev_end != data_len:
        raise SafetensorsParseError(
            f"data_offsets cover {prev_end} of {data_len} data buffer byte(s) "
            f"(trailing {data_len - prev_end} byte(s) unexplained)"
        )

"""Bounded SafeTensors v0.8.0 reader."""

from __future__ import annotations

import json
import mmap
import struct
from os import PathLike
from pathlib import Path
from typing import Any

from format_factory.core import BinarySource, ProbeResult, ResourceLimits

from ...errors import SafeTensorsParseError
from ...model import DType, SafeTensorsDocument, TensorDescriptor
from ...security import effective_limits

_PREFIX_SIZE = 8
_UPSTREAM_MAX_HEADER = 100_000_000


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise SafeTensorsParseError(f"duplicate JSON key: {key!r}")
        output[key] = value
    return output


def _parse(buffer: memoryview, limits: ResourceLimits, *, owner: Any = None) -> SafeTensorsDocument:
    limits.enforce("max_input_bytes", len(buffer))
    if len(buffer) < _PREFIX_SIZE:
        raise SafeTensorsParseError("input is shorter than the 8-byte header prefix")
    header_size = struct.unpack_from("<Q", buffer, 0)[0]
    header_limit = min(limits.max_header_bytes, _UPSTREAM_MAX_HEADER)
    if header_size > header_limit:
        raise SafeTensorsParseError(
            f"header length {header_size} exceeds configured limit {header_limit}"
        )
    header_end = _PREFIX_SIZE + header_size
    if header_end > len(buffer):
        raise SafeTensorsParseError("declared header extends beyond the input")
    try:
        header = json.loads(
            bytes(buffer[_PREFIX_SIZE:header_end]).decode("utf-8"),
            object_pairs_hook=_object_no_duplicates,
        )
    except SafeTensorsParseError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SafeTensorsParseError(f"invalid UTF-8 JSON header: {exc}") from exc
    if not isinstance(header, dict):
        raise SafeTensorsParseError("header must be a JSON object")

    raw_metadata = header.pop("__metadata__", {})
    if not isinstance(raw_metadata, dict) or any(
        not isinstance(k, str) or not isinstance(v, str)
        for k, v in raw_metadata.items()
    ):
        raise SafeTensorsParseError("__metadata__ must be a string-to-string object")

    limits.enforce("max_tensor_count", len(header))
    payload = buffer[header_end:]
    descriptors: dict[str, TensorDescriptor] = {}
    spans: list[TensorDescriptor] = []
    for name, raw in header.items():
        if not isinstance(name, str) or not name:
            raise SafeTensorsParseError("tensor names must be non-empty strings")
        if not isinstance(raw, dict):
            raise SafeTensorsParseError(f"tensor {name!r} descriptor must be an object")
        missing = {"dtype", "shape", "data_offsets"}.difference(raw)
        if missing:
            raise SafeTensorsParseError(
                f"tensor {name!r} is missing {', '.join(sorted(missing))}"
            )
        try:
            dtype = DType(raw["dtype"])
        except (TypeError, ValueError) as exc:
            raise SafeTensorsParseError(
                f"tensor {name!r} has unsupported dtype {raw.get('dtype')!r}"
            ) from exc
        shape_raw = raw["shape"]
        offsets_raw = raw["data_offsets"]
        if not isinstance(shape_raw, list):
            raise SafeTensorsParseError(f"tensor {name!r} shape must be a list")
        if not isinstance(offsets_raw, list) or len(offsets_raw) != 2:
            raise SafeTensorsParseError(f"tensor {name!r} data_offsets must have two items")
        try:
            descriptor = TensorDescriptor(
                name=name,
                dtype=dtype,
                shape=tuple(shape_raw),
                data_offsets=(offsets_raw[0], offsets_raw[1]),
                unknown_fields={
                    key: value
                    for key, value in raw.items()
                    if key not in {"dtype", "shape", "data_offsets"}
                },
            )
            expected_size = descriptor.byte_length
        except (TypeError, ValueError) as exc:
            raise SafeTensorsParseError(f"invalid tensor {name!r}: {exc}") from exc
        start, end = descriptor.data_offsets
        if end > len(payload):
            raise SafeTensorsParseError(f"tensor {name!r} extends beyond the payload")
        if end - start != expected_size:
            raise SafeTensorsParseError(
                f"tensor {name!r} spans {end - start} bytes, expected {expected_size}"
            )
        descriptors[name] = descriptor
        spans.append(descriptor)

    expected_start = 0
    for descriptor in sorted(spans, key=lambda item: item.data_offsets):
        start, end = descriptor.data_offsets
        if start != expected_start:
            relation = "overlaps" if start < expected_start else "leaves a hole before"
            raise SafeTensorsParseError(
                f"tensor {descriptor.name!r} {relation} offset {expected_start}"
            )
        expected_start = end
    if expected_start != len(payload):
        raise SafeTensorsParseError(
            f"tensor offsets cover {expected_start} of {len(payload)} payload bytes"
        )
    return SafeTensorsDocument(
        tensors=descriptors,
        metadata=raw_metadata,
        payload=payload,
        header_size=header_size,
        owner=owner,
    )


def loads(
    data: bytes | bytearray | memoryview,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> SafeTensorsDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    return _parse(memoryview(data), effective_limits(limits))


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> SafeTensorsDocument:
    if isinstance(source, (bytes, bytearray, memoryview)):
        return loads(source, mode=mode, limits=limits)
    if isinstance(source, (str, PathLike)):
        path = Path(source)
        selected = effective_limits(limits)
        selected.enforce("max_input_bytes", path.stat().st_size)
        file = path.open("rb")
        try:
            mapped = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception:
            file.close()
            raise
        file.close()
        try:
            return _parse(memoryview(mapped), selected, owner=mapped)
        except Exception:
            mapped.close()
            raise
    raw = source.read()
    if not isinstance(raw, bytes):
        raise TypeError("binary source read() must return bytes")
    return loads(raw, mode=mode, limits=limits)


def safe_open(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> SafeTensorsDocument:
    return load(source, mode=mode, limits=limits)


def probe(source: BinarySource, *, limits: ResourceLimits | None = None) -> ProbeResult:
    try:
        document = load(source, limits=limits)
    except Exception as exc:
        return ProbeResult(False, 0.0, "safetensors", reason=str(exc))
    with document:
        confidence = 1.0 if document.tensors else 0.85
        return ProbeResult(True, confidence, "safetensors", profile=document.profile)

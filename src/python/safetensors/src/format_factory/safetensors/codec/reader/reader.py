"""Bounded SafeTensors v0.8.0 reader."""

from __future__ import annotations

import json
import mmap
import struct
from os import PathLike
from pathlib import Path
from typing import Any, BinaryIO, Callable

from format_factory.core import BinarySource, ProbeResult, ResourceLimits

from ...errors import SafeTensorsParseError
from ...model import (
    DType,
    PayloadAccess,
    PayloadAccessMode,
    SafeTensorsDocument,
    SafeTensorsHeader,
    TensorDescriptor,
)
from ...security import effective_limits

_PREFIX_SIZE = 8
_UPSTREAM_MAX_HEADER = 100_000_000


def _error(code: str, message: str) -> SafeTensorsParseError:
    return SafeTensorsParseError(message, code=code)


def _descriptor_error_code(exc: Exception) -> str:
    message = str(exc)
    if "overflow" in message or "exceeds unsigned 64-bit" in message:
        return "SAFETENSORS_SIZE_OVERFLOW"
    if "shape dimension" in message:
        return "SAFETENSORS_SHAPE"
    if "data offsets" in message:
        return "SAFETENSORS_OFFSETS"
    if "sub-byte" in message:
        return "SAFETENSORS_SUBBYTE_ALIGNMENT"
    return "SAFETENSORS_DESCRIPTOR"


def _bounded_object_no_duplicates(
    limits: ResourceLimits,
) -> Callable[[list[tuple[str, Any]]], dict[str, Any]]:
    """Build a `json.loads(..., object_pairs_hook=...)` callback that checks
    `max_entries` DURING header parsing, not only after.

    `max_entries` was previously configured (security/limits.py) but never
    referenced anywhere in this package -- confirmed genuinely unenforced by
    direct probing before this fix: a 300,000-descriptor header (19.7MB)
    fully parsed into a live Python dict in ~0.66s before any entries limit
    could reject it. `object_pairs_hook` fires once per JSON object as it
    completes (innermost first, so nested tensor descriptors complete before
    the enclosing header object) -- a closure over a single running total
    accumulates the pair count across every object in the header (the
    top-level name-to-descriptor mapping, each descriptor, and __metadata__
    alike), checked immediately after each update, matching this session's
    established "check before the expensive operation completes, not after"
    discipline. Preserves the pre-existing duplicate-key rejection this hook
    already performed -- extending it, not replacing its behavior.
    """

    state = {"entries": 0}

    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        state["entries"] += len(pairs)
        limits.enforce("max_entries", state["entries"])
        output: dict[str, Any] = {}
        for key, value in pairs:
            if key in output:
                raise _error("SAFETENSORS_DUPLICATE_KEY", f"duplicate JSON key: {key!r}")
            output[key] = value
        return output

    return hook


def _decode_header(
    encoded: bytes,
    *,
    payload_size: int,
    limits: ResourceLimits,
) -> tuple[dict[str, TensorDescriptor], dict[str, str] | None]:
    """Validate a JSON header against the known payload extent.

    The returned metadata is `None` when `__metadata__` was absent from the
    header entirely, and a (possibly empty) dict when it was present --
    SAFETENSORS-PRESERVE-001 requires distinguishing "no __metadata__ key"
    from "__metadata__: {}", which collapsing both to `{}` here would lose
    before it ever reaches the model.
    """

    try:
        header = json.loads(
            encoded.decode("utf-8"),
            object_pairs_hook=_bounded_object_no_duplicates(limits),
        )
    except SafeTensorsParseError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _error(
            "SAFETENSORS_HEADER_ENCODING",
            f"invalid UTF-8 JSON header: {exc}",
        ) from exc
    if not isinstance(header, dict):
        raise _error("SAFETENSORS_HEADER_ROOT", "header must be a JSON object")

    raw_metadata = header.pop("__metadata__", None)
    if raw_metadata is not None and (
        not isinstance(raw_metadata, dict)
        or any(
            not isinstance(k, str) or not isinstance(v, str)
            for k, v in raw_metadata.items()
        )
    ):
        raise _error(
            "SAFETENSORS_METADATA_TYPE",
            "__metadata__ must be a string-to-string object",
        )

    limits.enforce("max_tensor_count", len(header))
    descriptors: dict[str, TensorDescriptor] = {}
    spans: list[TensorDescriptor] = []
    for name, raw in header.items():
        if not isinstance(name, str) or not name:
            raise _error(
                "SAFETENSORS_TENSOR_NAME",
                "tensor names must be non-empty strings",
            )
        if not isinstance(raw, dict):
            raise _error(
                "SAFETENSORS_DESCRIPTOR",
                f"tensor {name!r} descriptor must be an object",
            )
        missing = {"dtype", "shape", "data_offsets"}.difference(raw)
        if missing:
            raise _error(
                "SAFETENSORS_DESCRIPTOR_FIELDS",
                f"tensor {name!r} is missing {', '.join(sorted(missing))}",
            )
        try:
            dtype = DType(raw["dtype"])
        except (TypeError, ValueError) as exc:
            raise _error(
                "SAFETENSORS_DTYPE",
                f"tensor {name!r} has unsupported dtype {raw.get('dtype')!r}",
            ) from exc
        shape_raw = raw["shape"]
        offsets_raw = raw["data_offsets"]
        if not isinstance(shape_raw, list):
            raise _error(
                "SAFETENSORS_SHAPE",
                f"tensor {name!r} shape must be a list",
            )
        limits.enforce("max_nesting_depth", len(shape_raw))
        if not isinstance(offsets_raw, list) or len(offsets_raw) != 2:
            raise _error(
                "SAFETENSORS_OFFSETS",
                f"tensor {name!r} data_offsets must have two items",
            )
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
            raise _error(
                _descriptor_error_code(exc),
                f"invalid tensor {name!r}: {exc}",
            ) from exc
        start, end = descriptor.data_offsets
        if end > payload_size:
            raise _error(
                "SAFETENSORS_TENSOR_BOUNDS",
                f"tensor {name!r} extends beyond the payload",
            )
        if end - start != expected_size:
            raise _error(
                "SAFETENSORS_TENSOR_SIZE",
                f"tensor {name!r} spans {end - start} bytes, expected {expected_size}",
            )
        descriptors[name] = descriptor
        spans.append(descriptor)

    expected_start = 0
    for descriptor in sorted(spans, key=lambda item: item.data_offsets):
        start, end = descriptor.data_offsets
        if start != expected_start:
            relation = "overlaps" if start < expected_start else "leaves a hole before"
            raise _error(
                "SAFETENSORS_OFFSET_COVERAGE",
                f"tensor {descriptor.name!r} {relation} offset {expected_start}",
            )
        expected_start = end
    if expected_start != payload_size:
        raise _error(
            "SAFETENSORS_TRAILING_DATA",
            f"tensor offsets cover {expected_start} of {payload_size} payload bytes",
        )
    return descriptors, raw_metadata


def _header_extent(
    prefix: bytes | memoryview,
    *,
    total_size: int,
    limits: ResourceLimits,
) -> tuple[int, int]:
    if len(prefix) < _PREFIX_SIZE:
        raise _error(
            "SAFETENSORS_PREFIX_TRUNCATED",
            "input is shorter than the 8-byte header prefix",
        )
    header_size = struct.unpack_from("<Q", prefix, 0)[0]
    header_limit = min(limits.max_header_bytes, _UPSTREAM_MAX_HEADER)
    if header_size > header_limit:
        raise _error(
            "SAFETENSORS_HEADER_LIMIT",
            f"header length {header_size} exceeds configured limit {header_limit}",
        )
    header_end = _PREFIX_SIZE + header_size
    if header_end > total_size:
        raise _error(
            "SAFETENSORS_HEADER_TRUNCATED",
            "declared header extends beyond the input",
        )
    return header_size, header_end


def _parse(
    buffer: memoryview,
    limits: ResourceLimits,
    *,
    owner: Any = None,
    access: PayloadAccess | None = None,
) -> SafeTensorsDocument:
    limits.enforce("max_input_bytes", len(buffer))
    header_size, header_end = _header_extent(
        buffer[:_PREFIX_SIZE],
        total_size=len(buffer),
        limits=limits,
    )
    payload = buffer[header_end:]
    descriptors, metadata = _decode_header(
        bytes(buffer[_PREFIX_SIZE:header_end]),
        payload_size=len(payload),
        limits=limits,
    )
    return SafeTensorsDocument(
        tensors=descriptors,
        metadata=metadata,
        metadata_declared=metadata is not None,
        payload=payload,
        header_size=header_size,
        owner=owner,
        access=access,
    )


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = stream.read(remaining)
        if not isinstance(chunk, bytes):
            raise TypeError("binary source read() must return bytes")
        if not chunk:
            raise _error(
                "SAFETENSORS_HEADER_TRUNCATED",
                f"input ended with {remaining} required header bytes missing",
            )
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _stream_size(stream: BinaryIO) -> tuple[int, int]:
    """Return (current position, bytes available) without consuming the stream."""

    try:
        start = stream.tell()
        stream.seek(0, 2)
        end = stream.tell()
        stream.seek(start)
    except (AttributeError, OSError) as exc:
        raise _error(
            "SAFETENSORS_STREAM_NOT_SEEKABLE",
            "header-only inspection requires a seekable binary stream",
        ) from exc
    if end < start:
        raise _error(
            "SAFETENSORS_STREAM_EXTENT",
            "binary stream reports an invalid extent",
        )
    return start, end - start


def _read_header_stream(
    stream: BinaryIO,
    *,
    total_size: int,
    limits: ResourceLimits,
) -> SafeTensorsHeader:
    limits.enforce("max_input_bytes", total_size)
    prefix = _read_exact(stream, _PREFIX_SIZE)
    header_size, header_end = _header_extent(
        prefix,
        total_size=total_size,
        limits=limits,
    )
    encoded = _read_exact(stream, header_size)
    payload_size = total_size - header_end
    descriptors, metadata = _decode_header(
        encoded,
        payload_size=payload_size,
        limits=limits,
    )
    return SafeTensorsHeader(
        tensors=descriptors,
        metadata=metadata or {},
        metadata_declared=metadata is not None,
        payload_size=payload_size,
        header_size=header_size,
    )


def read_header(
    source: BinarySource,
    *,
    limits: ResourceLimits | None = None,
) -> SafeTensorsHeader:
    """Read and validate only the prefix and JSON header.

    Payload bytes are never copied or mapped. A stream must be seekable so its
    payload extent can be validated without consuming it.
    """

    selected = effective_limits(limits)
    if isinstance(source, (bytes, bytearray, memoryview)):
        buffer = memoryview(source)
        selected.enforce("max_input_bytes", len(buffer))
        header_size, header_end = _header_extent(
            buffer[:_PREFIX_SIZE],
            total_size=len(buffer),
            limits=selected,
        )
        descriptors, metadata = _decode_header(
            bytes(buffer[_PREFIX_SIZE:header_end]),
            payload_size=len(buffer) - header_end,
            limits=selected,
        )
        return SafeTensorsHeader(
            tensors=descriptors,
            metadata=metadata or {},
            metadata_declared=metadata is not None,
            payload_size=len(buffer) - header_end,
            header_size=header_size,
        )
    if isinstance(source, (str, PathLike)):
        path = Path(source)
        total_size = path.stat().st_size
        with path.open("rb") as stream:
            return _read_header_stream(
                stream,
                total_size=total_size,
                limits=selected,
            )
    _, total_size = _stream_size(source)
    return _read_header_stream(source, total_size=total_size, limits=selected)


def loads(
    data: bytes | bytearray | memoryview,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> SafeTensorsDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    return _parse(
        memoryview(data),
        effective_limits(limits),
        access=PayloadAccess(
            mode=PayloadAccessMode.BORROWED_BUFFER,
            zero_copy=True,
            region_reads=True,
            full_payload_read_required=False,
            full_decode_required=False,
            detail="tensor regions are borrowed from the caller-provided buffer",
        ),
    )


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> SafeTensorsDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
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
            return _parse(
                memoryview(mapped),
                selected,
                owner=mapped,
                access=PayloadAccess(
                    mode=PayloadAccessMode.MEMORY_MAPPED,
                    zero_copy=True,
                    region_reads=True,
                    full_payload_read_required=False,
                    full_decode_required=False,
                    detail=(
                        "the raw SafeTensors payload is memory mapped; the format "
                        "defines no compressed payload encoding"
                    ),
                ),
            )
        except Exception:
            mapped.close()
            raise
    raw = source.read()
    if not isinstance(raw, bytes):
        raise TypeError("binary source read() must return bytes")
    return _parse(
        memoryview(raw),
        effective_limits(limits),
        access=PayloadAccess(
            mode=PayloadAccessMode.BUFFERED_STREAM,
            zero_copy=True,
            region_reads=True,
            full_payload_read_required=True,
            full_decode_required=False,
            detail=(
                "the non-path stream was fully buffered; SafeTensors defines no "
                "compressed payload encoding"
            ),
        ),
    )


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

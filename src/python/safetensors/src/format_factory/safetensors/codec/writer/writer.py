"""Deterministic SafeTensors writer."""

from __future__ import annotations

import json
import struct
from os import PathLike
from pathlib import Path

from format_factory.core import BinaryDestination

from ...errors import SafeTensorsWriteError
from ...model import SafeTensorsDocument
from ...validation.validator import validate


def dumps(
    document: SafeTensorsDocument,
    *,
    profile: str | None = None,
) -> bytes:
    if profile not in {None, "v0.8.0"}:
        raise ValueError("only the v0.8.0 profile is supported")
    report = validate(document)
    if not report:
        raise SafeTensorsWriteError(report.errors[0].message)

    header: dict[str, object] = {}
    if document.metadata_declared:
        header["__metadata__"] = dict(sorted(document.metadata.items()))
    offset = 0
    payload_parts: list[bytes] = []
    ordered = sorted(
        document.tensors.values(),
        key=lambda item: (-item.dtype.bits, item.name),
    )
    for descriptor in ordered:
        data = bytes(document.tensor_bytes(descriptor.name))
        end = offset + len(data)
        entry: dict[str, object] = {
            "dtype": descriptor.dtype.value,
            "shape": list(descriptor.shape),
            "data_offsets": [offset, end],
        }
        for key in sorted(descriptor.unknown_fields):
            if key not in entry:
                entry[key] = descriptor.unknown_fields[key]
        header[descriptor.name] = entry
        payload_parts.append(data)
        offset = end
    try:
        encoded = json.dumps(
            header,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SafeTensorsWriteError(f"header is not JSON serializable: {exc}") from exc
    padding = (-len(encoded)) % 8
    encoded += b" " * padding
    return struct.pack("<Q", len(encoded)) + encoded + b"".join(payload_parts)


def dump(
    document: SafeTensorsDocument,
    destination: BinaryDestination,
    *,
    profile: str | None = None,
) -> None:
    data = dumps(document, profile=profile)
    if isinstance(destination, (str, PathLike)):
        Path(destination).write_bytes(data)
        return
    written = destination.write(data)
    if written is not None and written != len(data):
        raise SafeTensorsWriteError(f"short write: {written} of {len(data)} bytes")

"""Deterministic SafeTensors sharded-index JSON codec."""

from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import Any, BinaryIO, TextIO

from ..errors import SafeTensorsParseError, SafeTensorsWriteError
from ..model.sharded import SafeTensorsShardIndex


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise SafeTensorsParseError(f"duplicate JSON key: {key!r}")
        output[key] = value
    return output


def loads_index(data: str | bytes | bytearray | memoryview) -> SafeTensorsShardIndex:
    """Parse a sharded-index JSON document from text or UTF-8 bytes."""

    try:
        text = data if isinstance(data, str) else bytes(data).decode("utf-8")
        raw = json.loads(text, object_pairs_hook=_object_no_duplicates)
    except SafeTensorsParseError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SafeTensorsParseError(f"invalid sharded-index UTF-8 JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise SafeTensorsParseError("sharded index must be a JSON object")
    weight_map = raw.get("weight_map")
    metadata = raw.get("metadata", {})
    if not isinstance(weight_map, dict):
        raise SafeTensorsParseError("sharded index weight_map must be an object")
    if not isinstance(metadata, dict):
        raise SafeTensorsParseError("sharded index metadata must be an object")
    try:
        return SafeTensorsShardIndex(
            weight_map=weight_map,
            metadata=metadata,
            unknown_fields={
                key: value
                for key, value in raw.items()
                if key not in {"metadata", "weight_map"}
            },
        )
    except (TypeError, ValueError) as exc:
        raise SafeTensorsParseError(f"invalid sharded index: {exc}") from exc


def load_index(source: str | PathLike[str] | BinaryIO | TextIO) -> SafeTensorsShardIndex:
    """Parse a sharded index from a path or readable stream."""

    if isinstance(source, (str, PathLike)):
        return loads_index(Path(source).read_bytes())
    data = source.read()
    if not isinstance(data, (str, bytes, bytearray, memoryview)):
        raise TypeError("sharded-index stream read() must return str or bytes")
    return loads_index(data)


def dumps_index(index: SafeTensorsShardIndex) -> str:
    """Serialize a sharded index as canonical compact JSON."""

    document: dict[str, Any] = {
        "metadata": dict(index.metadata),
        "weight_map": dict(index.weight_map),
    }
    document.update(index.unknown_fields)
    try:
        return json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise SafeTensorsWriteError(
            f"sharded index is not JSON serializable: {exc}"
        ) from exc


def dump_index(
    index: SafeTensorsShardIndex,
    destination: str | PathLike[str] | TextIO,
) -> None:
    """Serialize a sharded index to a UTF-8 path or text stream."""

    text = dumps_index(index)
    if isinstance(destination, (str, PathLike)):
        Path(destination).write_text(text, encoding="utf-8")
        return
    written = destination.write(text)
    if written is not None and written != len(text):
        raise SafeTensorsWriteError(
            f"short sharded-index write: {written} of {len(text)} characters"
        )

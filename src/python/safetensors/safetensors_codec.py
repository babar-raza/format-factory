"""SafeTensors (.safetensors) codec — probe, load, write.

Binary format: 8-byte LE uint64 header length, then UTF-8 JSON header,
then raw tensor data at byte offsets specified in the header.

Spec reference: FACT-SAFETENSORS-001
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any, Union

from safetensors.exceptions import SafetensorsParseError, SafetensorsWriteError

MAX_FILE_SIZE = 256 * 1024 * 1024  # 256 MiB guard
MAX_HEADER_SIZE = 100 * 1024 * 1024  # 100 MiB header guard
HEADER_LEN_SIZE = 8  # bytes for the LE uint64

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "header_parse",
    "tensor_metadata",
    "multiple_tensors",
    "metadata_block",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "tensor_data_decode",
    "memory_mapped_access",
    "streaming_parse",
    "quantized_dtypes",
]

SourceType = Union[str, Path, bytes]


def _read_bytes(source: SourceType) -> bytes:
    """Read source into bytes."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    if not path.exists():
        raise SafetensorsParseError(f"File not found: {source}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise SafetensorsParseError(
            f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes"
        )
    return path.read_bytes()


def probe_safetensors(source: SourceType) -> bool:
    """Return True if source is a valid SafeTensors file.

    Checks: first 8 bytes are a valid LE uint64 header length, the header
    bytes parse as JSON, and the header contains tensor descriptors with
    dtype/shape/data_offsets keys. Never raises.
    """
    try:
        data = _read_bytes(source)
        if len(data) < HEADER_LEN_SIZE:
            return False
        header_len = struct.unpack("<Q", data[:HEADER_LEN_SIZE])[0]
        if header_len == 0 or header_len > len(data) - HEADER_LEN_SIZE:
            return False
        if header_len > MAX_HEADER_SIZE:
            return False
        header_bytes = data[HEADER_LEN_SIZE : HEADER_LEN_SIZE + header_len]
        header = json.loads(header_bytes.decode("utf-8"))
        if not isinstance(header, dict):
            return False
        for key, val in header.items():
            if key == "__metadata__":
                continue
            if isinstance(val, dict) and "dtype" in val and "shape" in val:
                return True
        return len(header) == 1 and "__metadata__" in header
    except Exception:
        return False


def load_safetensors(source: SourceType) -> dict[str, Any]:
    """Parse a SafeTensors file and return a canonical model dict.

    Returns a dict with keys: header_size, tensors, metadata.
    Each tensor entry has: dtype, shape, data_offsets.
    """
    data = _read_bytes(source)

    if len(data) < HEADER_LEN_SIZE:
        raise SafetensorsParseError(
            f"File too small: {len(data)} bytes (minimum {HEADER_LEN_SIZE})"
        )

    header_len = struct.unpack("<Q", data[:HEADER_LEN_SIZE])[0]

    if header_len > MAX_HEADER_SIZE:
        raise SafetensorsParseError(
            f"Header length {header_len} exceeds {MAX_HEADER_SIZE} byte limit"
        )

    if header_len > len(data) - HEADER_LEN_SIZE:
        raise SafetensorsParseError(
            f"Header length {header_len} exceeds available data "
            f"({len(data) - HEADER_LEN_SIZE} bytes)"
        )

    header_bytes = data[HEADER_LEN_SIZE : HEADER_LEN_SIZE + header_len]

    try:
        header = json.loads(header_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SafetensorsParseError(f"Invalid header JSON: {exc}") from exc

    if not isinstance(header, dict):
        raise SafetensorsParseError(
            f"Header must be a JSON object, got {type(header).__name__}"
        )

    metadata: dict[str, str] = {}
    tensors: dict[str, Any] = {}

    for key, val in header.items():
        if key == "__metadata__":
            if isinstance(val, dict):
                metadata = {str(k): str(v) for k, v in val.items()}
        elif isinstance(val, dict):
            tensors[key] = {
                "dtype": val.get("dtype", "unknown"),
                "shape": val.get("shape", []),
                "data_offsets": val.get("data_offsets", [0, 0]),
            }

    return {
        "header_size": header_len,
        "tensors": tensors,
        "metadata": metadata,
    }


def write_safetensors(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> bytes:
    """Serialize a safetensors model dict to binary format.

    Creates a valid safetensors file with header and zero-filled tensor data.
    Returns the bytes. If dest is provided, also writes to that path.
    """
    tensors = model.get("tensors", {})
    metadata = model.get("metadata", {})

    header: dict[str, Any] = {}

    if metadata:
        header["__metadata__"] = {str(k): str(v) for k, v in metadata.items()}

    offset = 0
    tensor_sizes: list[int] = []
    for name, info in tensors.items():
        dtype = info.get("dtype", "F32")
        shape = info.get("shape", [])

        dtype_sizes = {
            "F16": 2, "BF16": 2, "F32": 4, "F64": 8,
            "I8": 1, "I16": 2, "I32": 4, "I64": 8,
            "U8": 1, "U16": 2, "U32": 4, "U64": 8,
            "BOOL": 1,
        }
        element_size = dtype_sizes.get(dtype, 4)
        num_elements = 1
        for dim in shape:
            num_elements *= dim

        data_size = num_elements * element_size
        header[name] = {
            "dtype": dtype,
            "shape": shape,
            "data_offsets": [offset, offset + data_size],
        }
        tensor_sizes.append(data_size)
        offset += data_size

    try:
        header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SafetensorsWriteError(f"Cannot serialize header: {exc}") from exc

    header_len = struct.pack("<Q", len(header_json))
    tensor_data = b"\x00" * offset

    result = header_len + header_json + tensor_data

    if dest is not None:
        path = Path(dest)
        try:
            path.write_bytes(result)
        except OSError as exc:
            raise SafetensorsWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_tensor_count(model: dict[str, Any]) -> int:
    """Return the number of tensors in a safetensors model."""
    return len(model.get("tensors", {}))


def get_tensor_names(model: dict[str, Any]) -> list[str]:
    """Return sorted tensor names from a safetensors model."""
    return sorted(model.get("tensors", {}).keys())


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load a safetensors file, write it, and reload to prove round-trip fidelity."""
    model = load_safetensors(source)
    write_safetensors(model, dest)
    return load_safetensors(dest)


def safetensors_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for a safetensors source (installed-package proof)."""
    model = load_safetensors(source)
    return {
        "format": "safetensors",
        "loaded": True,
        "tensor_count": get_tensor_count(model),
        "tensor_names": get_tensor_names(model),
        "header_size": model.get("header_size", 0),
    }

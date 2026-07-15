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
from safetensors.safetensors_validation import (
    detect_duplicate_tensor_keys,
    slice_tensor_bytes,
    validate_tensor_offsets,
)
from safetensors.spec.header.tensor import Tensor

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
    "tensor_data_decode",
    "offset_integrity_validation",
    "duplicate_key_rejection",
    "fp8_dtypes",
]

UNSUPPORTED_FEATURES = [
    "memory_mapped_access",
    "streaming_parse",
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
        # object_pairs_hook sees every JSON object's raw (key, value) pairs
        # before json normally collapses duplicate keys, so it can reject a
        # header with a literal duplicate tensor key (FACT-SAFETENSORS-105).
        header = json.loads(
            header_bytes.decode("utf-8"), object_pairs_hook=detect_duplicate_tensor_keys
        )
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

    data_section = data[HEADER_LEN_SIZE + header_len :]
    # FACT-SAFETENSORS-104: reject overlapping/out-of-bounds/gapped offsets
    # before the model is ever handed back to a caller.
    validate_tensor_offsets(tensors, len(data_section))

    return {
        "header_size": header_len,
        "tensors": tensors,
        "metadata": metadata,
        # Real tensor data buffer (FACT-SAFETENSORS-101) — sliced on demand by
        # get_tensor_bytes()/get_tensor() using each tensor's data_offsets.
        "data": data_section,
    }


def write_safetensors(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> bytes:
    """Serialize a safetensors model dict to binary format.

    Creates a valid safetensors file with a header and real tensor data
    (FACT-SAFETENSORS-103). For each tensor, the payload bytes are resolved
    in this priority order:

    1. `info["data"]` — caller-supplied real bytes for that tensor. Its
       length must exactly match `num_elements * dtype_byte_size`.
    2. `model["data"]` — a raw data buffer from a prior `load_safetensors()`
       call (e.g. via `roundtrip()`); the tensor's own `data_offsets` are used
       to slice its original bytes out of that buffer, so a load->write cycle
       preserves real byte content rather than zero-filling it.
    3. Zero-fill — only when neither of the above is available (fully
       backward compatible with callers that only supply dtype/shape).

    Returns the bytes. If dest is provided, also writes to that path.
    """
    tensors = model.get("tensors", {})
    metadata = model.get("metadata", {})
    source_data = model.get("data")

    header: dict[str, Any] = {}

    if metadata:
        header["__metadata__"] = {str(k): str(v) for k, v in metadata.items()}

    offset = 0
    payloads: list[bytes] = []
    for name, info in tensors.items():
        dtype = info.get("dtype", "F32")
        shape = info.get("shape", [])

        element_size = Tensor.DTYPE_BYTE_SIZES.get(dtype, 4)
        num_elements = 1
        for dim in shape:
            num_elements *= dim
        expected_size = num_elements * element_size

        payload = info.get("data")
        if payload is not None:
            if not isinstance(payload, (bytes, bytearray)):
                raise SafetensorsWriteError(
                    f"Tensor {name!r} data must be bytes, got {type(payload).__name__}"
                )
            payload = bytes(payload)
            if len(payload) != expected_size:
                raise SafetensorsWriteError(
                    f"Tensor {name!r} data is {len(payload)} byte(s), expected "
                    f"{expected_size} byte(s) for dtype {dtype} shape {shape}"
                )
        elif source_data is not None:
            orig_offsets = info.get("data_offsets", [0, 0])
            payload = None
            if (
                isinstance(orig_offsets, (list, tuple))
                and len(orig_offsets) == 2
                and isinstance(orig_offsets[0], int)
                and isinstance(orig_offsets[1], int)
                and 0 <= orig_offsets[0] <= orig_offsets[1] <= len(source_data)
                and orig_offsets[1] - orig_offsets[0] == expected_size
            ):
                payload = source_data[orig_offsets[0] : orig_offsets[1]]
            if payload is None:
                payload = b"\x00" * expected_size
        else:
            payload = b"\x00" * expected_size

        header[name] = {
            "dtype": dtype,
            "shape": shape,
            "data_offsets": [offset, offset + expected_size],
        }
        payloads.append(payload)
        offset += expected_size

    try:
        header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SafetensorsWriteError(f"Cannot serialize header: {exc}") from exc

    header_len = struct.pack("<Q", len(header_json))
    tensor_data = b"".join(payloads)

    result = header_len + header_json + tensor_data

    if dest is not None:
        path = Path(dest)
        try:
            path.write_bytes(result)
        except OSError as exc:
            raise SafetensorsWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_tensor_bytes(model: dict[str, Any], name: str) -> bytes:
    """Return the real byte payload for tensor `name` (FACT-SAFETENSORS-101).

    Slices `model["data"]` (the raw data buffer captured by `load_safetensors`)
    using the tensor's stored `data_offsets` — this is the actual tensor
    content, not just header metadata.
    """
    tensors = model.get("tensors", {})
    if name not in tensors:
        raise SafetensorsParseError(f"Tensor {name!r} not found in model")
    data = model.get("data")
    if data is None:
        raise SafetensorsParseError(
            "Model has no data buffer; load it with load_safetensors() first"
        )
    return slice_tensor_bytes(data, tensors[name].get("data_offsets", [0, 0]), name)


def get_tensor(model: dict[str, Any], name: str) -> Any:
    """Decode tensor `name` into a numpy.ndarray (FACT-SAFETENSORS-102).

    Uses the tensor's dtype/shape to interpret the raw bytes returned by
    `get_tensor_bytes`. BF16 and the fp8 dtypes are decoded via a real
    bit-level reinterpretation (see `safetensors.dtype_codec`).
    """
    from safetensors.dtype_codec import decode_tensor_array

    raw = get_tensor_bytes(model, name)
    info = model["tensors"][name]
    return decode_tensor_array(raw, info.get("dtype", "F32"), info.get("shape", []))


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

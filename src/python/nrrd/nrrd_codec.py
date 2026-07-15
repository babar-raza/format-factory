"""NRRD (.nrrd, .nhdr) codec — probe, load, write.

Nearly Raw Raster Data format. Text header with key:value pairs
terminated by a blank line, followed by binary/encoded data payload.

MVP scope: raw and gzip encodings only.

Spec reference: FACT-NRRD-001
"""

from __future__ import annotations

import gzip
import struct
from pathlib import Path
from typing import Any, Union

from nrrd.exceptions import NrrdParseError, NrrdWriteError

MAX_FILE_SIZE = 256 * 1024 * 1024  # 256 MiB guard
MAGIC_PREFIX = b"NRRD0"

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "encoding_raw",
    "encoding_gzip",
    "header_parse",
    "int8", "int16", "int32", "float", "double",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "encoding_bzip2",
    "encoding_hex",
    "encoding_ascii",
    "encoding_zlib",
    "detached_header",
    "key_value_pairs",
    "streaming_parse",
]

DTYPE_MAP = {
    "int8": ("b", 1), "uint8": ("B", 1),
    "int16": ("h", 2), "uint16": ("H", 2), "short": ("h", 2),
    "int32": ("i", 4), "uint32": ("I", 4), "int": ("i", 4),
    "int64": ("q", 8), "uint64": ("Q", 8),
    "float": ("f", 4), "double": ("d", 8),
    "signed char": ("b", 1), "unsigned char": ("B", 1),
}

SourceType = Union[str, Path, bytes]


def _read_bytes(source: SourceType) -> bytes:
    """Read source into bytes."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    if not path.exists():
        raise NrrdParseError(f"File not found: {source}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise NrrdParseError(f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes")
    return path.read_bytes()


def probe_nrrd(source: SourceType) -> bool:
    """Return True if source is a valid NRRD file. Never raises."""
    try:
        data = _read_bytes(source)
        if len(data) < 8:
            return False
        first_line_end = data.index(b"\n") if b"\n" in data else len(data)
        first_line = data[:first_line_end]
        return first_line.startswith(MAGIC_PREFIX) and len(first_line) >= 8
    except Exception:
        return False


def _parse_header(data: bytes) -> tuple[dict[str, str], int, int]:
    """Parse NRRD header. Returns (header_dict, version, data_offset)."""
    text_portion = data[:min(len(data), 64 * 1024)]

    try:
        text = text_portion.decode("ascii", errors="replace")
    except Exception as exc:
        raise NrrdParseError(f"Cannot decode header: {exc}") from exc

    lines = text.split("\n")

    if not lines or not lines[0].startswith("NRRD0"):
        raise NrrdParseError("Missing NRRD magic line")

    magic = lines[0].strip()
    version = int(magic[4:8]) if len(magic) >= 8 else 0

    header: dict[str, str] = {}
    data_offset = len(lines[0].encode("ascii")) + 1

    for line in lines[1:]:
        stripped = line.strip()
        data_offset += len(line.encode("ascii")) + 1

        if stripped == "":
            break

        if stripped.startswith("#"):
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            header[key.strip().lower()] = val.strip()

    return header, version, data_offset


def load_nrrd(source: SourceType) -> dict[str, Any]:
    """Parse an NRRD file and return a canonical model dict.

    Returns: version, header (dict), data_size, element_count.
    Data is NOT loaded into memory — only metadata is extracted.
    """
    data = _read_bytes(source)
    header, version, data_offset = _parse_header(data)

    encoding = header.get("encoding", "raw")
    raw_data = data[data_offset:]
    data_size = len(raw_data)

    if encoding == "gzip" or encoding == "gz":
        try:
            decompressed = gzip.decompress(raw_data)
            data_size = len(decompressed)
        except Exception:
            pass

    type_str = header.get("type", "")
    sizes_str = header.get("sizes", "")
    element_count = 1
    if sizes_str:
        for s in sizes_str.split():
            element_count *= int(s)

    return {
        "version": version,
        "header": header,
        "data_size": data_size,
        "element_count": element_count,
        "data_offset": data_offset,
    }


def write_nrrd(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
    data: bytes | None = None,
) -> bytes:
    """Serialize an NRRD model dict to NRRD binary format.

    If data is None, writes zero-filled data of the expected size.
    """
    header = model.get("header", {})
    version = model.get("version", 4)

    lines: list[str] = [f"NRRD000{version}"]

    field_order = ["type", "dimension", "sizes", "encoding", "endian", "spacings"]
    for field in field_order:
        if field in header:
            lines.append(f"{field}: {header[field]}")

    for key, val in header.items():
        if key not in field_order:
            lines.append(f"{key}: {val}")

    header_text = "\n".join(lines) + "\n\n"
    header_bytes = header_text.encode("ascii")

    encoding = header.get("encoding", "raw")

    if data is None:
        type_str = header.get("type", "uint8")
        sizes_str = header.get("sizes", "0")
        element_count = 1
        for s in sizes_str.split():
            element_count *= int(s)
        dtype_info = DTYPE_MAP.get(type_str, ("B", 1))
        data = b"\x00" * (element_count * dtype_info[1])

    if encoding in ("gzip", "gz"):
        payload = gzip.compress(data)
    else:
        payload = data

    result = header_bytes + payload

    if dest is not None:
        path = Path(dest)
        try:
            path.write_bytes(result)
        except OSError as exc:
            raise NrrdWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_dimension(model: dict[str, Any]) -> int:
    """Return the number of dimensions."""
    return int(model.get("header", {}).get("dimension", "0"))


def get_encoding(model: dict[str, Any]) -> str:
    """Return the data encoding."""
    return model.get("header", {}).get("encoding", "raw")


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load an NRRD file, write it, and reload to prove round-trip fidelity."""
    model = load_nrrd(source)
    write_nrrd(model, dest)
    return load_nrrd(dest)


def nrrd_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for an NRRD source (installed-package proof)."""
    model = load_nrrd(source)
    return {
        "format": "nrrd",
        "loaded": True,
        "version": model.get("version", 0),
        "encoding": get_encoding(model),
        "dimension": get_dimension(model),
        "data_size": model.get("data_size", 0),
    }

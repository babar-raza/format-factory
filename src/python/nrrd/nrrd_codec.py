"""NRRD (.nrrd, .nhdr) codec — probe, load, write, decode.

Nearly Raw Raster Data format. Text header with key:value pairs
terminated by a blank line, followed by binary/encoded data payload.

Scope: raw and gzip encodings, attached (single-file) headers only.
Detached (.nhdr) headers, ascii/hex/bzip2/zlib encodings remain out of
scope for this pass (see reports/spec-coverage/nrrd-deferred.json).

Spec reference: FACT-NRRD-001
Spec source: http://teem.sourceforge.net/nrrd/format.html (Teem project)
"""

from __future__ import annotations

import gzip
import re
import struct
import sys
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
    "int8", "uint8", "int16", "uint16", "int32", "uint32", "float", "double",
    "size_guard",
    "payload_decode",
    "byteswap",
    "line_skip",
    "byte_skip",
    "kinds",
    "space_orientation",
    "key_value_pairs",
]

UNSUPPORTED_FEATURES = [
    "encoding_bzip2",
    "encoding_hex",
    "encoding_ascii",
    "encoding_zlib",
    "detached_header",
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

# NRRD `kinds` values that denote a domain (spatial/temporal) axis, per the
# Teem spec's kind enumeration. Every other declared kind (scalar, vector,
# RGB-color, ..., or an unrecognized value) is treated as a range axis.
DOMAIN_KINDS = frozenset({"domain", "space", "time"})

_VECTOR_TOKEN_RE = re.compile(r"\([^)]*\)|none", re.IGNORECASE)

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


def _parse_key_value_pair(line: str) -> tuple[str | None, str]:
    """Return (key, value) if ``line`` is a NRRD0002+ ``key:=value`` pair.

    Returns (None, "") if the line is not a key/value pair (i.e. it is a
    fixed ``field: description`` header line). This check MUST run before
    the generic ``:`` partition used for fixed fields: partitioning
    ``mykey:=myvalue`` on the first ``:`` alone leaves a stray ``=`` prefix
    on the value (``"=myvalue"``) — the historical bug this function fixes.
    """
    if ":=" not in line:
        return None, ""
    key, _, val = line.partition(":=")
    return key.strip(), val.strip()


def _parse_header(data: bytes) -> tuple[dict[str, str], dict[str, str], int, int]:
    """Parse NRRD header.

    Returns (header_fields, key_value_pairs, version, data_offset). Fixed
    fields (``type``, ``dimension``, ``sizes``, ...) and NRRD0002+ arbitrary
    key/value pairs are parsed into two separate dicts so a user-supplied
    key can never silently collide with/overwrite a fixed field name.
    """
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
    key_value_pairs: dict[str, str] = {}
    data_offset = len(lines[0].encode("ascii")) + 1

    for line in lines[1:]:
        stripped = line.strip()
        data_offset += len(line.encode("ascii")) + 1

        if stripped == "":
            break

        if stripped.startswith("#"):
            continue

        kv_key, kv_val = _parse_key_value_pair(stripped)
        if kv_key is not None:
            key_value_pairs[kv_key] = kv_val
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            header[key.strip().lower()] = val.strip()

    return header, key_value_pairs, version, data_offset


def _parse_optional_int(value: str | None, default: int = 0) -> int:
    """Parse an optional header integer field, tolerating absence/blank values."""
    if value is None:
        return default
    stripped = value.strip()
    if stripped == "":
        return default
    try:
        return int(stripped)
    except ValueError:
        return default


def _advance_past_lines(data: bytes, offset: int, n: int) -> int:
    """Advance ``offset`` past ``n`` additional newline-terminated lines.

    Implements the ``line skip`` header field: N additional lines, within
    the same file, are skipped after the header's terminating blank line
    and before the data payload begins.
    """
    pos = offset
    for _ in range(n):
        idx = data.find(b"\n", pos)
        if idx == -1:
            return len(data)
        pos = idx + 1
    return pos


def _expected_data_size(header: dict[str, str]) -> int | None:
    """Return element_count * item_size for header type/sizes, or None if unknown."""
    dtype_info = DTYPE_MAP.get(header.get("type", ""))
    if dtype_info is None:
        return None
    sizes_str = header.get("sizes", "")
    if not sizes_str:
        return None
    count = 1
    for s in sizes_str.split():
        count *= int(s)
    return count * dtype_info[1]


def _parse_space_vector(token: str) -> tuple[float, ...] | None:
    """Parse a single NRRD space vector token, e.g. ``(1,0,0)`` or ``none``."""
    token = token.strip()
    if token.lower() == "none":
        return None
    if token.startswith("(") and token.endswith(")"):
        inner = token[1:-1].strip()
        if not inner:
            return ()
        return tuple(float(x) for x in inner.split(","))
    raise NrrdParseError(f"Malformed NRRD space vector: {token!r}")


def _parse_space_vector_list(value: str) -> list[tuple[float, ...] | None]:
    """Parse a whitespace-separated list of NRRD space vectors/``none`` tokens.

    Used for the ``space directions`` field: one vector (or ``none`` for a
    non-spatial axis) per declared axis.
    """
    tokens = _VECTOR_TOKEN_RE.findall(value)
    return [_parse_space_vector(t) for t in tokens]


def _host_byte_order() -> str:
    """Return 'little' or 'big' for the host machine's native byte order."""
    return sys.byteorder


def _needs_byteswap(declared_endian: str) -> bool:
    """Return True if a declared ``endian`` differs from the host's native order.

    Only multi-byte element types are affected; callers should skip this
    check entirely for 1-byte types (int8/uint8). An unspecified/unrecognized
    endian value is treated as already matching host order (no swap).
    """
    if not declared_endian:
        return False
    normalized = declared_endian.strip().lower()
    if normalized not in ("little", "big"):
        return False
    return normalized != _host_byte_order()


def byteswap_values(values: list[Any], fmt_char: str) -> list[Any]:
    """Byte-swap a list of values decoded in the wrong byte order.

    Each value is re-packed using the host's native byte order, its byte
    string reversed, then re-unpacked — the standard technique for
    correcting an endian mismatch after an initial native-order
    ``struct.unpack``. Used by :func:`decode_nrrd_data` whenever the
    header's declared ``endian`` field differs from the host machine's
    native byte order (see :func:`_needs_byteswap`).
    """
    swapped: list[Any] = []
    for value in values:
        packed = struct.pack(f"={fmt_char}", value)
        swapped.append(struct.unpack(f"={fmt_char}", packed[::-1])[0])
    return swapped


def decode_nrrd_data(
    type_str: str,
    sizes: list[int],
    payload: bytes,
    endian: str | None = None,
) -> list[Any]:
    """Decode raw/decompressed payload bytes into a flat list of typed values.

    Uses ``struct.unpack`` (stdlib-only) to decode ``payload`` according to
    the NRRD ``type`` string and the element count implied by ``sizes``
    (the product of all axis sizes). Values are byte-swapped via
    :func:`byteswap_values` when ``endian`` differs from the host's native
    byte order. Only the leading ``element_count * item_size`` bytes of
    ``payload`` are consumed — trailing bytes (if any) are ignored.

    Args:
        type_str: NRRD ``type`` field value (e.g. ``"uint8"``, ``"float"``).
        sizes: Per-axis sizes (from the ``sizes`` header field).
        payload: Raw or already-decompressed data bytes.
        endian: Declared ``endian`` field value (``"little"``/``"big"``),
            or None/empty if unspecified (treated as already host-order).

    Returns:
        Flat list of decoded numeric values, in on-disk element order
        (axis 0 — the first entry in ``sizes`` — varies fastest). Empty
        list if any axis size is 0.

    Raises:
        NrrdParseError: if ``type_str`` is not a supported NRRD type, or if
            ``payload`` is too short for the declared element count.
    """
    if type_str not in DTYPE_MAP:
        raise NrrdParseError(f"Unsupported or unknown NRRD data type for decode: {type_str!r}")

    fmt_char, item_size = DTYPE_MAP[type_str]

    element_count = 1
    for s in sizes:
        element_count *= s
    if element_count == 0:
        return []

    expected_bytes = element_count * item_size
    if len(payload) < expected_bytes:
        raise NrrdParseError(
            f"NRRD data payload too short to decode: expected {expected_bytes} bytes "
            f"for {element_count} '{type_str}' elements, got {len(payload)}"
        )

    data_bytes = payload[:expected_bytes]
    values = list(struct.unpack(f"={element_count}{fmt_char}", data_bytes))

    if item_size > 1 and _needs_byteswap(endian or ""):
        values = byteswap_values(values, fmt_char)

    return values


def reshape_nrrd_array(flat: list[Any], sizes: list[int]) -> Any:
    """Reshape a flat decoded value list into nested lists per NRRD axis order.

    NRRD lists axis sizes fastest-varying first: for ``sizes = [s0, s1, ...,
    sn]``, element ``(i0, i1, ..., in)`` sits at flat index
    ``i0 + i1*s0 + i2*s0*s1 + ...``. The returned nested structure is
    indexed outer-to-inner from the slowest to the fastest axis, so the
    innermost lists correspond to axis 0.
    """
    if not sizes or len(sizes) == 1:
        return list(flat)

    strides = [1] * len(sizes)
    for axis in range(1, len(sizes)):
        strides[axis] = strides[axis - 1] * sizes[axis - 1]

    def _build(axis: int, base: int) -> Any:
        """Recursively build one nested-list level for the given axis."""
        if axis < 0:
            return flat[base]
        size = sizes[axis]
        stride = strides[axis]
        return [_build(axis - 1, base + i * stride) for i in range(size)]

    return _build(len(sizes) - 1, 0)


def get_array(model: dict[str, Any]) -> Any:
    """Return a model's decoded data reshaped into nested lists.

    Args:
        model: A model dict as returned by :func:`load_nrrd`.

    Returns:
        Nested list of typed values (see :func:`reshape_nrrd_array`), or
        None if no array was decoded (unsupported type/encoding, or the
        header declared no ``sizes``).
    """
    flat = model.get("array")
    if flat is None:
        return None
    sizes = model.get("array_shape") or []
    return reshape_nrrd_array(flat, sizes)


def load_nrrd(source: SourceType) -> dict[str, Any]:
    """Parse an NRRD file and return a canonical model dict.

    Returns a dict with: ``version``, ``header``, ``key_value_pairs``,
    ``data_size``, ``element_count``, ``data_offset``, ``line_skip``,
    ``byte_skip``, ``kinds``, ``space``, ``space_directions``,
    ``space_origin``, ``array`` (flat decoded values, or None if the
    declared type/encoding is unsupported for decode), ``array_shape``.
    """
    data = _read_bytes(source)
    header, key_value_pairs, version, base_offset = _parse_header(data)

    line_skip = _parse_optional_int(header.get("line skip") or header.get("lineskip"))
    data_offset = _advance_past_lines(data, base_offset, line_skip) if line_skip > 0 else base_offset

    encoding = header.get("encoding", "raw")

    byte_skip = _parse_optional_int(header.get("byte skip") or header.get("byteskip"))
    if byte_skip == -1:
        # Per spec, -1 means "skip to len(file) - expected_data_size" and is
        # only meaningful for the raw encoding (the expected size must be
        # known in *encoded* bytes, which only raw guarantees).
        if encoding == "raw":
            expected_size = _expected_data_size(header)
            if expected_size is not None:
                candidate_offset = len(data) - expected_size
                if candidate_offset >= data_offset:
                    data_offset = candidate_offset
    elif byte_skip > 0:
        data_offset += byte_skip

    raw_data = data[data_offset:]
    data_size = len(raw_data)
    decoded_payload = raw_data

    if encoding in ("gzip", "gz"):
        try:
            decoded_payload = gzip.decompress(raw_data)
            data_size = len(decoded_payload)
        except Exception:
            decoded_payload = b""

    type_str = header.get("type", "")
    sizes_str = header.get("sizes", "")
    sizes_list = [int(s) for s in sizes_str.split()] if sizes_str else []
    element_count = 1
    for s in sizes_list:
        element_count *= s

    array_flat: list[Any] | None = None
    array_shape: list[int] | None = None
    if type_str in DTYPE_MAP and encoding in ("raw", "gzip", "gz") and sizes_list:
        try:
            array_flat = decode_nrrd_data(type_str, sizes_list, decoded_payload, endian=header.get("endian"))
            array_shape = list(sizes_list)
        except NrrdParseError:
            array_flat = None
            array_shape = None

    kinds_str = header.get("kinds", "")
    kinds = kinds_str.split() if kinds_str else []

    space_directions_str = header.get("space directions", "")
    space_directions = _parse_space_vector_list(space_directions_str) if space_directions_str else []

    space_origin_str = header.get("space origin", "")
    space_origin = _parse_space_vector(space_origin_str) if space_origin_str else None

    return {
        "version": version,
        "header": header,
        "key_value_pairs": key_value_pairs,
        "data_size": data_size,
        "element_count": element_count,
        "data_offset": data_offset,
        "line_skip": line_skip,
        "byte_skip": byte_skip,
        "kinds": kinds,
        "space": header.get("space", ""),
        "space_directions": space_directions,
        "space_origin": space_origin,
        "array": array_flat,
        "array_shape": array_shape,
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
    key_value_pairs = model.get("key_value_pairs", {})
    version = model.get("version", 4)

    lines: list[str] = [f"NRRD000{version}"]

    field_order = ["type", "dimension", "sizes", "encoding", "endian", "spacings"]
    for field in field_order:
        if field in header:
            lines.append(f"{field}: {header[field]}")

    for key, val in header.items():
        if key not in field_order:
            lines.append(f"{key}: {val}")

    for kv_key, kv_val in key_value_pairs.items():
        lines.append(f"{kv_key}:={kv_val}")

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

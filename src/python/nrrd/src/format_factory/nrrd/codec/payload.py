"""Bounded NRRD scalar payload encoding and decoding."""

from __future__ import annotations

import bz2
import gzip
import math
import struct
import zlib
from typing import Any, Final

from format_factory.core import (
    CheckedArithmeticError,
    ResourceLimitError,
    ResourceLimits,
    checked_product,
)

from ..errors import NrrdParseError, NrrdWriteError

_DTYPE_ALIASES: Final[dict[str, tuple[str, int]]] = {
    "signed char": ("b", 1), "int8": ("b", 1), "int8_t": ("b", 1),
    "uchar": ("B", 1), "unsigned char": ("B", 1), "uint8": ("B", 1),
    "uint8_t": ("B", 1), "short": ("h", 2), "short int": ("h", 2),
    "signed short": ("h", 2), "signed short int": ("h", 2),
    "int16": ("h", 2), "int16_t": ("h", 2), "ushort": ("H", 2),
    "unsigned short": ("H", 2), "unsigned short int": ("H", 2),
    "uint16": ("H", 2), "uint16_t": ("H", 2), "int": ("i", 4),
    "signed int": ("i", 4), "int32": ("i", 4), "int32_t": ("i", 4),
    "uint": ("I", 4), "unsigned int": ("I", 4), "uint32": ("I", 4),
    "uint32_t": ("I", 4), "longlong": ("q", 8), "long long": ("q", 8),
    "long long int": ("q", 8), "signed long long": ("q", 8),
    "signed long long int": ("q", 8), "int64": ("q", 8), "int64_t": ("q", 8),
    "ulonglong": ("Q", 8), "unsigned long long": ("Q", 8),
    "unsigned long long int": ("Q", 8),
    "uint64": ("Q", 8), "uint64_t": ("Q", 8), "float": ("f", 4),
    "double": ("d", 8),
}

SUPPORTED_ENCODINGS = frozenset(
    {"raw", "ascii", "text", "txt", "hex", "gzip", "gz", "bzip2", "bz2"}
)

#: Encodings whose payload is decimal text. These expose no element byte order,
#: so SAL-NRRD-00014 ("endian is required whenever the encoding exposes byte
#: order") does not apply to them -- Teem reads such files with no `endian`
#: field, and so must we (TC-FF6-NRRD-ASCII-ENDIAN-001).
TEXTUAL_ENCODINGS = frozenset({"ascii", "text", "txt"})

#: Encodings that preserve the byte-level element representation, and therefore
#: do require a declared `endian` for multi-byte types.
BYTE_ORDER_EXPOSING_ENCODINGS = SUPPORTED_ENCODINGS - TEXTUAL_ENCODINGS

#: Byte order used when normalizing a textual payload into the document's
#: derived binary buffer. The on-disk text carries no byte order, so this choice
#: is not observable in output; it is fixed so the derived buffer is
#: deterministic across platforms.
_TEXTUAL_INTERNAL_BYTE_ORDER = "<"


def is_block_type(type_name: str) -> bool:
    """Return whether a declared NRRD type stores opaque fixed-size blocks."""

    return type_name.strip().lower() == "block"


def parse_block_size(value: str | int | None) -> int:
    """Validate the mandatory byte width for an opaque NRRD block value."""

    if value is None:
        raise NrrdParseError("block type requires a block size field")
    try:
        block_size = int(value)
    except ValueError as exc:
        raise NrrdParseError("block size must be a positive integer") from exc
    if block_size <= 0:
        raise NrrdParseError("block size must be a positive integer")
    return block_size


def dtype_info(type_name: str) -> tuple[str, int]:
    try:
        return _DTYPE_ALIASES[type_name.strip().lower()]
    except KeyError as exc:
        raise NrrdParseError(f"unsupported NRRD scalar type: {type_name!r}") from exc


def checked_element_count(sizes: list[int], limits: ResourceLimits) -> int:
    if not sizes:
        raise NrrdParseError("sizes must contain at least one axis")
    if len(sizes) > limits.max_entries:
        raise ResourceLimitError("NRRD dimension exceeds max_entries")
    for size in sizes:
        # NRRD axis sizes must be positive; zero is valid in some other formats,
        # so this stays here rather than moving into the shared primitive.
        if size <= 0:
            raise NrrdParseError("NRRD axis sizes must be positive")
    try:
        return checked_product(
            sizes,
            ceiling=limits.max_decompressed_bytes,
            label="NRRD element count",
        )
    except CheckedArithmeticError as exc:
        # Preserve this package's published error type; the shared primitive
        # carries no opinion about which exception a format exposes.
        raise ResourceLimitError(
            "NRRD element count exceeds resource limits", context=exc.context
        ) from exc


def expected_binary_size(
    type_name: str,
    sizes: list[int],
    limits: ResourceLimits,
    *,
    block_size: int | None = None,
) -> int:
    item_size = (
        parse_block_size(block_size)
        if is_block_type(type_name)
        else dtype_info(type_name)[1]
    )
    expected = checked_element_count(sizes, limits) * item_size
    limits.enforce("max_decompressed_bytes", expected)
    return expected


def _endian_prefix(
    endian: str | None, item_size: int, *, required: bool = True
) -> str:
    if item_size == 1:
        return "="
    normalized = (endian or "").strip().lower()
    if normalized == "little":
        return "<"
    if normalized == "big":
        return ">"
    if normalized:
        raise NrrdParseError(f"invalid endian value: {endian!r}")
    if not required:
        return _TEXTUAL_INTERNAL_BYTE_ORDER
    raise NrrdParseError(
        "endian is required for multi-byte NRRD scalar types "
        f"(item size {item_size}); declare 'endian: little' or 'endian: big'"
    )


def decode_binary(
    type_name: str,
    sizes: list[int],
    payload: bytes,
    *,
    endian: str | None,
    limits: ResourceLimits,
    block_size: int | None = None,
    require_endian: bool = True,
) -> list[Any]:
    count = checked_element_count(sizes, limits)
    expected = expected_binary_size(
        type_name, sizes, limits, block_size=block_size
    )
    if len(payload) != expected:
        raise NrrdParseError(
            f"payload length mismatch: expected {expected} bytes, got {len(payload)}"
        )
    if is_block_type(type_name):
        width = parse_block_size(block_size)
        return [payload[index : index + width] for index in range(0, expected, width)]
    fmt, item_size = dtype_info(type_name)
    prefix = _endian_prefix(endian, item_size, required=require_endian)
    try:
        return list(struct.unpack(f"{prefix}{count}{fmt}", payload))
    except struct.error as exc:
        raise NrrdParseError(f"cannot decode NRRD payload: {exc}") from exc


def encode_binary(
    type_name: str,
    sizes: list[int],
    values: list[Any],
    *,
    endian: str | None,
    limits: ResourceLimits,
    block_size: int | None = None,
    require_endian: bool = True,
) -> bytes:
    count = checked_element_count(sizes, limits)
    if len(values) != count:
        raise NrrdWriteError(
            f"array length mismatch: expected {count} elements, got {len(values)}"
        )
    if is_block_type(type_name):
        width = parse_block_size(block_size)
        blocks: list[bytes] = []
        for index, value in enumerate(values):
            if not isinstance(value, (bytes, bytearray, memoryview)):
                raise NrrdWriteError(
                    f"block value {index} must be bytes-like, not {type(value).__name__}"
                )
            block = bytes(value)
            if len(block) != width:
                raise NrrdWriteError(
                    f"block value {index} has {len(block)} bytes; expected {width}"
                )
            blocks.append(block)
        result = b"".join(blocks)
        limits.enforce("max_output_bytes", len(result))
        return result
    fmt, item_size = dtype_info(type_name)
    prefix = _endian_prefix(endian, item_size, required=require_endian)
    try:
        result = struct.pack(f"{prefix}{count}{fmt}", *values)
    except (OverflowError, struct.error, TypeError) as exc:
        raise NrrdWriteError(f"cannot encode NRRD values: {exc}") from exc
    limits.enforce("max_output_bytes", len(result))
    return result


def _enforce_expansion(encoded_size: int, decoded_size: int, limits: ResourceLimits) -> None:
    limits.enforce("max_decompressed_bytes", decoded_size)
    if encoded_size and decoded_size / encoded_size > limits.max_compression_ratio:
        raise ResourceLimitError("NRRD decompression ratio exceeds configured limit")


def decode_encoding(payload: bytes, encoding: str, *, limits: ResourceLimits) -> bytes:
    normalized = encoding.lower()
    if normalized == "raw":
        result = payload
    elif normalized in {"gzip", "gz"}:
        gzip_decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        result = gzip_decoder.decompress(payload, limits.max_decompressed_bytes + 1)
        if gzip_decoder.unconsumed_tail or len(result) > limits.max_decompressed_bytes:
            raise ResourceLimitError("gzip payload exceeds decompression limit")
        result += gzip_decoder.flush(limits.max_decompressed_bytes + 1 - len(result))
        if not gzip_decoder.eof:
            raise NrrdParseError("truncated gzip payload")
        if gzip_decoder.unused_data:
            raise NrrdParseError("trailing data after gzip payload")
    elif normalized in {"bzip2", "bz2"}:
        bzip2_decoder = bz2.BZ2Decompressor()
        try:
            result = bzip2_decoder.decompress(
                payload, max_length=limits.max_decompressed_bytes + 1
            )
        except OSError as exc:
            raise NrrdParseError(f"invalid bzip2 payload: {exc}") from exc
        if not bzip2_decoder.eof:
            if len(result) > limits.max_decompressed_bytes:
                raise ResourceLimitError("bzip2 payload exceeds decompression limit")
            raise NrrdParseError("truncated or oversized bzip2 payload")
        if bzip2_decoder.unused_data:
            raise NrrdParseError("trailing data after bzip2 payload")
    elif normalized == "hex":
        try:
            result = bytes.fromhex(payload.decode("ascii"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise NrrdParseError(f"invalid hexadecimal payload: {exc}") from exc
    else:
        raise NrrdParseError(f"binary decode is not valid for encoding {encoding!r}")
    _enforce_expansion(len(payload), len(result), limits)
    return result


def decode_ascii(
    type_name: str, sizes: list[int], payload: bytes, *, limits: ResourceLimits
) -> list[Any]:
    fmt, _ = dtype_info(type_name)
    expected = checked_element_count(sizes, limits)
    try:
        tokens = payload.decode("ascii").split()
    except UnicodeDecodeError as exc:
        raise NrrdParseError("ASCII NRRD payload is not ASCII") from exc
    if len(tokens) != expected:
        raise NrrdParseError(
            f"ASCII value count mismatch: expected {expected}, got {len(tokens)}"
        )
    converter = float if fmt in {"f", "d"} else int
    try:
        values = [converter(token) for token in tokens]
    except ValueError as exc:
        raise NrrdParseError(f"invalid ASCII scalar: {exc}") from exc
    if any(isinstance(value, float) and not math.isfinite(value) for value in values):
        raise NrrdParseError("non-finite ASCII scalar is not accepted in strict mode")
    return values


def encode_encoding(
    binary: bytes,
    values: list[Any],
    encoding: str,
    *,
    limits: ResourceLimits,
) -> bytes:
    normalized = encoding.lower()
    if normalized == "raw":
        result = binary
    elif normalized in {"gzip", "gz"}:
        result = gzip.compress(binary, mtime=0)
    elif normalized in {"bzip2", "bz2"}:
        result = bz2.compress(binary)
    elif normalized == "hex":
        result = binary.hex().encode("ascii")
    elif normalized in {"ascii", "text", "txt"}:
        result = (" ".join(str(value) for value in values) + "\n").encode("ascii")
    else:
        raise NrrdWriteError(f"unsupported NRRD encoding: {encoding!r}")
    limits.enforce("max_output_bytes", len(result))
    return result

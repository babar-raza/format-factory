"""Strict, bounded NRRD0001-NRRD0005 reader."""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from format_factory.core import BinarySource, ProbeResult, ResourceLimits

from ...errors import NrrdParseError
from ...model import NrrdDocument
from ...security import effective_limits
from ..payload import (
    SUPPORTED_ENCODINGS,
    decode_ascii,
    decode_binary,
    decode_encoding,
    encode_binary,
    expected_binary_size,
)

_REQUIRED_FIELDS = frozenset({"type", "dimension", "sizes", "encoding"})


def _read_source(source: BinarySource, limits: ResourceLimits) -> tuple[bytes, Path | None]:
    path: Path | None = None
    if isinstance(source, bytes):
        data = source
    elif isinstance(source, (bytearray, memoryview)):
        data = bytes(source)
    elif isinstance(source, (str, PathLike)):
        path = Path(source)
        try:
            limits.enforce("max_input_bytes", path.stat().st_size)
            data = path.read_bytes()
        except OSError as exc:
            raise NrrdParseError(f"cannot read {path}: {exc}") from exc
    elif hasattr(source, "read"):
        data = source.read(limits.max_input_bytes + 1)
        if not isinstance(data, bytes):
            raise TypeError("binary source read() must return bytes")
    else:
        raise TypeError("source must be bytes, a path, or a binary stream")
    limits.enforce("max_input_bytes", len(data))
    return data, path


def _split_header(data: bytes, limits: ResourceLimits) -> tuple[bytes, bytes, int]:
    candidates: list[tuple[int, int]] = []
    for terminator in (b"\n\n", b"\r\n\r\n"):
        index = data.find(terminator)
        if index >= 0:
            candidates.append((index, len(terminator)))
    if not candidates:
        raise NrrdParseError("NRRD header has no blank-line terminator")
    index, terminator_size = min(candidates, key=lambda item: item[0])
    end = index + terminator_size
    limits.enforce("max_header_bytes", end)
    return data[:index], data[end:], end


def _parse_header(
    raw_header: bytes,
) -> tuple[int, dict[str, str], list[str], dict[str, str]]:
    try:
        text = raw_header.decode("ascii")
    except UnicodeDecodeError as exc:
        raise NrrdParseError("NRRD header must be ASCII") from exc
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or len(lines[0]) != 8 or not lines[0].startswith("NRRD000"):
        raise NrrdParseError("invalid NRRD magic")
    try:
        version = int(lines[0][-1])
    except ValueError as exc:
        raise NrrdParseError("invalid NRRD version") from exc
    if not 1 <= version <= 5:
        raise NrrdParseError(f"unsupported NRRD version: {version}")

    header: dict[str, str] = {}
    comments: list[str] = []
    key_values: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        if line.startswith("#"):
            comments.append(line[1:].lstrip())
            continue
        if ":=" in line:
            key, value = line.split(":=", 1)
            if not key:
                raise NrrdParseError(f"empty key/value key at line {line_number}")
            if key in key_values:
                raise NrrdParseError(f"duplicate key/value key {key!r}")
            key_values[key] = value
            continue
        if ":" not in line:
            raise NrrdParseError(f"malformed header line {line_number}")
        key, value = line.split(":", 1)
        normalized = key.strip().lower()
        if not normalized or not value.strip():
            raise NrrdParseError(f"malformed header field at line {line_number}")
        if normalized in header:
            raise NrrdParseError(f"duplicate header field {normalized!r}")
        header[normalized] = value.strip()
    missing = sorted(_REQUIRED_FIELDS.difference(header))
    if missing:
        raise NrrdParseError(f"missing required header fields: {', '.join(missing)}")
    return version, header, comments, key_values


def _parse_sizes(header: dict[str, str]) -> list[int]:
    try:
        sizes = [int(value) for value in header["sizes"].split()]
        dimension = int(header["dimension"])
    except ValueError as exc:
        raise NrrdParseError("dimension and sizes must be integers") from exc
    if dimension <= 0 or len(sizes) != dimension:
        raise NrrdParseError("dimension must be positive and equal the number of sizes")
    return sizes


def _safe_detached_payload(
    value: str, *, source_path: Path | None, limits: ResourceLimits
) -> bytes:
    if source_path is None:
        raise NrrdParseError("detached data requires a filesystem header source")
    if value.upper().startswith("LIST") or "%" in value:
        raise NrrdParseError("detached LIST and printf-pattern payloads are not yet supported")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise NrrdParseError("unsafe detached data path")
    base = source_path.resolve().parent
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise NrrdParseError("detached data path escapes its header directory") from exc
    try:
        limits.enforce("max_input_bytes", resolved.stat().st_size)
        return resolved.read_bytes()
    except OSError as exc:
        raise NrrdParseError(f"cannot read detached payload {resolved}: {exc}") from exc


def _apply_skips(payload: bytes, header: dict[str, str]) -> bytes:
    try:
        line_skip = int(header.get("line skip", header.get("lineskip", "0")))
        byte_skip = int(header.get("byte skip", header.get("byteskip", "0")))
    except ValueError as exc:
        raise NrrdParseError("line skip and byte skip must be integers") from exc
    if line_skip < 0 or byte_skip < -1:
        raise NrrdParseError("invalid line skip or byte skip")
    for _ in range(line_skip):
        newline = payload.find(b"\n")
        if newline < 0:
            raise NrrdParseError("line skip exceeds payload")
        payload = payload[newline + 1 :]
    if byte_skip > 0:
        if byte_skip > len(payload):
            raise NrrdParseError("byte skip exceeds payload")
        payload = payload[byte_skip:]
    return payload


def probe(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> ProbeResult:
    """Inspect a bounded source without surfacing parse failures."""

    try:
        data, _ = _read_source(source, effective_limits(limits))
        line = data.splitlines()[0] if data else b""
        matched = (
            len(line) == 8
            and line.startswith(b"NRRD000")
            and line[-1:] in {b"1", b"2", b"3", b"4", b"5"}
        )
        return ProbeResult(
            matched=matched,
            confidence=1.0 if matched else 0.0,
            format_id="nrrd",
            profile=line.decode("ascii") if matched else None,
            reason="recognized NRRD magic" if matched else "NRRD magic not found",
        )
    except Exception:
        return ProbeResult(False, 0.0, "nrrd", reason="source is not readable")


def loads(
    data: bytes | bytearray | memoryview,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> NrrdDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    return _load(data, limits=effective_limits(limits))


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> NrrdDocument:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    return _load(source, limits=effective_limits(limits))


def _load(source: BinarySource, *, limits: ResourceLimits) -> NrrdDocument:
    data, source_path = _read_source(source, limits)
    raw_header, attached, data_offset = _split_header(data, limits)
    version, header, comments, key_values = _parse_header(raw_header)
    sizes = _parse_sizes(header)
    encoding = header["encoding"].lower()
    if encoding not in SUPPORTED_ENCODINGS:
        raise NrrdParseError(f"unsupported NRRD encoding: {encoding!r}")
    payload = (
        _safe_detached_payload(
            header["data file"], source_path=source_path, limits=limits
        )
        if "data file" in header
        else attached
    )
    payload = _apply_skips(payload, header)
    if header.get("byte skip", header.get("byteskip")) == "-1":
        if encoding != "raw":
            raise NrrdParseError("byte skip -1 is valid only for raw encoding")
        expected = expected_binary_size(header["type"], sizes, limits)
        if expected > len(payload):
            raise NrrdParseError("byte skip -1 payload is truncated")
        payload = payload[-expected:]

    if encoding in {"ascii", "text", "txt"}:
        array = decode_ascii(header["type"], sizes, payload, limits=limits)
        binary = encode_binary(
            header["type"],
            sizes,
            array,
            endian=header.get("endian"),
            limits=limits,
        )
    else:
        binary = decode_encoding(payload, encoding, limits=limits)
        array = decode_binary(
            header["type"],
            sizes,
            binary,
            endian=header.get("endian"),
            limits=limits,
        )
    return NrrdDocument(
        version=version,
        header=header,
        comments=comments,
        key_value_pairs=key_values,
        raw_header=raw_header,
        payload=binary,
        array=array,
        source_path=str(source_path) if source_path else None,
        data_offset=data_offset,
    )

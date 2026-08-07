"""NRRD-LAZY-001: header-only loading, lazy payload access, memory mapping
for eligible uncompressed data, and streaming decode for compressed
payloads.

"Provide header-only and lazy payload loading, memory mapping for eligible
uncompressed data, streaming decode, and region reads where layout
permits, reporting when full decompression is required."

Scope, stated plainly: eligible for zero-copy memory mapping is exactly a
raw-encoded, single-physical-file (attached, or a plain detached filename --
not a LIST or printf-numbered multi-file sequence) payload with zero line
skip and zero byte skip. Streaming decode covers gzip/bzip2-encoded
single-file payloads (attached or detached), read incrementally through
the standard library's own decompressing file wrappers rather than fully
materialized upfront. Anything else -- textual encodings, hex, multi-file
detached forms, or a declared line/byte skip -- is disclosed via
PayloadAccess as IN_MEMORY / not region-readable: honest disclosure that
the existing eager load()/loads() path is the only way to read that
payload, not a silent claim of laziness this module cannot deliver.

Region reads (byte-range access without materializing the whole array) are
supported only in MEMORY_MAPPED mode. A compressed stream is not randomly
seekable without decoding everything before the requested point, so
region() is not offered in STREAMING_DECODE mode -- PayloadAccess.full_decode_required
is True there, and the caller reads sequentially via read_stream() instead.

This module never touches codec/reader/reader.py's existing eager `_load`
path -- it is purely additive, reading the header with its own bounded
incremental reader (so a header-only call on a multi-gigabyte payload
genuinely reads only the header bytes, not the whole file).
"""

from __future__ import annotations

import bz2
import gzip
import mmap
import re
from dataclasses import dataclass
from enum import StrEnum
from os import PathLike
from pathlib import Path
from typing import BinaryIO

from format_factory.core import BinarySource, ResourceLimits

from ..errors import NrrdError, NrrdParseError
from ..security import effective_limits
from .reader.reader import _parse_header, _parse_sizes

_COMPRESSED_ENCODINGS = frozenset({"gzip", "gz", "bzip2", "bz2"})
_LIST_OR_PRINTF = re.compile(r"%")


class PayloadAccessMode(StrEnum):
    """How a payload would be reached, disclosed before it is opened."""

    HEADER_ONLY = "header_only"
    MEMORY_MAPPED = "memory_mapped"
    STREAMING_DECODE = "streaming_decode"
    IN_MEMORY = "in_memory"


@dataclass(frozen=True, slots=True)
class PayloadAccess:
    """Machine-readable disclosure of how a payload would be, or was, reached."""

    mode: PayloadAccessMode
    zero_copy: bool
    region_reads: bool
    full_payload_read_required: bool
    full_decode_required: bool
    detail: str


@dataclass(frozen=True, slots=True)
class NrrdHeader:
    """Validated header fields and comments/key-values, no payload opened."""

    version: int
    header: dict[str, str]
    comments: tuple[str, ...]
    key_value_pairs: dict[str, str]
    access: PayloadAccess
    source_path: str | None
    data_offset: int


def _read_header_stream(stream: BinaryIO, limits: ResourceLimits) -> tuple[bytes, int]:
    """Read only as many bytes as needed to find the blank-line terminator."""
    chunk_size = 4096
    buffer = b""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            raise NrrdParseError("NRRD header has no blank-line terminator")
        buffer += chunk
        limits.enforce("max_header_bytes", len(buffer))
        best: tuple[int, int] | None = None
        for terminator in (b"\n\n", b"\r\n\r\n"):
            index = buffer.find(terminator)
            if index >= 0 and (best is None or index < best[0]):
                best = (index, len(terminator))
        if best is not None:
            index, terminator_size = best
            return buffer[:index], index + terminator_size


def _read_header_only(
    source: BinarySource, limits: ResourceLimits
) -> tuple[bytes, Path | None, int]:
    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
        for terminator in (b"\n\n", b"\r\n\r\n"):
            index = data.find(terminator)
            if index >= 0:
                limits.enforce("max_header_bytes", index + len(terminator))
                return data[:index], None, index + len(terminator)
        raise NrrdParseError("NRRD header has no blank-line terminator")
    if isinstance(source, (str, PathLike)):
        path = Path(source)
        try:
            with path.open("rb") as stream:
                raw_header, offset = _read_header_stream(stream, limits)
        except OSError as exc:
            raise NrrdParseError(f"cannot read {path}: {exc}") from exc
        return raw_header, path, offset
    if hasattr(source, "read"):
        raw_header, offset = _read_header_stream(source, limits)
        return raw_header, None, offset
    raise TypeError("source must be bytes, a path, or a binary stream")


def _single_detached_filename(value: str) -> str | None:
    """Return the plain filename if `data file` names exactly one file, else None."""
    stripped = value.strip()
    if stripped.upper().startswith("LIST") or "%" in stripped:
        return None
    return stripped


def _resolve_detached_path(name: str, *, source_path: Path, version: int) -> Path:
    """Resolve a detached filename the same way reader.py's eager path does:
    no absolute paths, no traversal outside the header's own directory, and
    the same pre-NRRD0004-vs-NRRD0004+ './' signifier distinction."""
    if version < 4:
        if name.startswith("./"):
            name = name[2:]
        elif not name.startswith("/"):
            raise NrrdParseError(
                "pre-NRRD0004 detached data file names must start with "
                "'./' to be resolved relative to the header; this reader "
                "does not support cwd-relative resolution"
            )
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise NrrdParseError("unsafe detached data path")
    base = source_path.resolve().parent
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise NrrdParseError("detached data path escapes its header directory") from exc
    return resolved


def _describe_access(
    header: dict[str, str], *, source_path: Path | None
) -> PayloadAccess:
    encoding = header.get("encoding", "").lower()
    data_file = header.get("data file")
    single_name = _single_detached_filename(data_file) if data_file is not None else None
    is_multi_file = data_file is not None and single_name is None
    line_skip = header.get("line skip", header.get("lineskip", "0"))
    byte_skip = header.get("byte skip", header.get("byteskip", "0"))
    has_skip = line_skip not in ("0", "") or byte_skip not in ("0", "")

    if is_multi_file:
        return PayloadAccess(
            mode=PayloadAccessMode.IN_MEMORY,
            zero_copy=False,
            region_reads=False,
            full_payload_read_required=True,
            full_decode_required=False,
            detail="multi-file detached data (LIST or printf sequence) is not lazily accessible",
        )
    if data_file is not None and source_path is None:
        return PayloadAccess(
            mode=PayloadAccessMode.IN_MEMORY,
            zero_copy=False,
            region_reads=False,
            full_payload_read_required=True,
            full_decode_required=False,
            detail="detached data requires a filesystem header source",
        )
    if encoding == "raw" and not has_skip:
        return PayloadAccess(
            mode=PayloadAccessMode.MEMORY_MAPPED,
            zero_copy=True,
            region_reads=True,
            full_payload_read_required=False,
            full_decode_required=False,
            detail="raw encoding, single file, no line/byte skip: eligible for memory mapping",
        )
    if encoding in _COMPRESSED_ENCODINGS and (data_file is None or source_path is not None):
        return PayloadAccess(
            mode=PayloadAccessMode.STREAMING_DECODE,
            zero_copy=False,
            region_reads=False,
            full_payload_read_required=False,
            full_decode_required=True,
            detail=f"{encoding} payload is decoded incrementally via a streaming decompressor",
        )
    if encoding == "raw" and has_skip:
        reason = "a declared line or byte skip"
    elif encoding in _COMPRESSED_ENCODINGS:
        reason = "a detached compressed payload with no filesystem header source"
    else:
        reason = f"the {encoding!r} encoding"
    return PayloadAccess(
        mode=PayloadAccessMode.IN_MEMORY,
        zero_copy=False,
        region_reads=False,
        full_payload_read_required=True,
        full_decode_required=encoding in _COMPRESSED_ENCODINGS,
        detail=f"{reason} is not lazily accessible; use load()/loads() instead",
    )


def read_header(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> NrrdHeader:
    """Parse only the header; never opens or reads the payload bytes."""
    active_limits = effective_limits(limits)
    raw_header, source_path, data_offset = _read_header_only(source, active_limits)
    version, header, comments, key_values = _parse_header(raw_header)
    _parse_sizes(header)  # validates dimension/sizes eagerly; header-only, no payload touched
    access = _describe_access(header, source_path=source_path)
    return NrrdHeader(
        version=version,
        header=header,
        comments=tuple(comments),
        key_value_pairs=key_values,
        access=access,
        source_path=str(source_path) if source_path else None,
        data_offset=data_offset,
    )


class NrrdLazyPayload:
    """A lazily-opened NRRD payload: a memory-mapped raw buffer, a streaming
    decompressor, or a disclosure-only stand-in when neither applies."""

    def __init__(
        self,
        *,
        access: PayloadAccess,
        mapped: mmap.mmap | None = None,
        stream: gzip.GzipFile | bz2.BZ2File | None = None,
        owner_file: BinaryIO | None = None,
        start: int = 0,
    ) -> None:
        self.access = access
        self._mapped = mapped
        self._stream = stream
        self._owner_file = owner_file
        self._start = start
        self._closed = False

    def region(self, start: int, end: int) -> memoryview:
        """Zero-copy byte-range view. Only available in MEMORY_MAPPED mode."""
        if self._mapped is None:
            raise NrrdError(
                f"region reads are not available in {self.access.mode.value} mode: "
                f"{self.access.detail}"
            )
        if start < 0 or end < start:
            raise ValueError("region bounds must satisfy 0 <= start <= end")
        return memoryview(self._mapped)[self._start + start : self._start + end]

    def read_stream(self, size: int = -1) -> bytes:
        """Sequential decoded bytes. Only available in STREAMING_DECODE mode."""
        if self._stream is None:
            raise NrrdError(
                f"sequential streaming is not available in {self.access.mode.value} mode: "
                f"{self.access.detail}"
            )
        return self._stream.read(size)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._mapped is not None:
            self._mapped.close()
        if self._stream is not None:
            self._stream.close()
        if self._owner_file is not None:
            self._owner_file.close()

    def __enter__(self) -> "NrrdLazyPayload":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def open_lazy_payload(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> tuple[NrrdHeader, NrrdLazyPayload]:
    """Open the header and, where eligible, a lazy view of the payload.

    Never called by load()/loads()/validate()/dumps() -- this is a distinct,
    explicitly-invoked entry point.
    """
    active_limits = effective_limits(limits)
    header = read_header(source, limits=active_limits)
    mode = header.access.mode

    if mode is PayloadAccessMode.MEMORY_MAPPED:
        assert header.source_path is not None  # guaranteed by _describe_access
        data_file = header.header.get("data file")
        if data_file is None:
            payload_path = Path(header.source_path)
            start = header.data_offset
        else:
            name = _single_detached_filename(data_file)
            assert name is not None
            payload_path = _resolve_detached_path(
                name, source_path=Path(header.source_path), version=header.version
            )
            start = 0
        file_obj = payload_path.open("rb")
        try:
            file_size = payload_path.stat().st_size
            if file_size <= start:
                raise NrrdError(f"{payload_path} has no payload bytes after the header")
            mapped = mmap.mmap(file_obj.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, ValueError) as exc:
            file_obj.close()
            raise NrrdError(f"cannot memory-map {payload_path}: {exc}") from exc
        return header, NrrdLazyPayload(
            access=header.access, mapped=mapped, owner_file=file_obj, start=start
        )

    if mode is PayloadAccessMode.STREAMING_DECODE:
        assert header.source_path is not None  # guaranteed by _describe_access
        data_file = header.header.get("data file")
        encoding = header.header["encoding"].lower()
        if data_file is None:
            file_obj = Path(header.source_path).open("rb")
            file_obj.seek(header.data_offset)
        else:
            name = _single_detached_filename(data_file)
            assert name is not None
            payload_path = _resolve_detached_path(
                name, source_path=Path(header.source_path), version=header.version
            )
            file_obj = payload_path.open("rb")
        stream: gzip.GzipFile | bz2.BZ2File
        if encoding in {"gzip", "gz"}:
            stream = gzip.GzipFile(fileobj=file_obj)
        else:
            stream = bz2.BZ2File(file_obj)
        return header, NrrdLazyPayload(access=header.access, stream=stream, owner_file=file_obj)

    return header, NrrdLazyPayload(access=header.access)


__all__ = [
    "NrrdHeader",
    "NrrdLazyPayload",
    "PayloadAccess",
    "PayloadAccessMode",
    "open_lazy_payload",
    "read_header",
]

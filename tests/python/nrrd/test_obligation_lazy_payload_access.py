"""NRRD-LAZY-001: header-only loading, lazy payload access, memory mapping,
and streaming decode.

MUST: "Provide header-only and lazy payload loading, memory mapping for
eligible uncompressed data, streaming decode, and region reads where
layout permits, reporting when full decompression is required."

Scope, stated plainly: memory mapping is eligible only for raw-encoded,
single-physical-file payloads with zero line/byte skip. Streaming decode
covers gzip/bzip2-encoded single-file payloads. Multi-file detached forms
(LIST, printf sequences), textual encodings (ascii/text/hex), and a
declared line/byte skip fall back to an honest IN_MEMORY disclosure --
proven here as explicit negative/disclosure cases, not silently ignored.
See codec/lazy.py's own module docstring for the full scope statement.
"""

from __future__ import annotations

import bz2
import gzip
import io
from pathlib import Path

import pytest

from format_factory.nrrd import (
    NrrdError,
    NrrdParseError,
    PayloadAccessMode,
    loads,
    open_lazy_payload,
    read_header,
)


def _attached(header_lines: list[str], payload: bytes) -> bytes:
    header = "\n".join(header_lines).encode("ascii") + b"\n\n"
    return header + payload


def _minimal_raw_lines(sizes: str = "8") -> list[str]:
    return [
        "NRRD0004",
        "type: uint8",
        "dimension: 1",
        f"sizes: {sizes}",
        "encoding: raw",
    ]


# ── Header-only reading touches only the header ─────────────────────────────


class _TrackingStream(io.BytesIO):
    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.total_read = 0

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        chunk = super().read(size)
        self.total_read += len(chunk)
        return chunk


def test_header_only_does_not_read_the_payload_from_a_stream() -> None:
    payload = b"\0" * 1_000_000
    data = _attached(_minimal_raw_lines(sizes=str(len(payload))), payload)
    stream = _TrackingStream(data)

    header = read_header(stream)

    assert stream.total_read < len(payload)
    assert header.access.mode is PayloadAccessMode.MEMORY_MAPPED


def test_header_only_from_a_path_does_not_read_the_whole_file(tmp_path: Path) -> None:
    payload = b"\0" * 1_000_000
    data = _attached(_minimal_raw_lines(sizes=str(len(payload))), payload)
    path = tmp_path / "big.nrrd"
    path.write_bytes(data)

    header = read_header(path)

    assert header.header["type"] == "uint8"
    assert header.data_offset < 200


def test_header_only_from_bytes_reports_correct_offset_and_fields() -> None:
    data = _attached(_minimal_raw_lines(), bytes(range(8)))

    header = read_header(data)

    assert header.version == 4
    assert header.header["encoding"] == "raw"
    assert header.data_offset == data.index(b"\n\n") + 2


def test_header_only_rejects_missing_terminator() -> None:
    with pytest.raises(NrrdParseError, match="terminator"):
        read_header(b"NRRD0004\ntype: uint8\n")


# ── Memory mapping: attached raw ────────────────────────────────────────────


def test_attached_raw_is_eligible_for_memory_mapping(tmp_path: Path) -> None:
    payload = bytes(range(8))
    path = tmp_path / "a.nrrd"
    path.write_bytes(_attached(_minimal_raw_lines(), payload))

    header, lazy = open_lazy_payload(path)
    try:
        assert header.access.mode is PayloadAccessMode.MEMORY_MAPPED
        assert header.access.zero_copy is True
        region = lazy.region(0, 8)
        assert bytes(region) == payload
        del region
    finally:
        lazy.close()


def test_memory_mapped_region_matches_eager_load(tmp_path: Path) -> None:
    payload = bytes(range(32))
    data = _attached(_minimal_raw_lines(sizes="32"), payload)
    path = tmp_path / "a.nrrd"
    path.write_bytes(data)

    document = loads(data)
    header, lazy = open_lazy_payload(path)
    try:
        region = lazy.region(0, 32)
        assert bytes(region) == bytes(document.payload)
        del region
    finally:
        lazy.close()


def test_partial_region_read_returns_only_the_requested_bytes(tmp_path: Path) -> None:
    payload = bytes(range(16))
    path = tmp_path / "a.nrrd"
    path.write_bytes(_attached(_minimal_raw_lines(sizes="16"), payload))

    header, lazy = open_lazy_payload(path)
    try:
        region = lazy.region(4, 10)
        assert bytes(region) == payload[4:10]
        del region
    finally:
        lazy.close()


def test_memory_mapped_close_releases_the_file_handle(tmp_path: Path) -> None:
    path = tmp_path / "a.nrrd"
    path.write_bytes(_attached(_minimal_raw_lines(), bytes(range(8))))

    header, lazy = open_lazy_payload(path)
    lazy.close()
    lazy.close()  # redundant close must not raise

    # The underlying file must be closeable/removable now.
    path.unlink()


# ── Memory mapping: detached single file ────────────────────────────────────


def test_detached_single_file_raw_is_eligible_for_memory_mapping(tmp_path: Path) -> None:
    (tmp_path / "payload.raw").write_bytes(bytes(range(4)))
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "data file: payload.raw",
    ]
    path = tmp_path / "d.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    header, lazy = open_lazy_payload(path)
    try:
        assert header.access.mode is PayloadAccessMode.MEMORY_MAPPED
        region = lazy.region(0, 4)
        assert bytes(region) == bytes(range(4))
        del region
    finally:
        lazy.close()


def test_detached_lazy_access_rejects_path_traversal(tmp_path: Path) -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 1", "encoding: raw",
        "data file: ../../etc/passwd",
    ]
    path = tmp_path / "evil.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    with pytest.raises(NrrdParseError, match="unsafe"):
        open_lazy_payload(path)


def test_detached_lazy_access_rejects_absolute_path(tmp_path: Path) -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 1", "encoding: raw",
        "data file: /etc/passwd",
    ]
    path = tmp_path / "evil2.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    with pytest.raises(NrrdParseError):
        open_lazy_payload(path)


def test_detached_lazy_access_applies_the_pre_nrrd0004_dot_slash_version_gate(
    tmp_path: Path,
) -> None:
    """The lazy path (_resolve_detached_path) duplicates reader.py's eager
    path resolution logic -- proven separately here so the two cannot
    silently diverge. See SAL-NRRD-OBL-4CAFF21A47F62F19."""
    (tmp_path / "payload.raw").write_bytes(bytes(range(4)))
    header_lines = [
        "NRRD0003", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "data file: payload.raw",
    ]
    path = tmp_path / "d3.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    with pytest.raises(NrrdParseError, match="pre-NRRD0004"):
        open_lazy_payload(path)


# ── Streaming decode: gzip and bzip2 ─────────────────────────────────────────


def test_gzip_encoding_is_eligible_for_streaming_not_mapping(tmp_path: Path) -> None:
    raw = bytes(range(64))
    compressed = gzip.compress(raw)
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 64", "encoding: gzip",
    ]
    path = tmp_path / "g.nrrd"
    path.write_bytes(_attached(header_lines, compressed))

    header = read_header(path)
    assert header.access.mode is PayloadAccessMode.STREAMING_DECODE
    assert header.access.full_decode_required is True
    assert header.access.region_reads is False


def test_gzip_streaming_decode_matches_eager_load(tmp_path: Path) -> None:
    raw = bytes(range(64))
    compressed = gzip.compress(raw)
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 64", "encoding: gzip",
    ]
    data = _attached(header_lines, compressed)
    path = tmp_path / "g.nrrd"
    path.write_bytes(data)

    document = loads(data)
    header, lazy = open_lazy_payload(path)
    try:
        decoded = lazy.read_stream()
        assert decoded == raw == bytes(document.payload)
    finally:
        lazy.close()


def test_bzip2_streaming_decode_matches_eager_load(tmp_path: Path) -> None:
    raw = bytes(range(48))
    compressed = bz2.compress(raw)
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 48", "encoding: bzip2",
    ]
    data = _attached(header_lines, compressed)
    path = tmp_path / "b.nrrd"
    path.write_bytes(data)

    document = loads(data)
    header, lazy = open_lazy_payload(path)
    try:
        decoded = lazy.read_stream()
        assert decoded == raw == bytes(document.payload)
    finally:
        lazy.close()


def test_streaming_decode_supports_incremental_reads(tmp_path: Path) -> None:
    raw = bytes(range(64))
    compressed = gzip.compress(raw)
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 64", "encoding: gzip",
    ]
    path = tmp_path / "g.nrrd"
    path.write_bytes(_attached(header_lines, compressed))

    header, lazy = open_lazy_payload(path)
    try:
        first = lazy.read_stream(16)
        rest = lazy.read_stream()
        assert first + rest == raw
    finally:
        lazy.close()


# ── Region reads are unavailable outside memory-mapped mode ────────────────


def test_region_raises_in_streaming_decode_mode(tmp_path: Path) -> None:
    compressed = gzip.compress(bytes(range(8)))
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 8", "encoding: gzip",
    ]
    path = tmp_path / "g.nrrd"
    path.write_bytes(_attached(header_lines, compressed))

    header, lazy = open_lazy_payload(path)
    try:
        with pytest.raises(NrrdError, match="region reads"):
            lazy.region(0, 4)
    finally:
        lazy.close()


def test_read_stream_raises_in_memory_mapped_mode(tmp_path: Path) -> None:
    path = tmp_path / "a.nrrd"
    path.write_bytes(_attached(_minimal_raw_lines(), bytes(range(8))))

    header, lazy = open_lazy_payload(path)
    try:
        with pytest.raises(NrrdError, match="streaming"):
            lazy.read_stream()
    finally:
        lazy.close()


def test_region_raises_in_in_memory_mode() -> None:
    header_lines = ["NRRD0004", "type: uint8", "dimension: 1", "sizes: 3", "encoding: ascii"]
    data = _attached(header_lines, b"1 2 3\n")

    header, lazy = open_lazy_payload(data)
    try:
        with pytest.raises(NrrdError, match="region reads"):
            lazy.region(0, 1)
    finally:
        lazy.close()


# ── Honest disclosure: reporting when full decompression/materialization is required ─


def test_multi_file_list_detached_reports_in_memory_required(tmp_path: Path) -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "data file: LIST", "a.raw", "b.raw",
    ]
    path = tmp_path / "list.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    header = read_header(path)

    assert header.access.mode is PayloadAccessMode.IN_MEMORY
    assert header.access.full_payload_read_required is True


def test_printf_pattern_detached_reports_in_memory_required(tmp_path: Path) -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "data file: slice.%d.raw 0 3 1",
    ]
    path = tmp_path / "printf.nrrd"
    path.write_bytes(("\n".join(header_lines) + "\n\n").encode("ascii"))

    header = read_header(path)

    assert header.access.mode is PayloadAccessMode.IN_MEMORY


def test_textual_encoding_reports_in_memory_required() -> None:
    header_lines = ["NRRD0004", "type: uint8", "dimension: 1", "sizes: 3", "encoding: ascii"]
    data = _attached(header_lines, b"1 2 3\n")

    header = read_header(data)

    assert header.access.mode is PayloadAccessMode.IN_MEMORY
    assert "ascii" in header.access.detail


def test_declared_byte_skip_disqualifies_memory_mapping() -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "byte skip: 2",
    ]
    data = _attached(header_lines, b"XX" + bytes(range(4)))

    header = read_header(data)

    assert header.access.mode is PayloadAccessMode.IN_MEMORY
    assert "skip" in header.access.detail


def test_declared_line_skip_disqualifies_memory_mapping() -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "line skip: 1",
    ]
    data = _attached(header_lines, b"comment line\n" + bytes(range(4)))

    header = read_header(data)

    assert header.access.mode is PayloadAccessMode.IN_MEMORY


def test_bytes_source_with_detached_data_file_reports_in_memory_required() -> None:
    header_lines = [
        "NRRD0004", "type: uint8", "dimension: 1", "sizes: 4", "encoding: raw",
        "data file: payload.raw",
    ]
    data = ("\n".join(header_lines) + "\n\n").encode("ascii")

    header = read_header(data)  # bytes source, no filesystem path

    assert header.access.mode is PayloadAccessMode.IN_MEMORY
    assert "filesystem" in header.access.detail


# ── Bytes-source IN_MEMORY payloads still open (as a disclosure-only stand-in) ──


def test_bytes_source_open_lazy_payload_reports_in_memory_and_offers_no_access() -> None:
    header_lines = ["NRRD0004", "type: uint8", "dimension: 1", "sizes: 3", "encoding: ascii"]
    data = _attached(header_lines, b"1 2 3\n")

    header, lazy = open_lazy_payload(data)
    try:
        assert lazy.access.mode is PayloadAccessMode.IN_MEMORY
        with pytest.raises(NrrdError):
            lazy.region(0, 1)
        with pytest.raises(NrrdError):
            lazy.read_stream()
    finally:
        lazy.close()  # no-op, must not raise

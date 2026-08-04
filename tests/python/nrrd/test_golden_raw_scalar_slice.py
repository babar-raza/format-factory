"""TC-FF6-NRRD-GOLDEN-SLICE-001: raw scalar payload integrity.

Installed-wheel evidence for three exact obligations:
- SAL-NRRD-OBL-5FAF36D205C887AD: enforce endian for exposed multi-byte
  elements; transparently byte-swap on read/write; never transform opaque
  blocks.
- SAL-NRRD-OBL-644276A28216DFC0: require `endian` for raw multi-byte scalar
  payloads and accept only little/big semantics.
- SAL-NRRD-OBL-9C262130232DCD09: validate shape and encoded/decompressed
  payload size with checked arithmetic before allocation; fail hostile
  headers cheaply.
"""
from __future__ import annotations

import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest

from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.nrrd import NrrdDocument, NrrdParseError, NrrdWriteError, dumps, loads


def _raw_header(*, nrrd_type: str, sizes: str, dimension: str, endian: str | None = None,
                 extra: str = "") -> bytes:
    lines = [
        b"NRRD0005",
        f"type: {nrrd_type}".encode("ascii"),
        f"dimension: {dimension}".encode("ascii"),
        f"sizes: {sizes}".encode("ascii"),
    ]
    if endian is not None:
        lines.append(f"endian: {endian}".encode("ascii"))
    lines.append(b"encoding: raw")
    if extra:
        lines.append(extra.encode("ascii"))
    return b"\n".join(lines) + b"\n\n"


# ── Scenario 1: multi-byte raw read without endian fails before allocation ──

def test_multibyte_raw_read_without_endian_fails_before_read():
    header = _raw_header(nrrd_type="uint16", sizes="2", dimension="1")
    payload = struct.pack("<2H", 1, 2)
    with pytest.raises(NrrdParseError, match="endian"):
        loads(header + payload)


@pytest.mark.parametrize("nrrd_type,item_size,fmt", [
    ("int16", 2, "h"), ("uint32", 4, "I"), ("int64", 8, "q"), ("double", 8, "d"),
])
def test_every_multibyte_type_requires_endian(nrrd_type, item_size, fmt):
    header = _raw_header(nrrd_type=nrrd_type, sizes="1", dimension="1")
    payload = struct.pack(f"={fmt}", 1 if fmt != "d" else 1.0)
    with pytest.raises(NrrdParseError, match="endian"):
        loads(header + payload)


def test_missing_endian_with_also_truncated_payload_fails_cleanly():
    """A doubly-invalid header (missing endian AND a truncated payload) must
    still fail with a stable NrrdParseError before struct-level unpacking —
    whichever diagnostic fires first, no silent default and no crash."""
    header = _raw_header(nrrd_type="uint32", sizes="4", dimension="1")
    truncated_payload = b"\x00\x00"  # nowhere near the 16 bytes required
    with pytest.raises(NrrdParseError):
        loads(header + truncated_payload)


# ── Scenario 2: one-byte raw and opaque block payloads never need/get swap ──

def test_one_byte_type_never_requires_endian():
    header = _raw_header(nrrd_type="uint8", sizes="3", dimension="1")
    payload = bytes([1, 2, 3])
    document = loads(header + payload)
    assert document.array == [1, 2, 3]


def test_opaque_block_type_never_requires_endian_and_is_not_byte_swapped():
    document = NrrdDocument(
        version=5,
        header={
            "type": "block", "block size": "4", "dimension": "1", "sizes": "2",
            "encoding": "raw",
        },
        payload=b"",
        array=[b"\xde\xad\xbe\xef", b"\x01\x02\x03\x04"],
    )
    encoded = dumps(document)
    decoded = loads(encoded)
    # Opaque blocks are transferred byte-for-byte, never interpreted/swapped.
    assert decoded.array == [b"\xde\xad\xbe\xef", b"\x01\x02\x03\x04"]


# ── Scenario 3: little/big-endian scalars decode identically, write back correctly ──

@pytest.mark.parametrize("nrrd_type,fmt,values", [
    ("int16", "h", [258, -2]),
    ("uint32", "I", [16909060]),
    ("int64", "q", [72623859790382856]),
    ("double", "d", [1.5, -2.25]),
])
def test_little_and_big_endian_fixtures_decode_to_identical_logical_values(nrrd_type, fmt, values):
    count = len(values)
    little_payload = struct.pack(f"<{count}{fmt}", *values)
    big_payload = struct.pack(f">{count}{fmt}", *values)
    little_header = _raw_header(nrrd_type=nrrd_type, sizes=str(count), dimension="1", endian="little")
    big_header = _raw_header(nrrd_type=nrrd_type, sizes=str(count), dimension="1", endian="big")

    little_doc = loads(little_header + little_payload)
    big_doc = loads(big_header + big_payload)
    assert little_doc.array == values
    assert big_doc.array == values


def test_writer_emits_declared_byte_order():
    document = NrrdDocument(
        version=5,
        header={"type": "int16", "dimension": "1", "sizes": "2", "endian": "big", "encoding": "raw"},
        payload=b"", array=[258, -2],
    )
    encoded = dumps(document)
    assert encoded.endswith(struct.pack(">2h", 258, -2))

    document.header["endian"] = "little"
    encoded_little = dumps(document)
    assert encoded_little.endswith(struct.pack("<2h", 258, -2))
    assert encoded_little != encoded


# ── Scenario 4: invalid endian token / conflicting semantics fail deterministically ──

@pytest.mark.parametrize("bad_endian", ["middle", "LITTLE-ENDIAN", "1", "", "littleendian"])
def test_invalid_endian_token_is_rejected(bad_endian):
    header = _raw_header(nrrd_type="uint16", sizes="1", dimension="1", endian=bad_endian or None)
    payload = struct.pack("<H", 1)
    if not bad_endian:
        # empty string is indistinguishable from "not declared" at the header
        # level (no "endian:" line at all) -- covered by scenario 1 instead.
        pytest.skip("empty endian is the missing-declaration case")
    with pytest.raises(NrrdParseError, match="invalid endian|endian"):
        loads(header + payload)


def test_endian_declared_on_one_byte_type_is_accepted_but_irrelevant():
    """Declaring endian for a one-byte type is harmless (spec allows it);
    it must not change the decoded values."""
    header = _raw_header(nrrd_type="uint8", sizes="2", dimension="1", endian="big")
    payload = bytes([9, 10])
    assert loads(header + payload).array == [9, 10]


# ── Scenario 5: shape/size checked arithmetic before allocation ─────────────

def test_negative_dimension_rejected_before_allocation():
    header = _raw_header(nrrd_type="uint16", sizes="4", dimension="-1", endian="little")
    with pytest.raises(NrrdParseError):
        loads(header + b"\x00" * 8)


def test_declared_byte_count_mismatch_is_rejected():
    header = _raw_header(nrrd_type="uint16", sizes="4", dimension="1", endian="little")
    short_payload = struct.pack("<2H", 1, 2)  # 4 bytes, needs 8
    with pytest.raises(NrrdParseError, match="payload length mismatch"):
        loads(header + short_payload)


def test_shape_multiplication_overflow_is_rejected_before_allocation():
    tiny_limits = ResourceLimits(max_decompressed_bytes=1024)
    header = _raw_header(nrrd_type="double", sizes="100000 100000 100000", dimension="3", endian="little")
    with pytest.raises(ResourceLimitError):
        loads(header + b"", limits=tiny_limits)


def test_truncated_payload_rejected_for_raw_encoding():
    header = _raw_header(nrrd_type="uint32", sizes="4", dimension="1", endian="little")
    with pytest.raises(NrrdParseError, match="payload length mismatch"):
        loads(header + struct.pack("<I", 1))


def test_decompressed_size_limit_enforced_for_gzip():
    import gzip
    tiny_limits = ResourceLimits(max_decompressed_bytes=8)
    oversized = struct.pack("<100I", *range(100))
    header = (
        b"NRRD0005\ntype: uint32\ndimension: 1\nsizes: 100\n"
        b"endian: little\nencoding: gzip\n\n"
    )
    with pytest.raises(ResourceLimitError):
        loads(header + gzip.compress(oversized), limits=tiny_limits)


def test_compression_ratio_limit_enforced():
    import gzip
    ratio_limited = ResourceLimits(max_compression_ratio=2.0, max_decompressed_bytes=10_000_000)
    payload = b"\x00" * 100_000  # compresses far beyond a 2x ratio
    header = (
        b"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 100000\n"
        b"encoding: gzip\n\n"
    )
    with pytest.raises(ResourceLimitError):
        loads(header + gzip.compress(payload), limits=ratio_limited)


# ── Scenario 6: hostile declared shape rejected within bounded memory/time ──

def test_hostile_declared_shape_rejected_within_bounded_memory_and_time(tmp_path: Path):
    """A header declaring an astronomically large shape must be rejected
    quickly and without attempting the implied allocation. Measured in a
    subprocess so a regression that removes the guard shows up as an
    actual timeout/OOM, not just a slow local assertion."""
    script = tmp_path / "hostile_shape.py"
    script.write_text(
        "import sys\n"
        "from format_factory.nrrd import loads, NrrdParseError\n"
        "from format_factory.core import ResourceLimitError\n"
        "header = (\n"
        "    b'NRRD0005\\ntype: double\\ndimension: 3\\n'\n"
        "    b'sizes: 9999999999 9999999999 9999999999\\n'\n"
        "    b'endian: little\\nencoding: raw\\n\\n'\n"
        ")\n"
        "try:\n"
        "    loads(header + b'')\n"
        "    print('NO_EXCEPTION_RAISED')\n"
        "    sys.exit(1)\n"
        "except (NrrdParseError, ResourceLimitError, OverflowError) as exc:\n"
        "    print(f'REJECTED: {type(exc).__name__}')\n"
        "    sys.exit(0)\n",
        encoding="utf-8",
    )
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=10,
    )
    elapsed = time.monotonic() - start
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "REJECTED" in result.stdout
    assert elapsed < 5.0, f"hostile shape rejection took {elapsed:.2f}s, expected a cheap early reject"


# ── Scenario 7: writer roundtrip is byte-order correct and deterministic ────

@pytest.mark.parametrize("endian", ["little", "big"])
def test_writer_roundtrip_is_deterministic_across_three_runs(endian):
    document = NrrdDocument(
        version=5,
        header={"type": "uint32", "dimension": "1", "sizes": "3", "endian": endian, "encoding": "raw"},
        payload=b"", array=[1, 2, 3],
    )
    runs = [dumps(document) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert loads(runs[0]).array == [1, 2, 3]


def test_writer_roundtrip_preserves_logical_values_across_endian_conversion():
    document = NrrdDocument(
        version=5,
        header={"type": "int32", "dimension": "1", "sizes": "2", "endian": "little", "encoding": "raw"},
        payload=b"", array=[-100, 200000],
    )
    little_bytes = dumps(document)
    document.header["endian"] = "big"
    big_bytes = dumps(document)
    assert little_bytes != big_bytes
    assert loads(little_bytes).array == loads(big_bytes).array == [-100, 200000]

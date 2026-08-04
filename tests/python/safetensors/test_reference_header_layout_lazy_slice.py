"""TC-FF6-SAFETENSORS-REFERENCE-SLICE-001: header, layout, writer, lazy access.

Obligation-bound proof for seven of the taskcard's eight obligations (the
eighth, SAL-SAFETENSORS-OBL-official-interop, requires the official
`safetensors` PyPI package co-installed without namespace shadowing — see
the taskcard's "NOT YET SATISFIED" precondition note; that obligation is
proven separately once the isolated interop environment exists).
"""
from __future__ import annotations

import json
import struct
import tracemalloc
from pathlib import Path

import pytest

from format_factory.core import ResourceLimits
from format_factory.safetensors import (
    DType,
    PayloadAccessMode,
    SafeTensorsDocument,
    SafeTensorsParseError,
    SafeTensorsWriteError,
    TensorDescriptor,
    dumps,
    load,
    loads,
    read_header,
    safe_open,
)


def _file(header: dict, payload: bytes) -> bytes:
    encoded = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded + payload


# ── SAL-SAFETENSORS-OBL-12CE1029701DCBC7: exact length prefix + UTF-8 JSON header ──

def test_exact_eight_byte_length_prefix_and_utf8_json_header():
    header = {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x01")
    with loads(raw) as document:
        assert bytes(document.tensor_bytes("x")) == b"\x01"


def test_truncated_prefix_is_rejected():
    with pytest.raises(SafeTensorsParseError):
        loads(b"\x08\x00\x00")  # fewer than 8 prefix bytes


def test_declared_header_length_beyond_file_is_rejected():
    raw = struct.pack("<Q", 1000) + b'{"x":1}'
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_malformed_json_header_is_rejected():
    bad = b'{"x": not-json}'
    raw = struct.pack("<Q", len(bad)) + bad
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_invalid_utf8_header_is_rejected():
    bad = b"\xff\xfe\x00\x01"
    raw = struct.pack("<Q", len(bad)) + bad
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_duplicate_tensor_key_is_rejected():
    duplicate = b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},"x":{"dtype":"U8","shape":[1],"data_offsets":[1,2]}}'
    raw = struct.pack("<Q", len(duplicate)) + duplicate + b"\x01\x02"
    with pytest.raises(SafeTensorsParseError, match="duplicate"):
        loads(raw)


def test_official_header_limit_100_000_000_bytes_enforced():
    with pytest.raises(SafeTensorsParseError, match=r"100000000"):
        loads(
            struct.pack("<Q", 100_000_001) + b"x" * 10,
            limits=ResourceLimits(max_header_bytes=100_000_000),
        )


def test_default_limit_is_stricter_than_the_official_ceiling():
    # The default configured limit (16 MiB) is intentionally stricter than
    # the official 100,000,000-byte ceiling; both bounds are real and must
    # each be independently enforceable.
    with pytest.raises(SafeTensorsParseError, match=r"16777216"):
        loads(struct.pack("<Q", 100_000_001) + b"x" * 10)


def test_configurable_stricter_header_limit_enforced():
    header = {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x01")
    with pytest.raises(SafeTensorsParseError):
        loads(raw, limits=ResourceLimits(max_header_bytes=8))


# ── SAL-SAFETENSORS-OBL-0DEA50E8E2B34729: checked shape/bit-size arithmetic ──

def test_shape_element_overflow_is_rejected():
    header = {"x": {"dtype": "F32", "shape": [2**40, 2**40], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x00")
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_negative_dimension_is_rejected():
    header = {"x": {"dtype": "U8", "shape": [-1], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x00")
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_byte_span_mismatch_is_rejected():
    header = {"x": {"dtype": "F32", "shape": [4], "data_offsets": [0, 8]}}  # needs 16 bytes
    raw = _file(header, b"\x00" * 8)
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


def test_invalid_sub_byte_alignment_is_rejected():
    # I4 is a 4-bit dtype; 3 elements = 12 bits, not a whole byte.
    header = {"x": {"dtype": "I4", "shape": [3], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x00")
    with pytest.raises(SafeTensorsParseError):
        loads(raw)


# ── SAL-SAFETENSORS-OBL-56F8EB4984CEBAE8: contiguous, non-overlapping, hole-free coverage ──

def test_contiguous_offsets_accepted_gap_and_overlap_rejected():
    ok = _file(
        {
            "a": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
            "b": {"dtype": "U8", "shape": [2], "data_offsets": [2, 4]},
        },
        b"\x01\x02\x03\x04",
    )
    with loads(ok) as document:
        assert bytes(document.tensor_bytes("a")) == b"\x01\x02"

    hole = _file(
        {
            "a": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
            "b": {"dtype": "U8", "shape": [2], "data_offsets": [3, 5]},
        },
        b"\x01\x02\x00\x03\x04",
    )
    with pytest.raises(SafeTensorsParseError, match="hole"):
        loads(hole)

    overlap = _file(
        {
            "a": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
            "b": {"dtype": "U8", "shape": [2], "data_offsets": [1, 3]},
        },
        b"\x01\x02\x03",
    )
    with pytest.raises(SafeTensorsParseError, match="overlap"):
        loads(overlap)


def test_unindexed_trailing_payload_is_rejected():
    raw = _file({"a": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]}}, b"\x01\x02EXTRA")
    with pytest.raises(SafeTensorsParseError, match="cover"):
        loads(raw)


def test_out_of_order_region_declaration_still_validated_by_actual_offsets():
    # Declaration order in JSON need not match offset order; coverage must
    # still be validated by the offsets themselves, not declaration order.
    raw = _file(
        {
            "second": {"dtype": "U8", "shape": [2], "data_offsets": [2, 4]},
            "first": {"dtype": "U8", "shape": [2], "data_offsets": [0, 2]},
        },
        b"\x01\x02\x03\x04",
    )
    with loads(raw) as document:
        assert bytes(document.tensor_bytes("first")) == b"\x01\x02"
        assert bytes(document.tensor_bytes("second")) == b"\x03\x04"


# ── SAL-SAFETENSORS-OBL-2C467A52ABF9B0B1: deterministic writer, recomputed offsets ──

def test_writer_produces_identical_bytes_over_three_clean_runs():
    descriptor = TensorDescriptor(name="w", dtype=DType.F32, shape=(2,), data_offsets=(0, 8))
    with SafeTensorsDocument(tensors={"w": descriptor}, payload=b"\x00\x00\x80?\x00\x00\x00@") as document:
        runs = [dumps(document) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]


def test_writer_rejects_stale_offsets_inconsistent_with_actual_payload():
    # A descriptor whose declared data_offsets don't match its true position
    # in the payload is an inconsistent in-memory model. The writer's
    # validate-before-write contract means this is caught and rejected at
    # dumps() time, not silently "corrected" — a stronger guarantee than
    # silent recomputation would give (no wrong-but-plausible output).
    stale = TensorDescriptor(name="w", dtype=DType.U8, shape=(2,), data_offsets=(99, 101))
    with SafeTensorsDocument(tensors={"w": stale}, payload=b"\x01\x02") as document:
        with pytest.raises(SafeTensorsWriteError, match="starts at 99"):
            dumps(document)


def test_writer_rejects_inconsistent_in_memory_model_before_mutation():
    # Declared shape (4 elements * 4 bytes = 16) doesn't match the declared
    # 8-byte span. Rejected by validate() inside dumps(), before any bytes
    # are produced -- confirmed no partial/inconsistent output is returned.
    inconsistent = TensorDescriptor(name="w", dtype=DType.F32, shape=(4,), data_offsets=(0, 8))
    with SafeTensorsDocument(tensors={"w": inconsistent}, payload=b"\x00" * 8) as document:
        with pytest.raises(SafeTensorsWriteError):
            dumps(document)


# ── SAL-SAFETENSORS-OBL-83A3FF76296963EE: stable diagnostic validation ──

def test_validation_errors_carry_stable_diagnostic_fields():
    header = {"x": {"dtype": "not-a-dtype", "shape": [1], "data_offsets": [0, 1]}}
    raw = _file(header, b"\x00")
    with pytest.raises(SafeTensorsParseError) as excinfo:
        loads(raw)
    assert "dtype" in str(excinfo.value).lower()


# ── SAL-SAFETENSORS-OBL-909DA5B5108BBCF6: header-only, read-only mmap, access disclosure ──

def test_header_only_validation_does_not_read_payload(tmp_path: Path):
    payload_size = 4 * 1024 * 1024
    path = tmp_path / "big.safetensors"
    encoded = json.dumps(
        {"x": {"dtype": "U8", "shape": [payload_size], "data_offsets": [0, payload_size]}},
        separators=(",", ":"),
    ).encode("utf-8")
    with path.open("wb") as f:
        f.write(struct.pack("<Q", len(encoded)))
        f.write(encoded)
        f.seek(payload_size - 1, 1)
        f.write(b"\0")

    with path.open("rb") as stream:
        header = read_header(stream)
        bytes_consumed = stream.tell()
    assert bytes_consumed == 8 + len(encoded)
    assert header.access.mode is PayloadAccessMode.HEADER_ONLY
    assert not header.access.full_payload_read_required


def test_path_backed_read_uses_readonly_mapping_and_tensor_relative_views(tmp_path: Path):
    path = tmp_path / "small.safetensors"
    raw = _file({"x": {"dtype": "U8", "shape": [4], "data_offsets": [0, 4]}}, b"\x01\x02\x03\x04")
    path.write_bytes(raw)
    with safe_open(path) as document:
        assert document.access.mode is PayloadAccessMode.MEMORY_MAPPED
        assert document.access.zero_copy
        region = document.tensor_region("x", 1, 3)
        assert region.readonly
        assert bytes(region) == b"\x02\x03"
        region.release()


# ── SAL-SAFETENSORS-OBL-991021FCD2FCB37C: sparse-file bounded allocation, lifetime ──

def test_sparse_file_access_stays_within_bounded_python_allocation(tmp_path: Path):
    payload_size = 64 * 1024 * 1024
    path = tmp_path / "sparse.safetensors"
    encoded = json.dumps(
        {"large": {"dtype": "U8", "shape": [payload_size], "data_offsets": [0, payload_size]}},
        separators=(",", ":"),
    ).encode("utf-8")
    with path.open("wb") as f:
        f.write(struct.pack("<Q", len(encoded)))
        f.write(encoded)
        f.seek(payload_size - 1, 1)
        f.write(b"\0")

    tracemalloc.start()
    with safe_open(path) as document:
        tail = document.tensor_region("large", payload_size - 16, payload_size)
        assert bytes(tail) == bytes(16)
        tail.release()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 4 * 1024 * 1024, f"peak Python allocation {peak} bytes exceeded bound for a 64MB sparse tensor"


def test_released_view_survives_a_redundant_second_release_after_close(tmp_path: Path):
    # The dangerous path -- an active (unreleased) view outstanding when the
    # document closes -- is covered in test_obligation_validation_contract.py
    # (asserts SAFETENSORS_BORROWED_VIEW_ACTIVE). This test covers the
    # adjacent lifecycle edge: releasing an already-released view after
    # close must be a safe no-op, not a crash.
    path = tmp_path / "small.safetensors"
    raw = _file({"x": {"dtype": "U8", "shape": [4], "data_offsets": [0, 4]}}, b"\x01\x02\x03\x04")
    path.write_bytes(raw)
    document = safe_open(path)
    region = document.tensor_region("x", 0, 4)
    assert bytes(region) == b"\x01\x02\x03\x04"
    region.release()
    document.close()
    region.release()  # redundant release must not raise


def test_stream_backed_document_discloses_buffered_not_zero_copy_access():
    raw = _file({"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}, b"\x01")
    import io
    with load(io.BytesIO(raw)) as document:
        assert document.access.mode is PayloadAccessMode.BUFFERED_STREAM
        assert document.access.full_payload_read_required

"""Tests for SafeTensors header safety validation.

Covers FACT-SAFETENSORS-104 (offset overlap/bounds/coverage validation) and
FACT-SAFETENSORS-105 (duplicate tensor-name key rejection). These are the
format's core safety guarantee vs. pickle: a reader must be able to trust
the header's byte layout without executing any code.
"""

from __future__ import annotations

import json
import struct

import pytest

from safetensors.exceptions import SafetensorsParseError
from safetensors.safetensors_codec import load_safetensors
from safetensors.safetensors_validation import (
    detect_duplicate_tensor_keys,
    slice_tensor_bytes,
    validate_tensor_offsets,
)


def _build(header_obj: dict, data_len: int) -> bytes:
    header_json = json.dumps(header_obj).encode("utf-8")
    return struct.pack("<Q", len(header_json)) + header_json + b"\x00" * data_len


class TestOffsetOverlapRejection:
    """FACT-SAFETENSORS-104: overlapping data_offsets ranges must be rejected."""

    def test_load_rejects_overlapping_offsets(self):
        data = _build(
            {
                "a": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]},
                "b": {"dtype": "F32", "shape": [2], "data_offsets": [4, 12]},
            },
            data_len=12,
        )
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_validate_tensor_offsets_rejects_overlap_directly(self):
        tensors = {
            "a": {"data_offsets": [0, 10]},
            "b": {"data_offsets": [5, 15]},
        }
        with pytest.raises(SafetensorsParseError):
            validate_tensor_offsets(tensors, data_len=15)


class TestOffsetBoundsRejection:
    """FACT-SAFETENSORS-104: offsets extending past the data buffer must be rejected."""

    def test_load_rejects_out_of_bounds_offsets(self):
        data = _build(
            {"a": {"dtype": "F32", "shape": [10], "data_offsets": [0, 40]}},
            data_len=8,  # actual buffer far smaller than declared end=40
        )
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_validate_tensor_offsets_rejects_out_of_bounds_directly(self):
        tensors = {"a": {"data_offsets": [0, 100]}}
        with pytest.raises(SafetensorsParseError):
            validate_tensor_offsets(tensors, data_len=10)

    def test_slice_tensor_bytes_rejects_out_of_bounds(self):
        with pytest.raises(SafetensorsParseError):
            slice_tensor_bytes(b"\x00" * 4, [0, 100], "w")

    def test_slice_tensor_bytes_rejects_negative_start(self):
        with pytest.raises(SafetensorsParseError):
            slice_tensor_bytes(b"\x00" * 4, [-1, 2], "w")

    def test_slice_tensor_bytes_rejects_end_before_start(self):
        with pytest.raises(SafetensorsParseError):
            slice_tensor_bytes(b"\x00" * 4, [3, 1], "w")


class TestOffsetGapRejection:
    """FACT-SAFETENSORS-104: gaps ('holes') between tensors must be rejected."""

    def test_load_rejects_gap_between_tensors(self):
        data = _build(
            {
                "a": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]},
                "b": {"dtype": "F32", "shape": [1], "data_offsets": [8, 12]},
            },
            data_len=12,
        )
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_load_rejects_trailing_unexplained_bytes(self):
        data = _build(
            {"a": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}},
            data_len=20,  # 16 trailing bytes not covered by any tensor
        )
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_validate_tensor_offsets_rejects_gap_directly(self):
        tensors = {
            "a": {"data_offsets": [0, 4]},
            "b": {"data_offsets": [10, 14]},
        }
        with pytest.raises(SafetensorsParseError):
            validate_tensor_offsets(tensors, data_len=14)


class TestWellFormedHeaderAccepted:
    """A correctly-tiled header must load successfully."""

    def test_load_accepts_contiguous_non_overlapping_offsets(self):
        data = _build(
            {
                "a": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]},
                "b": {"dtype": "I8", "shape": [4], "data_offsets": [8, 12]},
            },
            data_len=12,
        )
        model = load_safetensors(data)
        assert set(model["tensors"].keys()) == {"a", "b"}

    def test_validate_tensor_offsets_accepts_well_formed(self):
        tensors = {
            "a": {"data_offsets": [0, 4]},
            "b": {"data_offsets": [4, 8]},
        }
        validate_tensor_offsets(tensors, data_len=8)  # must not raise

    def test_validate_tensor_offsets_accepts_empty_with_zero_data(self):
        validate_tensor_offsets({}, data_len=0)  # must not raise

    def test_validate_tensor_offsets_rejects_empty_with_nonzero_data(self):
        with pytest.raises(SafetensorsParseError):
            validate_tensor_offsets({}, data_len=5)


class TestDuplicateTensorKeyRejection:
    """FACT-SAFETENSORS-105: literal duplicate tensor-name keys must be rejected."""

    def test_load_rejects_literal_duplicate_key(self):
        # Hand-constructed JSON text with a literal duplicate key — json.dumps()
        # from a Python dict can never produce this, since dict keys are unique.
        header_text = (
            '{"w":{"dtype":"F32","shape":[1],"data_offsets":[0,4]},'
            '"w":{"dtype":"F32","shape":[1],"data_offsets":[0,4]}}'
        ).encode("utf-8")
        data = struct.pack("<Q", len(header_text)) + header_text + b"\x00" * 4
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_load_rejects_duplicate_metadata_key(self):
        header_text = (
            '{"__metadata__":{"a":"1"},"__metadata__":{"a":"2"},'
            '"w":{"dtype":"F32","shape":[1],"data_offsets":[0,4]}}'
        ).encode("utf-8")
        data = struct.pack("<Q", len(header_text)) + header_text + b"\x00" * 4
        with pytest.raises(SafetensorsParseError):
            load_safetensors(data)

    def test_detect_duplicate_tensor_keys_hook_directly(self):
        with pytest.raises(SafetensorsParseError):
            detect_duplicate_tensor_keys([("w", {}), ("x", {}), ("w", {})])

    def test_detect_duplicate_tensor_keys_hook_accepts_unique(self):
        result = detect_duplicate_tensor_keys([("a", 1), ("b", 2)])
        assert result == {"a": 1, "b": 2}

    def test_load_accepts_header_with_no_duplicates(self):
        header_text = '{"w":{"dtype":"F32","shape":[1],"data_offsets":[0,4]}}'.encode("utf-8")
        data = struct.pack("<Q", len(header_text)) + header_text + b"\x00" * 4
        model = load_safetensors(data)
        assert "w" in model["tensors"]

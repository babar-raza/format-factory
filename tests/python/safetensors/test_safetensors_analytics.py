"""Tests for safetensors_analytics.py — dtype histogram, byte totals, largest tensor.

Each function operates on a freshly-loaded value from a path/bytes source
(FACT-SAFETENSORS-002, FACT-SAFETENSORS-003).
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from safetensors.exceptions import SafetensorsParseError
from safetensors.safetensors_analytics import (
    safetensors_dtype_histogram,
    safetensors_largest_tensor_name,
    safetensors_total_tensor_bytes,
)
from safetensors.safetensors_codec import load_safetensors

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "safetensors"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


def _build_bytes(tensors: dict, metadata: dict | None = None) -> bytes:
    """Build a minimal valid safetensors byte blob for a given tensor header."""
    header = dict(tensors)
    if metadata:
        header["__metadata__"] = metadata
    header_json = json.dumps(header).encode("utf-8")
    total_size = max(
        (info["data_offsets"][1] for info in tensors.values()), default=0
    )
    return struct.pack("<Q", len(header_json)) + header_json + b"\x00" * total_size


class TestDtypeHistogram:
    """L2 behavior: safetensors_dtype_histogram returns correct per-dtype counts."""

    def test_histogram_single_tensor_file(self):
        result = safetensors_dtype_histogram(VALID_DIR / "single-tensor.safetensors")
        assert result == {"F32": 1}

    def test_histogram_multi_tensor_file(self):
        result = safetensors_dtype_histogram(VALID_DIR / "multi-tensor.safetensors")
        assert result == {"F32": 2}

    def test_histogram_with_metadata_sample(self):
        result = safetensors_dtype_histogram(VALID_DIR / "with-metadata.safetensors")
        assert result == {"F32": 1}

    def test_histogram_counts_correct_mixed_dtypes(self):
        data = _build_bytes({
            "a": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]},
            "b": {"dtype": "I8", "shape": [1], "data_offsets": [4, 5]},
            "c": {"dtype": "F32", "shape": [1], "data_offsets": [5, 9]},
        })
        result = safetensors_dtype_histogram(data)
        assert result == {"F32": 2, "I8": 1}

    def test_histogram_from_bytes_source(self):
        data = _build_bytes({"w": {"dtype": "BOOL", "shape": [1], "data_offsets": [0, 1]}})
        result = safetensors_dtype_histogram(data)
        assert result == {"BOOL": 1}

    def test_histogram_empty_tensors(self):
        data = _build_bytes({}, metadata={"note": "empty"})
        result = safetensors_dtype_histogram(data)
        assert result == {}

    def test_histogram_returns_dict_type(self):
        result = safetensors_dtype_histogram(VALID_DIR / "single-tensor.safetensors")
        assert isinstance(result, dict)
        assert all(isinstance(v, int) for v in result.values())


class TestTotalTensorBytes:
    """L2 behavior: safetensors_total_tensor_bytes sums data_offsets spans."""

    def test_total_bytes_single_tensor(self):
        assert safetensors_total_tensor_bytes(VALID_DIR / "single-tensor.safetensors") == 16

    def test_total_bytes_multi_tensor_sum(self):
        assert safetensors_total_tensor_bytes(VALID_DIR / "multi-tensor.safetensors") == 24

    def test_total_bytes_with_metadata_sample(self):
        assert safetensors_total_tensor_bytes(VALID_DIR / "with-metadata.safetensors") == 8

    def test_total_bytes_zero_when_no_tensors(self):
        data = _build_bytes({}, metadata={"note": "empty"})
        assert safetensors_total_tensor_bytes(data) == 0

    def test_total_bytes_from_bytes_source(self):
        data = _build_bytes({"w": {"dtype": "F64", "shape": [1], "data_offsets": [0, 8]}})
        assert safetensors_total_tensor_bytes(data) == 8

    def test_total_bytes_matches_manual_calc(self):
        model = load_safetensors(VALID_DIR / "multi-tensor.safetensors")
        manual_total = sum(
            info["data_offsets"][1] - info["data_offsets"][0]
            for info in model["tensors"].values()
        )
        assert safetensors_total_tensor_bytes(VALID_DIR / "multi-tensor.safetensors") == manual_total

    def test_total_bytes_type_is_int(self):
        result = safetensors_total_tensor_bytes(VALID_DIR / "single-tensor.safetensors")
        assert isinstance(result, int)


class TestLargestTensorName:
    """L2 behavior: safetensors_largest_tensor_name picks the biggest byte span."""

    def test_largest_name_single_tensor(self):
        assert safetensors_largest_tensor_name(VALID_DIR / "single-tensor.safetensors") == "weight"

    def test_largest_name_multi_tensor(self):
        # alpha: 16 bytes, beta: 8 bytes -> alpha is largest
        assert safetensors_largest_tensor_name(VALID_DIR / "multi-tensor.safetensors") == "alpha"

    def test_largest_name_none_when_empty(self):
        data = _build_bytes({}, metadata={"note": "empty"})
        assert safetensors_largest_tensor_name(data) is None

    def test_largest_name_from_bytes_source(self):
        data = _build_bytes({
            "small": {"dtype": "I8", "shape": [1], "data_offsets": [0, 1]},
            "big": {"dtype": "F64", "shape": [4], "data_offsets": [1, 33]},
        })
        assert safetensors_largest_tensor_name(data) == "big"

    def test_largest_name_matches_manual_calc(self):
        model = load_safetensors(VALID_DIR / "multi-tensor.safetensors")
        manual_best = max(
            model["tensors"].items(),
            key=lambda kv: kv[1]["data_offsets"][1] - kv[1]["data_offsets"][0],
        )[0]
        assert safetensors_largest_tensor_name(VALID_DIR / "multi-tensor.safetensors") == manual_best

    def test_largest_name_type_is_str_or_none(self):
        result = safetensors_largest_tensor_name(VALID_DIR / "single-tensor.safetensors")
        assert isinstance(result, str)

    def test_largest_name_with_metadata_sample(self):
        assert safetensors_largest_tensor_name(VALID_DIR / "with-metadata.safetensors") == "bias"


class TestAnalyticsMalformedInputs:
    """L3 edge: analytics functions on malformed/invalid input."""

    def test_dtype_histogram_invalid_file_raises(self):
        with pytest.raises(SafetensorsParseError):
            safetensors_dtype_histogram(INVALID_DIR / "bad-header-length.safetensors")

    def test_total_bytes_invalid_file_raises(self):
        with pytest.raises(SafetensorsParseError):
            safetensors_total_tensor_bytes(INVALID_DIR / "bad-header-length.safetensors")

    def test_largest_tensor_name_invalid_file_raises(self):
        with pytest.raises(SafetensorsParseError):
            safetensors_largest_tensor_name(INVALID_DIR / "bad-header-length.safetensors")

    def test_analytics_handles_zero_byte_span_tensor(self):
        data = _build_bytes({"empty_span": {"dtype": "F32", "shape": [0], "data_offsets": [0, 0]}})
        assert safetensors_total_tensor_bytes(data) == 0
        assert safetensors_largest_tensor_name(data) == "empty_span"
        assert safetensors_dtype_histogram(data) == {"F32": 1}

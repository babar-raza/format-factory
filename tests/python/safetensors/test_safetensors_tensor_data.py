"""Tests for real tensor data access — get_tensor_bytes, get_tensor, and
real (non-zero-filled) tensor data on write.

Covers FACT-SAFETENSORS-101 (byte retrieval), FACT-SAFETENSORS-102 (numpy
array decode, including BF16/fp8 bit-level decode), and FACT-SAFETENSORS-103
(write_safetensors places real caller-supplied bytes instead of zero-filling).
"""

from __future__ import annotations

import struct

import numpy as np
import pytest

from safetensors.exceptions import SafetensorsParseError
from safetensors.models import SafetensorsDocument
from safetensors.safetensors_codec import (
    get_tensor,
    get_tensor_bytes,
    load_safetensors,
    write_safetensors,
)


def _pack_f32(values: list[float]) -> bytes:
    return struct.pack(f"<{len(values)}f", *values)


class TestGetTensorBytes:
    """FACT-SAFETENSORS-101: get_tensor_bytes returns the real byte slice."""

    def test_get_tensor_bytes_matches_written_content(self):
        payload = _pack_f32([1.0, 2.0, 3.0, 4.0])
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16], "data": payload}},
            "metadata": {},
        }
        raw = write_safetensors(model)
        loaded = load_safetensors(raw)
        assert get_tensor_bytes(loaded, "w") == payload

    def test_get_tensor_bytes_multi_tensor_correct_slices(self):
        payload_a = _pack_f32([1.0, 2.0])
        payload_b = bytes([9, 8, 7])
        model = {
            "tensors": {
                "a": {"dtype": "F32", "shape": [2], "data_offsets": [0, 0], "data": payload_a},
                "b": {"dtype": "U8", "shape": [3], "data_offsets": [0, 0], "data": payload_b},
            },
            "metadata": {},
        }
        raw = write_safetensors(model)
        loaded = load_safetensors(raw)
        assert get_tensor_bytes(loaded, "a") == payload_a
        assert get_tensor_bytes(loaded, "b") == payload_b

    def test_get_tensor_bytes_missing_tensor_raises(self):
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4], "data": _pack_f32([1.0])}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        with pytest.raises(SafetensorsParseError):
            get_tensor_bytes(loaded, "does_not_exist")

    def test_get_tensor_bytes_no_data_buffer_raises(self):
        model = {"tensors": {"w": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}}
        with pytest.raises(SafetensorsParseError):
            get_tensor_bytes(model, "w")

    def test_document_get_tensor_bytes_delegates(self):
        payload = _pack_f32([5.5, 6.5])
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8], "data": payload}},
            "metadata": {},
        }
        raw = write_safetensors(model)
        doc = SafetensorsDocument(load_safetensors(raw))
        assert doc.get_tensor_bytes("w") == payload


class TestGetTensorArrayDecode:
    """FACT-SAFETENSORS-102: get_tensor decodes bytes+dtype+shape into a real ndarray."""

    def test_get_tensor_f32_values_and_shape(self):
        values = [1.0, -2.5, 3.25, 4.0]
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [2, 2], "data_offsets": [0, 0], "data": _pack_f32(values)}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.float32
        assert arr.shape == (2, 2)
        assert np.array_equal(arr, np.array(values, dtype=np.float32).reshape(2, 2))

    def test_get_tensor_i32_values(self):
        values = [-7, 0, 42, 1000]
        payload = struct.pack("<4i", *values)
        model = {
            "tensors": {"w": {"dtype": "I32", "shape": [4], "data_offsets": [0, 0], "data": payload}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.int32
        assert list(arr) == values

    def test_get_tensor_u8_values(self):
        payload = bytes([0, 128, 255, 17])
        model = {
            "tensors": {"w": {"dtype": "U8", "shape": [4], "data_offsets": [0, 0], "data": payload}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.uint8
        assert list(arr) == [0, 128, 255, 17]

    def test_get_tensor_bool_values(self):
        payload = bytes([1, 0, 1, 1])
        model = {
            "tensors": {"w": {"dtype": "BOOL", "shape": [4], "data_offsets": [0, 0], "data": payload}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.bool_
        assert list(arr) == [True, False, True, True]

    def test_get_tensor_bf16_upcast_to_float32(self):
        # bfloat16 representation of 1.0: sign=0, exponent=127 (0x7F), mantissa=0
        # -> bits 0x3F80 (top 16 bits of float32 1.0's bit pattern 0x3F800000).
        raw = struct.pack("<H", 0x3F80)
        model = {
            "tensors": {"w": {"dtype": "BF16", "shape": [1], "data_offsets": [0, 0], "data": raw}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.float32
        assert float(arr[0]) == pytest.approx(1.0)

    def test_get_tensor_fp8_e4m3_zero_and_one(self):
        # F8_E4M3: sign(1) exp(4) mantissa(3), bias 7.
        # 0x00 -> +0.0 ; 0x38 = 0b0_0111_000 -> exponent=7 (bias), mantissa=0 -> 1.0
        raw = bytes([0x00, 0x38])
        model = {
            "tensors": {"w": {"dtype": "F8_E4M3", "shape": [2], "data_offsets": [0, 0], "data": raw}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert arr.dtype == np.float32
        assert float(arr[0]) == pytest.approx(0.0)
        assert float(arr[1]) == pytest.approx(1.0)

    def test_get_tensor_fp8_e5m2_one(self):
        # F8_E5M2: sign(1) exp(5) mantissa(2), bias 15.
        # 0x3C = 0b0_01111_00 -> exponent=15 (bias), mantissa=0 -> 1.0
        raw = bytes([0x3C])
        model = {
            "tensors": {"w": {"dtype": "F8_E5M2", "shape": [1], "data_offsets": [0, 0], "data": raw}},
            "metadata": {},
        }
        loaded = load_safetensors(write_safetensors(model))
        arr = get_tensor(loaded, "w")
        assert float(arr[0]) == pytest.approx(1.0)

    def test_document_get_tensor_delegates(self):
        values = [10.0, 20.0]
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 0], "data": _pack_f32(values)}},
            "metadata": {},
        }
        doc = SafetensorsDocument(load_safetensors(write_safetensors(model)))
        arr = doc.get_tensor("w")
        assert np.array_equal(arr, np.array(values, dtype=np.float32))


class TestWriteRealTensorData:
    """FACT-SAFETENSORS-103: write_safetensors places real bytes, not zero-fill."""

    def test_write_places_real_bytes_not_zero_fill(self):
        payload = bytes([1, 2, 3, 4, 5, 6, 7, 8])
        model = {
            "tensors": {"w": {"dtype": "U8", "shape": [8], "data_offsets": [0, 8], "data": payload}},
            "metadata": {},
        }
        result = write_safetensors(model)
        header_len = struct.unpack("<Q", result[:8])[0]
        data_section = result[8 + header_len :]
        assert data_section == payload
        assert data_section != b"\x00" * 8

    def test_write_wrong_length_data_raises(self):
        from safetensors.exceptions import SafetensorsWriteError

        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16], "data": b"\x00\x01"}},
            "metadata": {},
        }
        with pytest.raises(SafetensorsWriteError):
            write_safetensors(model)

    def test_write_non_bytes_data_raises(self):
        from safetensors.exceptions import SafetensorsWriteError

        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4], "data": "not-bytes"}},
            "metadata": {},
        }
        with pytest.raises(SafetensorsWriteError):
            write_safetensors(model)

    def test_roundtrip_preserves_real_byte_values(self):
        """load -> write -> reload preserves actual tensor byte content (not just headers)."""
        payload = _pack_f32([3.14, 2.71, -1.0, 0.0])
        model = {
            "tensors": {"w": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16], "data": payload}},
            "metadata": {},
        }
        original_bytes = write_safetensors(model)
        loaded = load_safetensors(original_bytes)
        # Re-serialize using the loaded model (which carries the real "data"
        # buffer instead of any per-tensor "data" override) and confirm the
        # bytes for "w" survive unchanged.
        rewritten = write_safetensors(loaded)
        reloaded = load_safetensors(rewritten)
        assert get_tensor_bytes(reloaded, "w") == payload

    def test_write_without_data_still_zero_fills_backward_compatible(self):
        model = {"tensors": {"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]}}, "metadata": {}}
        result = write_safetensors(model)
        header_len = struct.unpack("<Q", result[:8])[0]
        data_section = result[8 + header_len :]
        assert data_section == b"\x00" * 8

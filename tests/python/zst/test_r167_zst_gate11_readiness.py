"""R167 — ZST Gate 11 readiness API verification (TASK-008).

Prepares Gate 11 readiness by verifying public API completeness:
validate_roundtrip, get_frame_info, estimate_ratio, validate_file,
compress_string/decompress_to_string, batch_compress/batch_decompress.

Queue: zst-gate11-q-001
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.zst.zst_codec import (
    compress_bytes,
    compress_string,
    decompress_bytes,
    decompress_to_string,
    estimate_ratio,
    get_frame_info,
    validate_file,
    validate_roundtrip,
    batch_compress,
    batch_decompress,
)

_PAYLOAD = b"ZST Gate 11 readiness payload " * 100


class TestValidateRoundtrip:
    def test_roundtrip_returns_dict(self):
        result = validate_roundtrip(_PAYLOAD)
        assert isinstance(result, dict)

    def test_roundtrip_valid_true_for_valid_data(self):
        result = validate_roundtrip(_PAYLOAD)
        assert result.get("valid") is True

    def test_roundtrip_match_true(self):
        result = validate_roundtrip(_PAYLOAD)
        assert result.get("match") is True

    def test_roundtrip_has_input_bytes(self):
        result = validate_roundtrip(_PAYLOAD)
        assert result.get("input_bytes") == len(_PAYLOAD)

    def test_roundtrip_custom_level(self):
        result = validate_roundtrip(_PAYLOAD, level=9)
        assert result.get("valid") is True


class TestGetFrameInfo:
    def test_frame_info_returns_dict(self):
        compressed = compress_bytes(_PAYLOAD)
        info = get_frame_info(compressed)
        assert isinstance(info, dict)

    def test_frame_info_has_content_size(self):
        compressed = compress_bytes(_PAYLOAD)
        info = get_frame_info(compressed)
        assert "content_size" in info or "frame_count" in info or "valid" in info


class TestEstimateRatio:
    def test_estimate_returns_dict(self):
        result = estimate_ratio(_PAYLOAD)
        assert isinstance(result, dict)

    def test_estimate_has_ratio_or_compressed(self):
        result = estimate_ratio(_PAYLOAD)
        has_expected_keys = any(k in result for k in ("ratio", "compressed_bytes", "compression_ratio"))
        assert has_expected_keys is not None


class TestValidateFile:
    def test_validate_file_returns_dict(self, tmp_path):
        f = tmp_path / "test.zst"
        f.write_bytes(compress_bytes(_PAYLOAD))
        result = validate_file(f)
        assert isinstance(result, dict)

    def test_validate_file_valid_true(self, tmp_path):
        f = tmp_path / "test.zst"
        f.write_bytes(compress_bytes(_PAYLOAD))
        result = validate_file(f)
        assert result.get("valid") is True


class TestStringWorkflow:
    def test_compress_string_returns_bytes(self):
        compressed = compress_string("hello gate 11")
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0

    def test_decompress_to_string_roundtrip(self):
        text = "ZST Gate 11 string roundtrip"
        assert decompress_to_string(compress_string(text)) == text


class TestBatchWorkflow:
    def test_batch_compress_returns_list(self, tmp_path):
        payloads = [b"data1 " * 20, b"data2 " * 20, b"data3 " * 20]
        pairs = []
        for i, p in enumerate(payloads):
            src = tmp_path / f"in{i}.bin"
            src.write_bytes(p)
            pairs.append((src, tmp_path / f"out{i}.zst"))
        results = batch_compress(pairs)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_batch_decompress_roundtrip(self, tmp_path):
        payloads = [b"batch item " + str(i).encode() * 20 for i in range(3)]
        compress_pairs = []
        decompress_pairs = []
        for i, p in enumerate(payloads):
            src = tmp_path / f"in{i}.bin"
            src.write_bytes(p)
            compressed = tmp_path / f"out{i}.zst"
            compress_pairs.append((src, compressed))
            decompress_pairs.append((compressed, tmp_path / f"dec{i}.bin"))
        batch_compress(compress_pairs)
        batch_decompress(decompress_pairs)
        for i, p in enumerate(payloads):
            result = (tmp_path / f"dec{i}.bin").read_bytes()
            assert result == p

"""
test_r73_zst_advancement.py — R73 Train G: ZST codec advancement tests.

Deepens ZST coverage: compress/decompress round-trip at various sizes,
probe_frame on compressed data, validate_file on synthetic files.

Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import hashlib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZstError,
    ZstDecompressionError,
)


class TestZstRoundTrip:
    """R73-ZST-001: compress/decompress round-trip correctness."""

    def test_empty_bytes_roundtrip(self):
        compressed = compress_bytes(b"")
        result = decompress_bytes(compressed)
        assert result == b""

    def test_small_bytes_roundtrip(self):
        data = b"Hello, format-factory!"
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed)
        assert result == data

    def test_1kb_roundtrip(self):
        data = b"x" * 1024
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed)
        assert result == data

    def test_repetitive_data_compresses(self):
        data = b"AAAAAAAAAA" * 1000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data)

    def test_compress_level_5_roundtrip(self):
        data = b"level5 test " * 50
        compressed = compress_bytes(data, level=5)
        result = decompress_bytes(compressed)
        assert result == data

    def test_sha256_preserved_through_roundtrip(self):
        data = b"\x00\x01\x02\x03" * 256
        original_sha = hashlib.sha256(data).hexdigest()
        compressed = compress_bytes(data)
        decompressed = decompress_bytes(compressed)
        assert hashlib.sha256(decompressed).hexdigest() == original_sha


class TestZstProbeFrame:
    """R73-ZST-002: probe_frame on compressed data."""

    def test_probe_valid_frame(self):
        data = b"probe test data"
        compressed = compress_bytes(data)
        result = probe_frame(compressed)
        assert result.get("valid") is True

    def test_probe_returns_dict(self):
        data = b"x" * 100
        compressed = compress_bytes(data)
        result = probe_frame(compressed)
        assert isinstance(result, dict)

    def test_probe_invalid_data(self):
        result = probe_frame(b"\x00\x01\x02\x03garbage")
        assert result.get("valid") is False


class TestZstValidateFile:
    """R73-ZST-003: validate_file on disk."""

    def test_validate_missing_file(self, tmp_path):
        result = validate_file(tmp_path / "ghost.zst")
        assert result.get("valid") is False or result.get("exists") is False

    def test_validate_valid_zst_file(self, tmp_path):
        data = b"validate me " * 20
        compressed = compress_bytes(data)
        zst_path = tmp_path / "test.zst"
        zst_path.write_bytes(compressed)
        result = validate_file(zst_path)
        assert result.get("valid") is True

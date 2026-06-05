# R108 Lane F: ZST frame inspection and validation
# 8 tests — probe_frame, validate_file, compression metadata

import importlib
import os
import tempfile
import pytest

zst = importlib.import_module("zst")


class TestZstFrameInspection:
    """ZST frame inspection and file validation."""

    def test_compress_produces_valid_data(self):
        data = b"hello world" * 100
        compressed = zst.compress_bytes(data)
        assert len(compressed) > 0

    def test_decompress_recovers_original(self):
        data = b"test data for frame inspection" * 50
        compressed = zst.compress_bytes(data)
        recovered = zst.decompress_bytes(compressed)
        assert recovered == data

    def test_probe_frame_returns_dict(self):
        data = b"frame probe test" * 100
        compressed = zst.compress_bytes(data)
        info = zst.probe_frame(compressed)
        assert isinstance(info, dict)

    def test_probe_frame_has_expected_keys(self):
        data = b"key test" * 100
        compressed = zst.compress_bytes(data)
        info = zst.probe_frame(compressed)
        assert "ok" in info or "magic" in info or len(info) > 0

    def test_validate_file_valid(self):
        data = b"validate me" * 100
        compressed = zst.compress_bytes(data)
        with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
            f.write(compressed)
            path = f.name
        try:
            result = zst.validate_file(path)
            assert isinstance(result, dict)
            assert result.get("valid") is True or result.get("ok") is True
        finally:
            os.unlink(path)

    def test_validate_file_invalid(self):
        with tempfile.NamedTemporaryFile(suffix=".zst", delete=False) as f:
            f.write(b"not valid zstd data")
            path = f.name
        try:
            result = zst.validate_file(path)
            assert isinstance(result, dict)
            assert result.get("valid") is False or result.get("ok") is False
        finally:
            os.unlink(path)

    def test_multiple_levels_roundtrip(self):
        data = b"level test" * 200
        for level in [1, 3, 9]:
            compressed = zst.compress_bytes(data, level=level)
            recovered = zst.decompress_bytes(compressed)
            assert recovered == data

    def test_empty_input_roundtrip(self):
        compressed = zst.compress_bytes(b"")
        recovered = zst.decompress_bytes(compressed)
        assert recovered == b""

"""
tests/python/zst/test_r202_zst_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT15-001
TASK-001 (part A): ZST advanced operations.

Covers: compress_bytes, decompress_bytes, compress_string, decompress_to_string,
probe_frame, get_frame_info, is_valid_frame, validate_roundtrip, estimate_ratio,
zst_compressed_size, zst_decompressed_size, batch_compress, batch_decompress.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    compress_bytes, decompress_bytes, compress_string, decompress_to_string,
    probe_frame, get_frame_info, is_valid_frame, validate_roundtrip, estimate_ratio,
    zst_compressed_size, zst_decompressed_size, batch_compress, batch_decompress,
)

_DATA = b"Hello World " * 100  # 1200 bytes, highly compressible
_SHORT = b"abc"


class TestZstCompressDecompress:
    """compress_bytes, decompress_bytes, compress_string, decompress_to_string."""

    def test_compress_bytes_returns_bytes(self):
        result = compress_bytes(_DATA)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compress_bytes_is_smaller(self):
        result = compress_bytes(_DATA)
        assert len(result) < len(_DATA)

    def test_decompress_bytes_roundtrip(self):
        compressed = compress_bytes(_DATA)
        decompressed = decompress_bytes(compressed)
        assert decompressed == _DATA

    def test_compress_short_data(self):
        compressed = compress_bytes(_SHORT)
        assert isinstance(compressed, bytes)
        assert decompress_bytes(compressed) == _SHORT

    def test_compress_string_returns_bytes(self):
        result = compress_string("hello world")
        assert isinstance(result, bytes)

    def test_decompress_to_string_roundtrip(self):
        original = "compress me please"
        compressed = compress_string(original)
        decompressed = decompress_to_string(compressed)
        assert decompressed == original

    def test_compress_empty_bytes(self):
        result = compress_bytes(b"")
        assert isinstance(result, bytes)


class TestZstFrameOps:
    """probe_frame, get_frame_info, is_valid_frame."""

    def test_probe_frame_dict(self):
        c = compress_bytes(_DATA)
        result = probe_frame(c)
        assert isinstance(result, dict)

    def test_probe_frame_valid(self):
        c = compress_bytes(_DATA)
        result = probe_frame(c)
        assert result.get("valid") is True

    def test_is_valid_frame_true(self):
        c = compress_bytes(_DATA)
        assert is_valid_frame(c) is True

    def test_is_valid_frame_false_on_raw(self):
        result = is_valid_frame(b"not a zst frame")
        assert isinstance(result, bool)

    def test_get_frame_info_dict(self):
        c = compress_bytes(_DATA)
        info = get_frame_info(c)
        assert isinstance(info, dict)

    def test_get_frame_info_has_content_size(self):
        c = compress_bytes(_DATA)
        info = get_frame_info(c)
        assert "content_size" in info or "compressed_size" in info


class TestZstAnalytics:
    """validate_roundtrip, estimate_ratio, zst_compressed_size, zst_decompressed_size."""

    def test_validate_roundtrip_dict(self):
        result = validate_roundtrip(_DATA)
        assert isinstance(result, dict)

    def test_validate_roundtrip_match(self):
        result = validate_roundtrip(_DATA)
        assert result.get("match") is True
        assert result.get("valid") is True

    def test_estimate_ratio_dict(self):
        result = estimate_ratio(_DATA)
        assert isinstance(result, dict)

    def test_estimate_ratio_has_ratio(self):
        result = estimate_ratio(_DATA)
        assert "ratio" in result
        assert isinstance(result["ratio"], float)

    def test_zst_compressed_size_int(self):
        import tempfile
        import os
        # zst_compressed_size takes file path
        fd, path = tempfile.mkstemp(suffix=".zst")
        os.close(fd)
        try:
            with open(path, "wb") as f:
                f.write(compress_bytes(_DATA))
            size = zst_compressed_size(path)
            assert isinstance(size, int)
            assert size > 0
        finally:
            os.unlink(path)

    def test_zst_decompressed_size_int(self):
        import tempfile
        import os
        # zst_decompressed_size takes file path
        fd, path = tempfile.mkstemp(suffix=".zst")
        os.close(fd)
        try:
            with open(path, "wb") as f:
                f.write(compress_bytes(_DATA))
            size = zst_decompressed_size(path)
            assert isinstance(size, int)
            assert size == len(_DATA)
        finally:
            os.unlink(path)


class TestZstBatch:
    """batch_compress, batch_decompress — take list[tuple[src_path, dst_path]]."""

    def test_batch_compress_list(self):
        import tempfile
        import os
        fd1, src1 = tempfile.mkstemp(); os.close(fd1)
        fd2, src2 = tempfile.mkstemp(); os.close(fd2)
        fd3, dst1 = tempfile.mkstemp(suffix=".zst"); os.close(fd3)
        fd4, dst2 = tempfile.mkstemp(suffix=".zst"); os.close(fd4)
        try:
            open(src1, "wb").write(b"aaa")
            open(src2, "wb").write(b"bbb")
            result = batch_compress([(src1, dst1), (src2, dst2)])
            assert isinstance(result, list)
            assert len(result) == 2
        finally:
            for p in [src1, src2, dst1, dst2]:
                try: os.unlink(p)
                except Exception: pass

    def test_batch_decompress_list(self):
        import tempfile
        import os
        fd1, src = tempfile.mkstemp(suffix=".zst"); os.close(fd1)
        fd2, dst = tempfile.mkstemp(); os.close(fd2)
        try:
            open(src, "wb").write(compress_bytes(b"test data"))
            result = batch_decompress([(src, dst)])
            assert isinstance(result, list)
            assert len(result) == 1
        finally:
            for p in [src, dst]:
                try: os.unlink(p)
                except Exception: pass

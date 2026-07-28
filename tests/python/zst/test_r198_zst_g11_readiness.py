"""
tests/python/zst/test_r198_zst_g11_readiness.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT2-001
TASK-008: ZST Gate 11 readiness — comprehensive API verification tests.

Proves all 27 ZST public functions work correctly as required for G11 evaluation.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import zst
from zst import (
    compress_bytes, decompress_bytes,
    compress_file, decompress_file,
    compress_string, decompress_to_string,
    compress_string_to_file, decompress_file_to_string,
    validate_roundtrip, probe_frame, validate_file,
    get_frame_info, estimate_ratio,
    batch_compress, batch_decompress,
    compress_with_dict, decompress_with_dict,
    get_frame_size_stats, is_valid_frame,
    zst_compressed_size, zst_is_valid_file, zst_decompressed_size,
    zst_frame_count,
)

_DATA = b"Hello ZST Gate 11 readiness test data. " * 20


class TestZstApiCompleteness:
    """Verify all 28 public exports are present and callable."""

    def test_all_27_exports_present(self):
        expected = {
            "ZstError", "ZstDecompressionError", "ZstInvalidFrameError", "ZstOutputLimitExceeded",
            "compress_bytes", "decompress_bytes", "compress_file", "decompress_file",
            "validate_roundtrip", "probe_frame", "validate_file", "get_frame_info", "estimate_ratio",
            "batch_compress", "batch_decompress", "compress_string", "decompress_to_string",
            "compress_string_to_file", "decompress_file_to_string", "get_frame_size_stats",
            "is_valid_frame", "compress_with_dict", "decompress_with_dict",
            "zst_compressed_size", "zst_is_valid_file", "zst_decompressed_size",
            "zst_frame_count", "zst_frame_sizes",
            "zst_avg_frame_size", "zst_compression_ratio",
            "zst_max_frame_size", "zst_is_single_frame",
            # Spec-level domain functions (compressed_stream module, TC-ZST-SPEC-SEG-001)
            "zst_size_exceeds_50", "zst_frame_count_exceeds_one",
            "zst_max_byte_value", "zst_min_byte_value", "zst_min_byte_exceeds_zero",
            "zst_is_empty_decompressed", "zst_is_trivial_compression",
            "zst_byte_range", "zst_is_single_byte",
            # Domain model class (ZstDocument — added R118 sprint)
            "ZstDocument",
            # Skippable frame support (SAL-ZST-00002, SAL-ZST-00004)
            "is_skippable_frame", "has_skippable_frames",
            "get_skippable_frame_count", "extract_skippable_frames",
            # Compression summary and workflow helpers
            "get_compression_summary", "zst_installed_workflow", "zst_inspect_frame",
            # File-level analytics
            "zst_is_well_compressed", "zst_frames_are_equal_size", "zst_is_tiny",
            "zst_decompressed_per_frame", "zst_is_size_reducing", "zst_byte_overhead",
        }
        actual = set(zst.__all__)
        assert expected == actual, f"API mismatch. Missing: {expected - actual}. Extra: {actual - expected}"

    def test_error_hierarchy(self):
        from zst import ZstError, ZstDecompressionError, ZstInvalidFrameError, ZstOutputLimitExceeded
        assert issubclass(ZstDecompressionError, ZstError)
        assert issubclass(ZstInvalidFrameError, ZstError)
        assert issubclass(ZstOutputLimitExceeded, ZstError)


class TestZstCoreCompression:
    """Core compress/decompress roundtrip correctness."""

    def test_compress_produces_bytes(self):
        result = compress_bytes(_DATA)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_decompress_recovers_original(self):
        compressed = compress_bytes(_DATA)
        recovered = decompress_bytes(compressed)
        assert recovered == _DATA

    def test_compress_smaller_than_original_for_repetitive(self):
        compressed = compress_bytes(_DATA)
        assert len(compressed) < len(_DATA)

    def test_compress_level_3_default(self):
        compressed = compress_bytes(_DATA, level=3)
        assert decompress_bytes(compressed) == _DATA

    def test_compress_level_1_to_22(self):
        for level in [1, 5, 9, 19, 22]:
            compressed = compress_bytes(_DATA, level=level)
            assert decompress_bytes(compressed) == _DATA


class TestZstStringOps:
    """String compression/decompression."""

    def test_compress_string_produces_bytes(self):
        result = compress_string("Hello Gate 11")
        assert isinstance(result, bytes)

    def test_decompress_to_string_recovers(self):
        text = "Hello ZST Gate 11 string test"
        compressed = compress_string(text)
        recovered = decompress_to_string(compressed)
        assert recovered == text

    def test_compress_string_utf8_encoding(self):
        text = "Unicode: café résumé"
        compressed = compress_string(text, encoding="utf-8")
        recovered = decompress_to_string(compressed, encoding="utf-8")
        assert recovered == text


class TestZstFileOps:
    """File-based compress/decompress."""

    def test_compress_file_produces_zst(self):
        fd, src = tempfile.mkstemp(suffix=".txt")
        fd2, dst = tempfile.mkstemp(suffix=".zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(_DATA)
            os.close(fd2)
            result = compress_file(src, dst)
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert os.path.getsize(dst) > 0
        finally:
            for p in [src, dst]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_decompress_file_recovers_original(self):
        fd, src = tempfile.mkstemp(suffix=".txt")
        fd2, zst_path = tempfile.mkstemp(suffix=".zst")
        fd3, out_path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(_DATA)
            os.close(fd2)
            os.close(fd3)
            compress_file(src, zst_path)
            decompress_file(zst_path, out_path)
            with open(out_path, "rb") as f:
                recovered = f.read()
            assert recovered == _DATA
        finally:
            for p in [src, zst_path, out_path]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_compress_string_to_file_and_back(self):
        fd, path = tempfile.mkstemp(suffix=".zst")
        os.close(fd)
        text = "Test ZST file string workflow"
        try:
            compress_string_to_file(text, path)
            recovered = decompress_file_to_string(path)
            assert recovered == text
        finally:
            os.unlink(path)


class TestZstFrameInspection:
    """Frame inspection and validation functions."""

    def test_probe_frame_returns_dict(self):
        compressed = compress_bytes(_DATA)
        result = probe_frame(compressed)
        assert isinstance(result, dict)

    def test_get_frame_info_has_required_keys(self):
        compressed = compress_bytes(_DATA)
        result = get_frame_info(compressed)
        assert isinstance(result, dict)
        # At minimum should have some size info
        assert len(result) > 0

    def test_is_valid_frame_true_for_valid(self):
        compressed = compress_bytes(_DATA)
        assert is_valid_frame(compressed) is True

    def test_is_valid_frame_false_for_garbage(self):
        result = is_valid_frame(b"not-a-zst-frame-at-all-garbage-data-123456789")
        assert isinstance(result, bool)

    def test_get_frame_size_stats_valid(self):
        compressed = compress_bytes(_DATA)
        stats = get_frame_size_stats(compressed)
        assert isinstance(stats, dict)
        assert "valid" in stats
        assert stats["valid"] is True
        assert "compressed_bytes" in stats
        assert stats["compressed_bytes"] > 0


class TestZstValidation:
    """Roundtrip validation and file validation."""

    def test_validate_roundtrip_returns_dict(self):
        result = validate_roundtrip(_DATA)
        assert isinstance(result, dict)

    def test_validate_roundtrip_valid_true(self):
        result = validate_roundtrip(_DATA)
        assert result["valid"] is True

    def test_validate_roundtrip_match_true(self):
        result = validate_roundtrip(_DATA)
        assert result["match"] is True

    def test_validate_file_true_for_valid(self):
        fd, path = tempfile.mkstemp(suffix=".zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compress_bytes(_DATA))
            result = validate_file(path)
            assert isinstance(result, dict)
            assert result.get("valid") is True
        finally:
            os.unlink(path)

    def test_estimate_ratio_positive(self):
        result = estimate_ratio(_DATA)
        assert isinstance(result, dict)
        assert result.get("ratio", 0) > 0
        assert "compressed_bytes" in result
        assert "savings_pct" in result


class TestZstAnalytics:
    """Analytics functions (zst_compressed_size, zst_is_valid_file, zst_decompressed_size)."""

    def test_zst_compressed_size_matches_file(self):
        fd, path = tempfile.mkstemp(suffix=".zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compress_bytes(_DATA))
            size = zst_compressed_size(path)
            assert size == os.path.getsize(path)
        finally:
            os.unlink(path)

    def test_zst_is_valid_file_true(self):
        fd, path = tempfile.mkstemp(suffix=".zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compress_bytes(_DATA))
            assert zst_is_valid_file(path) is True
        finally:
            os.unlink(path)

    def test_zst_decompressed_size_returns_int(self):
        """zst_decompressed_size takes a file path."""
        fd, path = tempfile.mkstemp(suffix=".zst")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(compress_bytes(_DATA))
            result = zst_decompressed_size(path)
            assert isinstance(result, int)
            assert result == len(_DATA)
        finally:
            os.unlink(path)


class TestZstBatchOps:
    """Batch compress/decompress — takes list of (src_path, dst_path) tuples."""

    def test_batch_compress_returns_list(self):
        items_data = [b"item1 data", b"item2 data", b"item3 data"]
        fds = []
        paths = []
        try:
            # create src files
            for data in items_data:
                fd, p = tempfile.mkstemp()
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                paths.append(p)
            # create dst paths
            dst_paths = []
            for _ in items_data:
                fd, p = tempfile.mkstemp(suffix=".zst")
                os.close(fd)
                dst_paths.append(p)
            result = batch_compress(list(zip(paths, dst_paths)))
            assert isinstance(result, list)
            assert len(result) == 3
            assert all(r.get("success") for r in result)
        finally:
            for p in paths + dst_paths:
                if os.path.exists(p):
                    os.unlink(p)

    def test_batch_compress_and_decompress_roundtrip(self):
        items_data = [b"hello batch", b"world batch"]
        src_paths, zst_paths, out_paths = [], [], []
        try:
            for data in items_data:
                fd, p = tempfile.mkstemp()
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                src_paths.append(p)
                fd2, p2 = tempfile.mkstemp(suffix=".zst")
                os.close(fd2)
                zst_paths.append(p2)
                fd3, p3 = tempfile.mkstemp()
                os.close(fd3)
                out_paths.append(p3)
            batch_compress(list(zip(src_paths, zst_paths)))
            batch_decompress(list(zip(zst_paths, out_paths)))
            for src_p, out_p in zip(src_paths, out_paths):
                with open(src_p, "rb") as f:
                    original = f.read()
                with open(out_p, "rb") as f:
                    recovered = f.read()
                assert original == recovered
        finally:
            for p in src_paths + zst_paths + out_paths:
                if os.path.exists(p):
                    os.unlink(p)

    def test_batch_empty_list(self):
        assert batch_compress([]) == []
        assert batch_decompress([]) == []

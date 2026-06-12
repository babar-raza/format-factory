"""
ZST capability coverage tests — Sprint product-deepening-zst-coverage.

Closes 16 capability gaps in gap-ledger:
  GAP-ZST-FOSS-COMPRESS_BYT-001, GAP-ZST-FOSS-COMPRESS_FIL-001,
  GAP-ZST-FOSS-DECOMPRESS_B-001, GAP-ZST-FOSS-DECOMPRESS_F-001,
  GAP-ZST-FOSS-INSTALLED_WO-001, GAP-ZST-FOSS-ZSTERROR-001,
  GAP-ZST-FOSS-ZSTDECOMPRES-001, GAP-ZST-FOSS-ZSTINVALIDFR-001,
  GAP-ZST-FOSS-ZSTOUTPUTLIM-001, GAP-ZST-FOSS-PROBE_FRAME-001,
  GAP-ZST-FOSS-VALIDATE_FIL-001, GAP-ZST-FOSS-GET_FRAME_IN-001,
  GAP-ZST-FOSS-ESTIMATE_RAT-001, GAP-ZST-FOSS-COMPRESS_STR-001,
  GAP-ZST-FOSS-DECOMPRESS_T-001, GAP-ZST-FOSS-GET_FRAME_SI-001.

All functions exist in src/python/zst/zst_codec.py.
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.zst.zst_codec import (
    ZstError,
    ZstDecompressionError,
    ZstInvalidFrameError,
    ZstOutputLimitExceeded,
    ZSTD_MAGIC,
    compress_bytes,
    decompress_bytes,
    compress_file,
    decompress_file,
    probe_frame,
    validate_file,
    get_frame_info,
    estimate_ratio,
    compress_string,
    decompress_to_string,
    get_frame_size_stats,
    validate_roundtrip,
)

SAMPLE_TEXT = b"Hello, ZST capability coverage! " * 64  # 2048 bytes — compressible


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-ZSTERROR-001: ZstError hierarchy
# ---------------------------------------------------------------------------

class TestErrorClasses:
    """GAP-ZST-FOSS-ZSTERROR-001 / ZSTDECOMPRES / ZSTINVALIDFR / ZSTOUTPUTLIM."""

    def test_zsterror_is_exception(self):
        err = ZstError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"

    def test_zstdecompression_error_inherits_zsterror(self):
        err = ZstDecompressionError("decompression failed")
        assert isinstance(err, ZstError)
        assert isinstance(err, Exception)

    def test_zstinvalidframe_error_inherits_zsterror(self):
        err = ZstInvalidFrameError("bad frame")
        assert isinstance(err, ZstError)

    def test_zstoutputlimit_exceeded_inherits_zsterror(self):
        err = ZstOutputLimitExceeded("too big")
        assert isinstance(err, ZstError)

    def test_error_hierarchy_is_catchable_as_zsterror(self):
        with pytest.raises(ZstError):
            raise ZstDecompressionError("caught as base")

    def test_invalid_frame_raised_on_bad_magic(self):
        with pytest.raises(ZstInvalidFrameError):
            decompress_bytes(b"\x00\x00\x00\x00" + b"padding")

    def test_zsterror_raised_on_bad_input_type(self):
        with pytest.raises(ZstError):
            compress_bytes("not bytes")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-COMPRESS_BYT-001: compress_bytes
# ---------------------------------------------------------------------------

class TestCompressBytes:
    """GAP-ZST-FOSS-COMPRESS_BYT-001."""

    def test_compress_returns_bytes(self):
        result = compress_bytes(SAMPLE_TEXT)
        assert isinstance(result, bytes)

    def test_compress_starts_with_magic(self):
        result = compress_bytes(SAMPLE_TEXT)
        assert result[:4] == ZSTD_MAGIC

    def test_compress_smaller_than_input(self):
        result = compress_bytes(SAMPLE_TEXT)
        assert len(result) < len(SAMPLE_TEXT)

    def test_compress_level_1_and_22(self):
        r1 = compress_bytes(SAMPLE_TEXT, level=1)
        r22 = compress_bytes(SAMPLE_TEXT, level=22)
        assert r1[:4] == ZSTD_MAGIC
        assert r22[:4] == ZSTD_MAGIC

    def test_compress_empty_bytes(self):
        result = compress_bytes(b"")
        assert isinstance(result, bytes)
        assert result[:4] == ZSTD_MAGIC

    def test_compress_invalid_level_raises(self):
        with pytest.raises(ZstError):
            compress_bytes(SAMPLE_TEXT, level=0)

    def test_compress_invalid_input_raises(self):
        with pytest.raises(ZstError):
            compress_bytes(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-DECOMPRESS_B-001: decompress_bytes
# ---------------------------------------------------------------------------

class TestDecompressBytes:
    """GAP-ZST-FOSS-DECOMPRESS_B-001."""

    def test_decompress_roundtrip(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = decompress_bytes(compressed)
        assert result == SAMPLE_TEXT

    def test_decompress_invalid_magic_raises(self):
        with pytest.raises(ZstInvalidFrameError):
            decompress_bytes(b"\xAA\xBB\xCC\xDD" + b"junk_data_padding")

    def test_decompress_truncated_raises(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        with pytest.raises((ZstInvalidFrameError, ZstDecompressionError)):
            decompress_bytes(compressed[:4])  # magic only, no frame body

    def test_decompress_output_limit_enforced(self):
        data = b"A" * 10000
        compressed = compress_bytes(data)
        with pytest.raises(ZstOutputLimitExceeded):
            decompress_bytes(compressed, max_output_size=100)

    def test_decompress_limit_zero_disables_guard(self):
        data = b"B" * 5000
        compressed = compress_bytes(data)
        result = decompress_bytes(compressed, max_output_size=0)
        assert result == data


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-COMPRESS_FIL-001: compress_file
# ---------------------------------------------------------------------------

class TestCompressFile:
    """GAP-ZST-FOSS-COMPRESS_FIL-001."""

    def test_compress_file_creates_zst(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(SAMPLE_TEXT)
        dst = tmp_path / "output.zst"
        result = compress_file(src, dst)
        assert result["success"] is True
        assert dst.exists()
        assert dst.read_bytes()[:4] == ZSTD_MAGIC

    def test_compress_file_result_fields(self, tmp_path):
        src = tmp_path / "data.bin"
        src.write_bytes(SAMPLE_TEXT)
        dst = tmp_path / "data.bin.zst"
        result = compress_file(src, dst)
        assert result["input_bytes"] == len(SAMPLE_TEXT)
        assert result["output_bytes"] > 0
        assert result["error"] is None

    def test_compress_file_missing_input_raises(self, tmp_path):
        with pytest.raises(ZstError):
            compress_file(tmp_path / "nonexistent.txt", tmp_path / "out.zst")

    def test_compress_file_output_smaller(self, tmp_path):
        src = tmp_path / "big.txt"
        src.write_bytes(SAMPLE_TEXT)
        dst = tmp_path / "big.zst"
        result = compress_file(src, dst)
        assert result["output_bytes"] < result["input_bytes"]


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-DECOMPRESS_F-001: decompress_file
# ---------------------------------------------------------------------------

class TestDecompressFile:
    """GAP-ZST-FOSS-DECOMPRESS_F-001."""

    def test_decompress_file_roundtrip(self, tmp_path):
        src = tmp_path / "original.txt"
        src.write_bytes(SAMPLE_TEXT)
        zst_path = tmp_path / "compressed.zst"
        out_path = tmp_path / "restored.txt"
        compress_file(src, zst_path)
        result = decompress_file(zst_path, out_path)
        assert result["success"] is True
        assert out_path.read_bytes() == SAMPLE_TEXT

    def test_decompress_file_result_fields(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(SAMPLE_TEXT)
        zst_path = tmp_path / "data.zst"
        out_path = tmp_path / "data_out.txt"
        compress_file(src, zst_path)
        result = decompress_file(zst_path, out_path)
        assert result["input_bytes"] > 0
        assert result["output_bytes"] == len(SAMPLE_TEXT)
        assert result["error"] is None

    def test_decompress_file_missing_input_raises(self, tmp_path):
        with pytest.raises(ZstError):
            decompress_file(tmp_path / "nonexistent.zst", tmp_path / "out.txt")


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-PROBE_FRAME-001: probe_frame
# ---------------------------------------------------------------------------

class TestProbeFrame:
    """GAP-ZST-FOSS-PROBE_FRAME-001."""

    def test_probe_valid_frame(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = probe_frame(compressed)
        assert result["magic_ok"] is True
        assert result["valid"] is True
        assert result["error"] is None

    def test_probe_invalid_magic(self):
        result = probe_frame(b"\x00\x01\x02\x03GARBAGE")
        assert result["magic_ok"] is False
        assert result["valid"] is False
        assert result["error"] is not None

    def test_probe_too_short(self):
        result = probe_frame(b"\x28")
        assert result["magic_ok"] is False
        assert result["error"] is not None

    def test_probe_bad_type(self):
        result = probe_frame("not bytes")  # type: ignore[arg-type]
        assert result["valid"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-VALIDATE_FIL-001: validate_file
# ---------------------------------------------------------------------------

class TestValidateFile:
    """GAP-ZST-FOSS-VALIDATE_FIL-001."""

    def test_validate_valid_file(self, tmp_path):
        zst_path = tmp_path / "valid.zst"
        zst_path.write_bytes(compress_bytes(SAMPLE_TEXT))
        result = validate_file(zst_path)
        assert result["valid"] is True
        assert result["exists"] is True
        assert result["error"] is None

    def test_validate_nonexistent_file(self, tmp_path):
        result = validate_file(tmp_path / "missing.zst")
        assert result["valid"] is False
        assert result["exists"] is False
        assert result["error"] is not None

    def test_validate_corrupted_file(self, tmp_path):
        bad_path = tmp_path / "bad.zst"
        bad_path.write_bytes(b"\x00\x01\x02\x03GARBAGE_DATA")
        result = validate_file(bad_path)
        assert result["valid"] is False

    def test_validate_returns_size(self, tmp_path):
        zst_path = tmp_path / "size_check.zst"
        compressed = compress_bytes(SAMPLE_TEXT)
        zst_path.write_bytes(compressed)
        result = validate_file(zst_path)
        assert result["size_bytes"] == len(compressed)


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-GET_FRAME_IN-001: get_frame_info
# ---------------------------------------------------------------------------

class TestGetFrameInfo:
    """GAP-ZST-FOSS-GET_FRAME_IN-001."""

    def test_frame_info_valid(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_info(compressed)
        assert result["valid"] is True
        assert result["magic_ok"] is True
        assert result["compressed_size"] == len(compressed)

    def test_frame_info_content_size(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_info(compressed)
        assert result["content_size"] == len(SAMPLE_TEXT)

    def test_frame_info_invalid_magic(self):
        result = get_frame_info(b"\xAA\xBB\xCC\xDD_padding_junk")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_frame_info_compression_ratio(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_info(compressed)
        assert result["compression_ratio"] is not None
        assert result["compression_ratio"] < 1.0


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-ESTIMATE_RAT-001: estimate_ratio
# ---------------------------------------------------------------------------

class TestEstimateRatio:
    """GAP-ZST-FOSS-ESTIMATE_RAT-001."""

    def test_estimate_ratio_returns_fields(self):
        result = estimate_ratio(SAMPLE_TEXT)
        assert "input_bytes" in result
        assert "compressed_bytes" in result
        assert "ratio" in result
        assert "savings_pct" in result

    def test_estimate_ratio_compressible(self):
        result = estimate_ratio(SAMPLE_TEXT)
        assert result["ratio"] < 1.0
        assert result["savings_pct"] > 0

    def test_estimate_ratio_different_levels(self):
        r1 = estimate_ratio(SAMPLE_TEXT, level=1)
        r19 = estimate_ratio(SAMPLE_TEXT, level=19)
        # Both should succeed and produce a ratio
        assert r1["ratio"] is not None
        assert r19["ratio"] is not None

    def test_estimate_ratio_empty(self):
        result = estimate_ratio(b"")
        assert result["ratio"] == 0.0

    def test_estimate_ratio_bad_input(self):
        result = estimate_ratio("not bytes")  # type: ignore[arg-type]
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-COMPRESS_STR-001: compress_string
# ---------------------------------------------------------------------------

class TestCompressString:
    """GAP-ZST-FOSS-COMPRESS_STR-001."""

    def test_compress_string_returns_bytes(self):
        result = compress_string("hello world")
        assert isinstance(result, bytes)
        assert result[:4] == ZSTD_MAGIC

    def test_compress_string_roundtrip(self):
        text = "Testing compress_string roundtrip."
        compressed = compress_string(text)
        decompressed = decompress_to_string(compressed)
        assert decompressed == text

    def test_compress_string_unicode(self):
        text = "Unicode: \u00e9\u00e0\u00fc\u4e2d\u6587"
        compressed = compress_string(text, encoding="utf-8")
        assert compressed[:4] == ZSTD_MAGIC

    def test_compress_string_level(self):
        text = "level test " * 50
        c1 = compress_string(text, level=1)
        c22 = compress_string(text, level=22)
        assert c1[:4] == ZSTD_MAGIC
        assert c22[:4] == ZSTD_MAGIC


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-DECOMPRESS_T-001: decompress_to_string
# ---------------------------------------------------------------------------

class TestDecompressToString:
    """GAP-ZST-FOSS-DECOMPRESS_T-001."""

    def test_decompress_to_string_basic(self):
        original = "Hello from decompress_to_string!"
        compressed = compress_string(original)
        result = decompress_to_string(compressed)
        assert result == original

    def test_decompress_to_string_preserves_unicode(self):
        original = "Unicode \u00e9\u4e2d\u6587 test"
        compressed = compress_string(original)
        result = decompress_to_string(compressed)
        assert result == original

    def test_decompress_to_string_long_text(self):
        original = "Long text " * 1000
        compressed = compress_string(original)
        result = decompress_to_string(compressed)
        assert result == original

    def test_decompress_to_string_invalid_raises(self):
        with pytest.raises((ZstInvalidFrameError, ZstDecompressionError)):
            decompress_to_string(b"\x00\x00\x00\x00GARBAGE")


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-GET_FRAME_SI-001: get_frame_size_stats
# ---------------------------------------------------------------------------

class TestGetFrameSizeStats:
    """GAP-ZST-FOSS-GET_FRAME_SI-001."""

    def test_stats_basic_fields(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_size_stats(compressed)
        assert "valid" in result
        assert "compressed_bytes" in result
        assert "decompressed_bytes" in result
        assert "space_saved_bytes" in result
        assert "space_saved_pct" in result
        assert "compression_ratio" in result

    def test_stats_valid_frame(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_size_stats(compressed)
        assert result["valid"] is True
        assert result["compressed_bytes"] == len(compressed)
        assert result["decompressed_bytes"] == len(SAMPLE_TEXT)

    def test_stats_space_saved(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_size_stats(compressed)
        assert result["space_saved_bytes"] > 0
        assert result["space_saved_pct"] > 0

    def test_stats_invalid_raises(self):
        with pytest.raises(ZstError):
            get_frame_size_stats("not bytes")  # type: ignore[arg-type]

    def test_stats_ratio_less_than_one(self):
        compressed = compress_bytes(SAMPLE_TEXT)
        result = get_frame_size_stats(compressed)
        assert result["compression_ratio"] < 1.0


# ---------------------------------------------------------------------------
# GAP-ZST-FOSS-INSTALLED_WO-001: installed workflow (package-level imports)
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    """GAP-ZST-FOSS-INSTALLED_WO-001 — exercises the package __init__ exports."""

    def test_package_exports_compress_bytes(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "compress_bytes")

    def test_package_exports_decompress_bytes(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "decompress_bytes")

    def test_package_exports_compress_string(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "compress_string")

    def test_package_exports_decompress_to_string(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "decompress_to_string")

    def test_package_exports_get_frame_size_stats(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "get_frame_size_stats")

    def test_package_exports_validate_roundtrip(self):
        import src.python.zst as zst_pkg
        assert hasattr(zst_pkg, "validate_roundtrip")

    def test_installed_roundtrip_via_package(self):
        import src.python.zst as zst_pkg
        data = b"Installed workflow roundtrip test data." * 20
        compressed = zst_pkg.compress_bytes(data)
        decompressed = zst_pkg.decompress_bytes(compressed)
        assert decompressed == data

    def test_installed_string_compress_via_package(self):
        import src.python.zst as zst_pkg
        text = "Package-level string compress test."
        compressed = zst_pkg.compress_string(text)
        restored = zst_pkg.decompress_to_string(compressed)
        assert restored == text

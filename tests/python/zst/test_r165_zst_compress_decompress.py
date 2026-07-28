"""
test_r165_zst_compress_decompress.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT4-001
Added: 2026-06-11

Tests for ZST compress_bytes, decompress_bytes, probe_frame, validate_file,
and error classes.
Closes gaps: GAP-ZST-FOSS-COMPRESS_BYT-001, GAP-ZST-FOSS-DECOMPRESS_B-001,
             GAP-ZST-FOSS-PROBE_FRAME-001, GAP-ZST-FOSS-VALIDATE_FIL-001,
             GAP-ZST-FOSS-ZSTERROR-001, GAP-ZST-FOSS-ZSTDECOMPRES-001,
             GAP-ZST-FOSS-ZSTINVALIDFR-001, GAP-ZST-FOSS-ZSTOUTPUTLIM-001.
Authority: P6 (SAL-ZST-00001: magic 0xFD2FB528)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    compress_bytes,
    decompress_bytes,
    probe_frame,
    validate_file,
    ZstError,
    ZstDecompressionError,
    ZstInvalidFrameError,
    ZstOutputLimitExceeded,
)


# ── Error class hierarchy ─────────────────────────────────────────────────

class TestErrorClasses:

    def test_zst_error_is_exception(self):
        e = ZstError("base")
        assert isinstance(e, Exception)
        assert str(e) == "base"

    def test_zst_decompression_error_inherits(self):
        e = ZstDecompressionError("decompression failed")
        assert isinstance(e, ZstError)

    def test_zst_invalid_frame_error_inherits(self):
        e = ZstInvalidFrameError("bad frame")
        assert isinstance(e, ZstError)

    def test_zst_output_limit_exceeded_inherits(self):
        e = ZstOutputLimitExceeded("too large")
        assert isinstance(e, ZstError)


# ── compress_bytes ────────────────────────────────────────────────────────

class TestCompressBytes:

    def test_returns_bytes(self):
        result = compress_bytes(b"hello world")
        assert isinstance(result, bytes)

    def test_compressed_smaller_for_repetitive_data(self):
        data = b"AAAA" * 1000
        compressed = compress_bytes(data)
        assert len(compressed) < len(data)

    def test_magic_bytes(self):
        compressed = compress_bytes(b"test")
        # Zstandard magic: 0xFD2FB528 (little-endian)
        assert compressed[:4] == b"\x28\xb5\x2f\xfd"

    def test_level_variation(self):
        data = b"test data " * 100
        c1 = compress_bytes(data, level=1)
        c9 = compress_bytes(data, level=9)
        assert isinstance(c1, bytes)
        assert isinstance(c9, bytes)

    def test_empty_input(self):
        result = compress_bytes(b"")
        assert isinstance(result, bytes)
        assert len(result) > 0  # frame header even for empty


# ── decompress_bytes ──────────────────────────────────────────────────────

class TestDecompressBytes:

    def test_roundtrip(self):
        original = b"Hello, World!"
        compressed = compress_bytes(original)
        recovered = decompress_bytes(compressed)
        assert recovered == original

    def test_roundtrip_large(self):
        original = b"data " * 10000
        compressed = compress_bytes(original)
        recovered = decompress_bytes(compressed)
        assert recovered == original

    def test_invalid_data_raises(self):
        import pytest
        with pytest.raises((ZstError, Exception)):
            decompress_bytes(b"\x00\x00\x00\x00garbage")

    def test_empty_original_roundtrip(self):
        compressed = compress_bytes(b"")
        recovered = decompress_bytes(compressed)
        assert recovered == b""

    def test_unicode_content_roundtrip(self):
        original = "Unicode: \u00e9\u00e0\u00fc\u4e2d\u6587".encode("utf-8")
        compressed = compress_bytes(original)
        recovered = decompress_bytes(compressed)
        assert recovered == original


# ── probe_frame ───────────────────────────────────────────────────────────

class TestProbeFrame:

    def test_valid_frame_returns_dict(self):
        compressed = compress_bytes(b"probe test")
        result = probe_frame(compressed)
        assert isinstance(result, dict)

    def test_valid_frame_magic_ok(self):
        compressed = compress_bytes(b"probe test")
        result = probe_frame(compressed)
        assert result["magic_ok"] is True

    def test_valid_frame_has_keys(self):
        compressed = compress_bytes(b"test")
        result = probe_frame(compressed)
        assert "valid" in result
        assert "magic_ok" in result
        assert "content_size" in result
        assert "error" in result

    def test_invalid_magic(self):
        result = probe_frame(b"\x00\x00\x00\x00padding")
        assert result["magic_ok"] is False
        assert result["error"] is not None

    def test_too_short(self):
        result = probe_frame(b"\xfd\x2f")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_not_bytes_input(self):
        result = probe_frame("not bytes")
        assert result["valid"] is False
        assert result["error"] is not None


# ── validate_file ─────────────────────────────────────────────────────────

class TestValidateFile:

    def test_nonexistent_file(self, tmp_path):
        result = validate_file(tmp_path / "no_such_file.zst")
        assert result["exists"] is False
        assert result["valid"] is False
        assert result["error"] is not None

    def test_valid_file(self, tmp_path):
        data = b"file content " * 100
        compressed = compress_bytes(data)
        p = tmp_path / "test.zst"
        p.write_bytes(compressed)
        result = validate_file(p)
        assert result["exists"] is True
        assert result["valid"] is True
        assert result["error"] is None

    def test_returns_path(self, tmp_path):
        p = tmp_path / "test.zst"
        p.write_bytes(compress_bytes(b"x"))
        result = validate_file(p)
        assert "path" in result

    def test_has_size_bytes(self, tmp_path):
        compressed = compress_bytes(b"size check")
        p = tmp_path / "test.zst"
        p.write_bytes(compressed)
        result = validate_file(p)
        assert result["size_bytes"] == len(compressed)

    def test_invalid_file_content(self, tmp_path):
        p = tmp_path / "bad.zst"
        p.write_bytes(b"not a zst frame at all!!")
        result = validate_file(p)
        assert result["valid"] is False

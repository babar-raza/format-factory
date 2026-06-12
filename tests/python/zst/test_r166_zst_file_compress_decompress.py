"""
test_r166_zst_file_compress_decompress.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT5-001
Added: 2026-06-11

Tests for ZST compress_file and decompress_file functions.
Closes gaps: GAP-ZST-FOSS-COMPRESS_FIL-001, GAP-ZST-FOSS-DECOMPRESS_F-001.
Authority: P6 (FACT-ZST-001: magic 0xFD2FB528)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    compress_file,
    decompress_file,
    compress_bytes,
    ZstError,
)


# ── compress_file ────────────────────────────────────────────────────────

class TestCompressFile:

    def test_returns_dict(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"hello world " * 100)
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert isinstance(result, dict)

    def test_success_true(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"compress me " * 100)
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert result["success"] is True

    def test_creates_output_file(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"data " * 200)
        out = tmp_path / "output.zst"
        compress_file(src, out)
        assert out.exists()

    def test_output_is_smaller(self, tmp_path):
        src = tmp_path / "input.txt"
        original = b"AAAA" * 1000
        src.write_bytes(original)
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert result["output_bytes"] < result["input_bytes"]

    def test_has_input_bytes(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"data")
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert result["input_bytes"] == 4

    def test_has_output_bytes(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"data " * 50)
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert result["output_bytes"] is not None
        assert result["output_bytes"] > 0

    def test_output_path_in_result(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"x")
        out = tmp_path / "output.zst"
        result = compress_file(src, out)
        assert "output_path" in result

    def test_nonexistent_input_raises(self, tmp_path):
        import pytest
        with pytest.raises(ZstError):
            compress_file(tmp_path / "no_such_file.txt", tmp_path / "out.zst")

    def test_level_parameter(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"level test " * 100)
        out = tmp_path / "output.zst"
        result = compress_file(src, out, level=1)
        assert result["success"] is True

    def test_output_has_zstd_magic(self, tmp_path):
        src = tmp_path / "input.txt"
        src.write_bytes(b"magic test " * 50)
        out = tmp_path / "output.zst"
        compress_file(src, out)
        data = out.read_bytes()
        assert data[:4] == b"\x28\xb5\x2f\xfd"


# ── decompress_file ───────────────────────────────────────────────────────

class TestDecompressFile:

    def test_returns_dict(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(b"hello " * 100)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        result = decompress_file(zst, out)
        assert isinstance(result, dict)

    def test_roundtrip_content(self, tmp_path):
        original = b"round-trip test content " * 50
        src = tmp_path / "data.txt"
        src.write_bytes(original)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        decompress_file(zst, out)
        assert out.read_bytes() == original

    def test_success_true(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(b"success test " * 100)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        result = decompress_file(zst, out)
        assert result["success"] is True

    def test_creates_output_file(self, tmp_path):
        src = tmp_path / "data.txt"
        src.write_bytes(b"file creation " * 100)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        decompress_file(zst, out)
        assert out.exists()

    def test_has_output_bytes(self, tmp_path):
        src = tmp_path / "data.txt"
        original = b"bytes test " * 100
        src.write_bytes(original)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        result = decompress_file(zst, out)
        assert result["output_bytes"] == len(original)

    def test_nonexistent_input_raises(self, tmp_path):
        import pytest
        with pytest.raises(ZstError):
            decompress_file(tmp_path / "no_such.zst", tmp_path / "out.txt")

    def test_unicode_content_roundtrip(self, tmp_path):
        original = "Unicode: \u00e9\u00e0\u00fc\u4e2d\u6587".encode("utf-8") * 50
        src = tmp_path / "data.txt"
        src.write_bytes(original)
        zst = tmp_path / "data.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        decompress_file(zst, out)
        assert out.read_bytes() == original

    def test_empty_file_roundtrip(self, tmp_path):
        src = tmp_path / "empty.txt"
        src.write_bytes(b"")
        zst = tmp_path / "empty.zst"
        compress_file(src, zst)
        out = tmp_path / "recovered.txt"
        decompress_file(zst, out)
        assert out.read_bytes() == b""

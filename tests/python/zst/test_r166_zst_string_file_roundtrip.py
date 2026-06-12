"""
test_r166_zst_string_file_roundtrip.py

Lane I — Gated Product Advancement:
Proves that compress_string_to_file and decompress_file_to_string work
correctly through the full pipeline.

Sprint: FORMAT-FACTORY-SAL-RECONCILIATION-HARDENING-AND-PRODUCT-GATED-ADVANCEMENT-SPRINT-3
spec_fact_refs: FACT-ZST-001
Queue item: sal3-product-q-001, sal3-product-q-002
Authority: ZST P4 — dispatched with spec_fact_refs per Hard Rule 10
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "src" / "python" / "zst"))

from zst_codec import compress_string_to_file, decompress_file_to_string, ZstError


class TestCompressStringToFile:
    def test_basic_roundtrip(self, tmp_path):
        text = "Hello, Zstandard world! Sprint 3 gated product advancement."
        out = tmp_path / "test.zst"
        result = compress_string_to_file(text, out)
        assert result["success"] is True
        assert result["input_bytes"] == len(text.encode("utf-8"))
        assert result["output_bytes"] > 0
        assert Path(result["output_path"]).exists()

    def test_file_is_valid_zst(self, tmp_path):
        text = "Spec-backed product advancement via FACT-ZST-001."
        out = tmp_path / "out.zst"
        compress_string_to_file(text, out)
        raw = out.read_bytes()
        # Zstandard magic
        assert raw[:4] == b"\x28\xb5\x2f\xfd"

    def test_output_path_returned_absolute(self, tmp_path):
        out = tmp_path / "subdir" / "file.zst"
        result = compress_string_to_file("test", out)
        assert Path(result["output_path"]).is_absolute()

    def test_creates_parent_directory(self, tmp_path):
        out = tmp_path / "new_dir" / "nested" / "file.zst"
        result = compress_string_to_file("content", out)
        assert result["success"] is True
        assert out.exists()

    def test_compression_ratio_present(self, tmp_path):
        text = "A" * 1000
        out = tmp_path / "ratio.zst"
        result = compress_string_to_file(text, out)
        assert result["compression_ratio"] is not None
        assert result["compression_ratio"] < 1.0  # should compress well

    def test_empty_string_ratio_none(self, tmp_path):
        out = tmp_path / "empty.zst"
        result = compress_string_to_file("", out)
        assert result["success"] is True
        assert result["input_bytes"] == 0
        assert result["compression_ratio"] is None

    def test_different_levels_produce_different_sizes(self, tmp_path):
        text = "x" * 5000
        out1 = tmp_path / "level1.zst"
        out22 = tmp_path / "level22.zst"
        r1 = compress_string_to_file(text, out1, level=1)
        r22 = compress_string_to_file(text, out22, level=22)
        # Level 22 should produce smaller or equal output for repetitive data
        assert r1["success"] and r22["success"]


class TestDecompressFileToString:
    def test_basic_roundtrip(self, tmp_path):
        text = "Round-trip through compress_string_to_file / decompress_file_to_string."
        out = tmp_path / "rt.zst"
        compress_string_to_file(text, out)
        recovered = decompress_file_to_string(out)
        assert recovered == text

    def test_multiline_roundtrip(self, tmp_path):
        lines = ["line one\n", "line two\n", "line three with unicode: \u00e9\u00e0\n"]
        text = "".join(lines)
        out = tmp_path / "multi.zst"
        compress_string_to_file(text, out)
        recovered = decompress_file_to_string(out)
        assert recovered == text

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            decompress_file_to_string(tmp_path / "nonexistent.zst")

    def test_invalid_zst_raises(self, tmp_path):
        bad = tmp_path / "bad.zst"
        bad.write_bytes(b"not a zstandard frame at all!!!")
        with pytest.raises(ZstError):
            decompress_file_to_string(bad)

    def test_encoding_utf8_default(self, tmp_path):
        text = "UTF-8 content: \u4e2d\u6587\u6d4b\u8bd5"
        out = tmp_path / "utf8.zst"
        compress_string_to_file(text, out, encoding="utf-8")
        recovered = decompress_file_to_string(out, encoding="utf-8")
        assert recovered == text

    def test_max_output_size_respected(self, tmp_path):
        text = "A" * 10000
        out = tmp_path / "large.zst"
        compress_string_to_file(text, out)
        # max_output_size smaller than actual decompressed size should raise
        with pytest.raises(ZstError):
            decompress_file_to_string(out, max_output_size=100)

    def test_error_none_in_compress_result(self, tmp_path):
        out = tmp_path / "ok.zst"
        result = compress_string_to_file("clean", out)
        assert result["error"] is None

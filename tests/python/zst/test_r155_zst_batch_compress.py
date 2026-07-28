"""
test_r155_zst_batch_compress.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT13-001
Added: 2026-06-09

Tests for ZST batch_compress function.
Authority: P6 (SAL-ZST-00001: Zstandard magic 0xFD2FB528, RFC 8878 §3.1.1)
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.zst.zst_codec import batch_compress, decompress_file, ZSTD_MAGIC


class TestBatchCompress:
    """batch_compress: compress multiple files in a batch."""

    def test_batch_single_file(self, tmp_path):
        src = tmp_path / "a.txt"
        src.write_bytes(b"batch test data" * 20)
        dst = tmp_path / "a.zst"
        results = batch_compress([(src, dst)])
        assert len(results) == 1
        assert results[0]["success"] is True
        assert dst.exists()

    def test_batch_multiple_files(self, tmp_path):
        items = []
        for i in range(3):
            src = tmp_path / f"file{i}.txt"
            src.write_bytes(f"content {i} ".encode() * 50)
            dst = tmp_path / f"file{i}.zst"
            items.append((src, dst))
        results = batch_compress(items)
        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_batch_output_has_valid_magic(self, tmp_path):
        src = tmp_path / "magic.txt"
        src.write_bytes(b"magic check" * 10)
        dst = tmp_path / "magic.zst"
        batch_compress([(src, dst)])
        assert dst.read_bytes()[:4] == ZSTD_MAGIC

    def test_batch_continues_on_failure(self, tmp_path):
        good = tmp_path / "good.txt"
        good.write_bytes(b"good data" * 10)
        items = [
            (tmp_path / "nonexistent.txt", tmp_path / "fail.zst"),
            (good, tmp_path / "good.zst"),
        ]
        results = batch_compress(items)
        assert len(results) == 2
        assert results[0]["success"] is False
        assert results[0]["error"] is not None
        assert results[1]["success"] is True

    def test_batch_custom_level(self, tmp_path):
        src = tmp_path / "lvl.txt"
        src.write_bytes(b"level test " * 100)
        dst = tmp_path / "lvl.zst"
        results = batch_compress([(src, dst)], level=9)
        assert results[0]["success"] is True

    def test_batch_empty_list(self):
        results = batch_compress([])
        assert results == []

    def test_batch_roundtrip(self, tmp_path):
        original = b"roundtrip batch " * 100
        src = tmp_path / "rt.txt"
        src.write_bytes(original)
        zst = tmp_path / "rt.zst"
        batch_compress([(src, zst)])
        out = tmp_path / "rt_out.txt"
        decompress_file(zst, out)
        assert out.read_bytes() == original

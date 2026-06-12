"""Tests for ZST batch_decompress.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Covers: batch_decompress on multiple .zst files
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import (
    compress_file,
    batch_decompress,
)


def _make_temp_files(count=3):
    """Create temp files with known content and compress them."""
    items = []
    for i in range(count):
        src = Path(tempfile.mktemp(suffix=f"_{i}.txt"))
        src.write_text(f"content for file {i}" * 100)
        zst = Path(tempfile.mktemp(suffix=f"_{i}.txt.zst"))
        compress_file(src, zst)
        dst = Path(tempfile.mktemp(suffix=f"_{i}_restored.txt"))
        items.append((src, zst, dst))
    return items


class TestBatchDecompress:
    def test_batch_decompress_all_succeed(self):
        items = _make_temp_files(3)
        try:
            batch_items = [(str(zst), str(dst)) for (_, zst, dst) in items]
            results = batch_decompress(batch_items)
            assert len(results) == 3
            for r in results:
                assert r["success"] is True
        finally:
            for src, zst, dst in items:
                src.unlink(missing_ok=True)
                zst.unlink(missing_ok=True)
                dst.unlink(missing_ok=True)

    def test_batch_decompress_restores_content(self):
        items = _make_temp_files(2)
        try:
            batch_items = [(str(zst), str(dst)) for (_, zst, dst) in items]
            batch_decompress(batch_items)
            for i, (src, _, dst) in enumerate(items):
                original = src.read_text()
                restored = dst.read_text()
                assert restored == original, f"File {i} content mismatch"
        finally:
            for src, zst, dst in items:
                src.unlink(missing_ok=True)
                zst.unlink(missing_ok=True)
                dst.unlink(missing_ok=True)

    def test_batch_decompress_handles_bad_file(self):
        good_src = Path(tempfile.mktemp(suffix=".txt"))
        good_src.write_text("good content")
        good_zst = Path(tempfile.mktemp(suffix=".zst"))
        compress_file(good_src, good_zst)
        good_dst = Path(tempfile.mktemp(suffix="_out.txt"))

        bad_zst = Path(tempfile.mktemp(suffix=".zst"))
        bad_zst.write_bytes(b"not a zst file")
        bad_dst = Path(tempfile.mktemp(suffix="_bad_out.txt"))

        try:
            results = batch_decompress([
                (str(good_zst), str(good_dst)),
                (str(bad_zst), str(bad_dst)),
            ])
            assert len(results) == 2
            assert results[0]["success"] is True
            assert results[1]["success"] is False
            assert "error" in results[1]
        finally:
            good_src.unlink(missing_ok=True)
            good_zst.unlink(missing_ok=True)
            good_dst.unlink(missing_ok=True)
            bad_zst.unlink(missing_ok=True)
            bad_dst.unlink(missing_ok=True)

    def test_batch_decompress_empty_list(self):
        results = batch_decompress([])
        assert results == []

    def test_batch_decompress_returns_file_sizes(self):
        items = _make_temp_files(1)
        try:
            batch_items = [(str(zst), str(dst)) for (_, zst, dst) in items]
            results = batch_decompress(batch_items)
            assert results[0]["input_bytes"] is not None
            assert results[0]["output_bytes"] is not None
            assert results[0]["output_bytes"] > results[0]["input_bytes"]
        finally:
            for src, zst, dst in items:
                src.unlink(missing_ok=True)
                zst.unlink(missing_ok=True)
                dst.unlink(missing_ok=True)

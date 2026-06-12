"""
tests/python/zst/test_r183_zst_compressed_size.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT51-001
Tests for zst_compressed_size() — byte size of a .zst compressed file.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import zst_compressed_size

SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstCompressedSize:
    def test_minimal_synthetic_size(self):
        result = zst_compressed_size(SAMPLES / "minimal-synthetic.zst")
        assert result == 10

    def test_text_compressed_size(self):
        result = zst_compressed_size(SAMPLES / "text-compressed.zst")
        assert result > 0

    def test_random_data_size_positive(self):
        result = zst_compressed_size(SAMPLES / "random-data.zst")
        assert result > 0

    def test_returns_int(self):
        result = zst_compressed_size(SAMPLES / "minimal-synthetic.zst")
        assert isinstance(result, int)

    def test_file_not_found_raises(self):
        import pytest
        with pytest.raises(FileNotFoundError):
            zst_compressed_size(SAMPLES / "nonexistent.zst")

    def test_exported_from_init(self):
        from src.python.zst import zst_compressed_size as fn
        result = fn(SAMPLES / "minimal-synthetic.zst")
        assert result == 10

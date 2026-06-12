"""
tests/python/zst/test_r166_zst_string_workflow.py

Tests for ZST string workflow: compress_string and decompress_to_string.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-001, broad-accel-q-002
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_codec import compress_string, decompress_to_string, ZstError


class TestCompressString:
    def test_compress_string_returns_bytes(self) -> None:
        result = compress_string("hello world")
        assert isinstance(result, bytes)

    def test_compress_string_is_smaller_for_long_text(self) -> None:
        text = "abcdef" * 1000
        compressed = compress_string(text)
        assert len(compressed) < len(text.encode("utf-8"))

    def test_compress_string_roundtrip(self) -> None:
        original = "The quick brown fox jumps over the lazy dog."
        compressed = compress_string(original)
        recovered = decompress_to_string(compressed)
        assert recovered == original

    def test_compress_empty_string(self) -> None:
        compressed = compress_string("")
        assert isinstance(compressed, bytes)

    def test_compress_unicode_string(self) -> None:
        text = "Héllo Wörld — café résumé"
        compressed = compress_string(text, encoding="utf-8")
        recovered = decompress_to_string(compressed, encoding="utf-8")
        assert recovered == text

    def test_compress_level_variants(self) -> None:
        text = "test compression levels " * 100
        for level in [1, 3, 9]:
            compressed = compress_string(text, level=level)
            recovered = decompress_to_string(compressed)
            assert recovered == text


class TestDecompressToString:
    def test_decompress_to_string_returns_str(self) -> None:
        compressed = compress_string("hello")
        result = decompress_to_string(compressed)
        assert isinstance(result, str)

    def test_decompress_multiline_text(self) -> None:
        text = "line1\nline2\nline3\n"
        recovered = decompress_to_string(compress_string(text))
        assert recovered == text

    def test_decompress_preserves_whitespace(self) -> None:
        text = "  leading spaces\ttabs\n"
        recovered = decompress_to_string(compress_string(text))
        assert recovered == text

    def test_decompress_json_string(self) -> None:
        import json
        data = json.dumps({"key": "value", "nums": [1, 2, 3]})
        recovered = decompress_to_string(compress_string(data))
        assert json.loads(recovered) == json.loads(data)

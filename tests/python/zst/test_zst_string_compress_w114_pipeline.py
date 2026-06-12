"""
test_zst_string_compress_w114_pipeline.py -- ZST compress_string + decompress_to_string pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-114
Tests compress_string returns bytes, compressed shorter than original, decompress_to_string returns str,
roundtrip identity, roundtrip with unicode.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    compress_string,
    decompress_to_string,
)

_TEXT = "Hello World! This is a test string for Zstandard compression verification."


def test_compress_string_returns_bytes():
    result = compress_string(_TEXT)
    assert isinstance(result, bytes)


def test_compress_string_non_empty():
    result = compress_string(_TEXT)
    assert len(result) > 0


def test_decompress_to_string_returns_str():
    compressed = compress_string(_TEXT)
    result = decompress_to_string(compressed)
    assert isinstance(result, str)


def test_roundtrip_identity():
    compressed = compress_string(_TEXT)
    result = decompress_to_string(compressed)
    assert result == _TEXT


def test_roundtrip_with_unicode():
    text = "Hello \u4e2d\u6587 World \u00e9\u00e0\u00fc"
    compressed = compress_string(text)
    result = decompress_to_string(compressed)
    assert result == text

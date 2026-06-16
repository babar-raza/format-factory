"""
Dogfood pipeline: ZST compress/decompress + ABW remaining → NDJSON export.
Covers: compress_file, decompress_file, compress_string_to_file, decompress_file_to_string,
        abw_average_word_length, abw_avg_words_per_paragraph
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import compress_file, decompress_file, compress_string_to_file, decompress_file_to_string
from abw.abw_codec import abw_average_word_length, abw_avg_words_per_paragraph
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _content_abw():
    from abw.abw_codec import abw_has_content
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if abw_has_content(str(f)):
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def test_zst_compress_file_returns_dict(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text("hello world compression test data")
    dest = tmp_path / "out.zst"
    result = compress_file(str(src), str(dest))
    assert isinstance(result, dict)
    assert dest.exists()
    record = {"format": "zst", "function": "compress_file", "ok": dest.exists()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_zst_decompress_file_returns_dict(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text("hello world decompression test data")
    compressed = tmp_path / "out.zst"
    compress_file(str(src), str(compressed))
    decompressed = tmp_path / "restored.txt"
    result = decompress_file(str(compressed), str(decompressed))
    assert isinstance(result, dict)
    assert decompressed.read_text() == "hello world decompression test data"
    record = {"format": "zst", "function": "decompress_file", "ok": decompressed.exists()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_zst_compress_string_to_file_works(tmp_path):
    dest = tmp_path / "str.zst"
    compress_string_to_file("test string content", str(dest))
    assert dest.exists()
    record = {"format": "zst", "function": "compress_string_to_file", "ok": dest.exists()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_zst_decompress_file_to_string_returns_str(tmp_path):
    dest = tmp_path / "str.zst"
    compress_string_to_file("roundtrip content", str(dest))
    result = decompress_file_to_string(str(dest))
    assert isinstance(result, str)
    assert result == "roundtrip content"
    record = {"format": "zst", "function": "decompress_file_to_string", "content": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["content"] == "roundtrip content"
    assert json.dumps(loaded[0]) is not None


def test_abw_average_word_length_returns_float(tmp_path):
    path = _content_abw()
    result = abw_average_word_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "abw", "function": "abw_average_word_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_words_per_paragraph_returns_float(tmp_path):
    path = _content_abw()
    result = abw_avg_words_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "abw", "function": "abw_avg_words_per_paragraph", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None

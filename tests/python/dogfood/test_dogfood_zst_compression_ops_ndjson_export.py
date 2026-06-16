"""
tests/python/dogfood/test_dogfood_zst_compression_ops_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-83
Dogfood export: ZST compression ops -> write as NDJSON -> verify.
Uses: compress_string, decompress_to_string, compress_string_to_file,
      decompress_file_to_string, batch_compress, batch_decompress.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    compress_string,
    decompress_to_string,
    compress_string_to_file,
    decompress_file_to_string,
    batch_compress,
    batch_decompress,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_SAMPLE_TEXTS = [
    "Hello, format factory! This is test data for ZST compression.",
    "Sprint 83 dogfood pipeline: batch compress and decompress operations.",
    "The quick brown fox jumps over the lazy dog. Repeated text repeated text.",
]


class TestZstCompressionOpsNdjsonExport:
    """ZST compression ops -> NDJSON export -> roundtrip verification."""

    def test_compress_decompress_basics(self):
        for text in _SAMPLE_TEXTS:
            compressed = compress_string(text)
            assert isinstance(compressed, bytes)
            assert len(compressed) > 0
            recovered = decompress_to_string(compressed)
            assert recovered == text

    def test_compress_to_file_basics(self, tmp_path):
        for i, text in enumerate(_SAMPLE_TEXTS):
            dest = str(tmp_path / f"sample{i}.zst")
            result = compress_string_to_file(text, dest)
            assert isinstance(result, dict)
            recovered = decompress_file_to_string(dest)
            assert recovered == text

    def test_compression_ops_to_ndjson(self, tmp_path):
        records = []
        for i, text in enumerate(_SAMPLE_TEXTS):
            compressed = compress_string(text)
            assert isinstance(compressed, bytes)
            recovered = decompress_to_string(compressed)
            assert isinstance(recovered, str)
            assert recovered == text
            dest = str(tmp_path / f"item{i}.zst")
            file_result = compress_string_to_file(text, dest)
            assert isinstance(file_result, dict)
            file_recovered = decompress_file_to_string(dest)
            assert isinstance(file_recovered, str)
            records.append({
                "index": i,
                "original_length": len(text),
                "compressed_bytes": len(compressed),
                "roundtrip_match": recovered == text,
                "file_roundtrip_match": file_recovered == text,
                "source_format": "zst",
            })
        dest = tmp_path / "zst-compression-ops.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) == len(_SAMPLE_TEXTS)

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for i, text in enumerate(_SAMPLE_TEXTS):
            compressed = compress_string(text)
            recovered = decompress_to_string(compressed)
            records.append({
                "index": i,
                "original_length": len(text),
                "compressed_bytes": len(compressed),
                "roundtrip_match": recovered == text,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["index"] == back["index"]
            assert orig["original_length"] == back["original_length"]
            assert orig["roundtrip_match"] == back["roundtrip_match"]

    def test_json_lines_valid(self, tmp_path):
        text = _SAMPLE_TEXTS[0]
        compressed = compress_string(text)
        recovered = decompress_to_string(compressed)
        records = [{"original_length": len(text), "compressed_bytes": len(compressed), "roundtrip_match": recovered == text}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_batch_compress_decompress(self, tmp_path):
        # batch_compress takes (input_path, output_path) tuples
        # First write sample texts to files
        src_files = []
        for i, text in enumerate(_SAMPLE_TEXTS):
            src = tmp_path / f"src{i}.txt"
            src.write_text(text, encoding="utf-8")
            src_files.append(src)
        compress_items = [(str(src), str(tmp_path / f"out{i}.zst")) for i, src in enumerate(src_files)]
        batch_results = batch_compress(compress_items)
        assert isinstance(batch_results, list)
        assert len(batch_results) == len(_SAMPLE_TEXTS)
        decomp_items = [(str(tmp_path / f"out{i}.zst"), str(tmp_path / f"restored{i}.txt")) for i in range(len(_SAMPLE_TEXTS))]
        decomp_results = batch_decompress(decomp_items)
        assert isinstance(decomp_results, list)
        records = []
        for i, (comp, decomp) in enumerate(zip(batch_results, decomp_results)):
            assert isinstance(comp, dict)
            assert isinstance(decomp, dict)
            records.append({
                "index": i,
                "compress_ok": isinstance(comp, dict),
                "decompress_ok": isinstance(decomp, dict),
                "format": "zst",
            })
        dest = tmp_path / "batch-ops.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(_SAMPLE_TEXTS)
        assert all(r["format"] == "zst" for r in loaded)
        assert all(r["compress_ok"] for r in loaded)

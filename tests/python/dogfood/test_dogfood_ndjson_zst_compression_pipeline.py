"""
tests/python/dogfood/test_dogfood_ndjson_zst_compression_pipeline.py

Sprint: IDEMPOTENT-SWARM-SPRINT-22
Pipeline dogfood: generate NDJSON from format stats -> compress to ZST -> decompress -> verify.
Exercises both the NDJSON codec and ZST codec together in a complete pipeline.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import get_dimensions, pixel_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson
from zst import compress_file, decompress_file, zst_is_valid_file, zst_compressed_size


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestNdjsonZstCompressionPipeline:
    """NDJSON generation -> ZST compression -> decompression -> roundtrip verification."""

    def test_generate_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            dims = get_dimensions(str(f))
            records.append({"file": f.name, "w": dims[0], "h": dims[1]})
        dest = tmp_path / "stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert len(records) >= 3

    def test_compress_ndjson_to_zst(self, tmp_path):
        records = [{"file": "test.ppm", "pixels": 100}]
        ndjson_path = tmp_path / "data.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "data.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        assert zst_path.exists()
        assert zst_is_valid_file(str(zst_path))

    def test_full_pipeline_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            dims = get_dimensions(str(f))
            records.append({
                "file": f.name, "width": dims[0], "height": dims[1],
                "pixels": pixel_count(str(f)),
            })
        ndjson_path = tmp_path / "pipeline.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "pipeline.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        restored_path = tmp_path / "restored.ndjson"
        decompress_file(str(zst_path), str(restored_path))
        loaded = load_ndjson(str(restored_path))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["pixels"] == back["pixels"]

    def test_compressed_smaller_than_original(self, tmp_path):
        records = [{"i": i, "data": "x" * 200} for i in range(50)]
        ndjson_path = tmp_path / "big.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "big.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        assert zst_path.stat().st_size < ndjson_path.stat().st_size

    def test_json_lines_preserved_after_roundtrip(self, tmp_path):
        records = [{"a": 1}, {"b": 2}, {"c": 3}]
        ndjson_path = tmp_path / "lines.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "lines.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        restored_path = tmp_path / "lines-restored.ndjson"
        decompress_file(str(zst_path), str(restored_path))
        for line in restored_path.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_zst_file_is_valid(self, tmp_path):
        records = [{"format": "pipeline-test", "count": 42}]
        ndjson_path = tmp_path / "valid.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "valid.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        assert zst_is_valid_file(str(zst_path))
        assert zst_compressed_size(str(zst_path)) > 0

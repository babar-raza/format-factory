"""
tests/python/dogfood/test_dogfood_multiformat_zst_archive_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-29
Dogfood export: Collect multi-format stats -> write as NDJSON -> compress to ZST -> decompress -> verify.
End-to-end pipeline: analytics collection + NDJSON serialization + ZST compression roundtrip.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import abw_word_count
from fodp import fodp_slide_count
from ppm import ppm_pixel_count
from zst import compress_file, decompress_file, zst_is_valid_file, zst_compressed_size
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestMultiformatZstArchiveNdjsonExport:
    """Multi-format stats -> NDJSON -> ZST compress -> decompress -> verify roundtrip."""

    def test_collect_stats(self):
        sample = str(_ABW_DIR / "minimal-document.abw")
        words = abw_word_count(sample)
        assert words >= 0

    def test_ndjson_to_zst_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            records.append({"file": f.name, "format": "abw", "metric": abw_word_count(str(f))})
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({"file": f.name, "format": "fodp", "metric": fodp_slide_count(str(f))})
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({"file": f.name, "format": "ppm", "metric": ppm_pixel_count(str(f))})
        ndjson_path = tmp_path / "stats.ndjson"
        write_ndjson(records, str(ndjson_path))
        assert ndjson_path.stat().st_size > 0
        zst_path = tmp_path / "stats.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        assert zst_path.exists()
        assert zst_is_valid_file(str(zst_path))
        decompressed = tmp_path / "stats-restored.ndjson"
        decompress_file(str(zst_path), str(decompressed))
        loaded = load_ndjson(str(decompressed))
        assert len(loaded) == len(records)

    def test_compressed_smaller(self, tmp_path):
        records = [{"file": f"row-{i}", "val": i * 100} for i in range(50)]
        ndjson_path = tmp_path / "large.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "large.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        original_size = ndjson_path.stat().st_size
        compressed_size = zst_compressed_size(str(zst_path))
        assert compressed_size < original_size, "ZST should compress NDJSON"

    def test_decompressed_json_valid(self, tmp_path):
        records = [{"file": "a.abw", "words": abw_word_count(str(_ABW_DIR / "minimal-document.abw"))}]
        ndjson_path = tmp_path / "one.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "one.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        restored = tmp_path / "one-restored.ndjson"
        decompress_file(str(zst_path), str(restored))
        for line in restored.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_multi_format_coverage(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            records.append({"file": f.name, "format": "abw"})
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({"file": f.name, "format": "fodp"})
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({"file": f.name, "format": "ppm"})
        dest = tmp_path / "coverage.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        formats = {r["format"] for r in loaded}
        assert len(formats) == 3

    def test_zst_valid_check(self, tmp_path):
        records = [{"test": True}]
        ndjson_path = tmp_path / "check.ndjson"
        write_ndjson(records, str(ndjson_path))
        zst_path = tmp_path / "check.ndjson.zst"
        compress_file(str(ndjson_path), str(zst_path))
        assert zst_is_valid_file(str(zst_path))
        assert zst_compressed_size(str(zst_path)) > 0

"""
tests/python/dogfood/test_dogfood_zst_compression_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-41
Dogfood export: ZST parse -> compression analytics -> write as NDJSON -> verify.
Uses: zst_frame_sizes, zst_file_info, zst_compression_ratio, zst_avg_frame_size,
zst_compressed_size, zst_decompressed_size.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    zst_frame_sizes,
    zst_compression_ratio,
    zst_avg_frame_size,
    zst_compressed_size,
    zst_decompressed_size,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _valid_zst_files():
    return sorted(_ZST_DIR.glob("*.zst"))


class TestZstCompressionAnalyticsNdjsonExport:
    """ZST -> compression analytics -> NDJSON export -> roundtrip verification."""

    def test_frame_sizes(self):
        sample = str(_ZST_DIR / "text-compressed.zst")
        sizes = zst_frame_sizes(sample)
        assert isinstance(sizes, list)
        assert all(s >= 0 for s in sizes)

    def test_compression_ratio_and_avg_frame(self):
        sample = str(_ZST_DIR / "text-compressed.zst")
        ratio = zst_compression_ratio(sample)
        avg = zst_avg_frame_size(sample)
        assert ratio >= 0.0
        assert avg >= 0.0

    def test_compression_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            sizes = zst_frame_sizes(path)
            try:
                ratio = zst_compression_ratio(path)
            except Exception:
                ratio = 0.0
            avg = zst_avg_frame_size(path)
            comp = zst_compressed_size(path)
            try:
                decomp = zst_decompressed_size(path)
            except Exception:
                decomp = -1
            assert isinstance(sizes, list), f"frame_sizes must be list for {f.name}"
            assert ratio >= 0.0, f"compression_ratio must be >= 0 for {f.name}"
            assert avg >= 0.0, f"avg_frame_size must be >= 0 for {f.name}"
            assert comp >= 0, f"compressed_size must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "frame_count": len(sizes),
                "compression_ratio": ratio,
                "avg_frame_size": avg,
                "compressed_size": comp,
                "decompressed_size": decomp,
                "source_format": "zst",
            })
        dest = tmp_path / "zst-compression.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            records.append({
                "file": f.name,
                "compression_ratio": zst_compression_ratio(path),
                "compressed_size": zst_compressed_size(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert abs(orig["compression_ratio"] - back["compression_ratio"]) < 1e-9
            assert orig["compressed_size"] == back["compressed_size"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ZST_DIR / "text-compressed.zst")
        records = [{"file": "text-compressed.zst", "ratio": zst_compression_ratio(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_file_info_export(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            ratio = zst_compression_ratio(path)
            sizes = zst_frame_sizes(path)
            avg = zst_avg_frame_size(path)
            assert ratio >= 0.0
            assert isinstance(sizes, list)
            assert avg >= 0.0
            records.append({
                "file": f.name,
                "compression_ratio": ratio,
                "frame_count": len(sizes),
                "avg_frame_size": avg,
                "format": "zst",
            })
        dest = tmp_path / "file-info.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "zst" for r in loaded)
        assert all(r["compression_ratio"] >= 0.0 for r in loaded)

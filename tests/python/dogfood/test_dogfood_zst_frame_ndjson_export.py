"""
tests/python/dogfood/test_dogfood_zst_frame_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-16
Dogfood export: ZST file -> extract frame metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    zst_compressed_size,
    zst_decompressed_size,
    zst_frame_count,
    zst_is_valid_file,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


class TestZstFrameNdjsonExport:
    """ZST -> frame metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_is_valid_zst(self):
        sample = str(_ZST_DIR / "text-compressed.zst")
        assert zst_is_valid_file(sample) is True

    def test_frame_count(self):
        sample = str(_ZST_DIR / "text-compressed.zst")
        assert zst_frame_count(sample) >= 1

    def test_frame_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ZST_DIR.glob("*.zst")):
            try:
                decomp = zst_decompressed_size(str(f))
            except Exception:
                decomp = -1
            records.append({
                "file": f.name,
                "compressed_size": zst_compressed_size(str(f)),
                "decompressed_size": decomp,
                "frame_count": zst_frame_count(str(f)),
                "source_format": "zst",
            })
        dest = tmp_path / "zst-frames.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 5

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_ZST_DIR.glob("*.zst")):
            records.append({
                "file": f.name,
                "compressed_size": zst_compressed_size(str(f)),
                "frame_count": zst_frame_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["compressed_size"] == back["compressed_size"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ZST_DIR / "minimal-synthetic.zst")
        records = [{"file": "minimal-synthetic.zst", "frames": zst_frame_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_compression_ratio_in_export(self, tmp_path):
        records = []
        for f in sorted(_ZST_DIR.glob("*.zst")):
            comp = zst_compressed_size(str(f))
            try:
                decomp = zst_decompressed_size(str(f))
            except Exception:
                decomp = comp
            records.append({
                "file": f.name,
                "ratio": decomp / comp if comp > 0 else 0.0,
                "format": "zst",
            })
        dest = tmp_path / "ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 5
        assert all(r["format"] == "zst" for r in loaded)

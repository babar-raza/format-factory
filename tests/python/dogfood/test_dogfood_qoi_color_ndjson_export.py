"""
tests/python/dogfood/test_dogfood_qoi_color_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-17
Dogfood export: QOI parse -> extract color/channel stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    qoi_dimensions,
    qoi_pixel_count,
    qoi_unique_color_count,
    qoi_channel_count,
    qoi_is_opaque,
    qoi_average_brightness,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiColorNdjsonExport:
    """QOI -> color/channel stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_qoi_dimensions(self):
        sample = str(_QOI_DIR / "1x1-red.qoi")
        dims = qoi_dimensions(sample)
        assert dims["width"] == 1
        assert dims["height"] == 1

    def test_extract_channel_count(self):
        sample = str(_QOI_DIR / "2x2-black.qoi")
        channels = qoi_channel_count(sample)
        assert channels >= 3

    def test_color_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_QOI_DIR.glob("*.qoi")):
            dims = qoi_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims["width"],
                "height": dims["height"],
                "pixels": qoi_pixel_count(str(f)),
                "unique_colors": qoi_unique_color_count(str(f)),
                "channels": qoi_channel_count(str(f)),
                "is_opaque": qoi_is_opaque(str(f)),
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-colors.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_QOI_DIR.glob("*.qoi")):
            records.append({
                "file": f.name,
                "unique_colors": qoi_unique_color_count(str(f)),
                "is_opaque": qoi_is_opaque(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["unique_colors"] == back["unique_colors"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_QOI_DIR / "1x1-red.qoi")
        records = [{"file": "1x1-red.qoi", "pixels": qoi_pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_brightness_in_export(self, tmp_path):
        records = []
        for f in sorted(_QOI_DIR.glob("*.qoi")):
            records.append({
                "file": f.name,
                "avg_brightness": qoi_average_brightness(str(f)),
                "format": "qoi",
            })
        dest = tmp_path / "brightness.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "qoi" for r in loaded)

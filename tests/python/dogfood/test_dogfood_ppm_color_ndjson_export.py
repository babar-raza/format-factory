"""
tests/python/dogfood/test_dogfood_ppm_color_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-15
Dogfood export: PPM parse -> extract color stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import parse_ppm, get_dimensions, pixel_count, ppm_unique_color_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmColorNdjsonExport:
    """PPM -> color stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_ppm_sample(self):
        sample = str(_PPM_DIR / "2x2-rgbw.ppm")
        img = parse_ppm(sample)
        assert isinstance(img, dict)

    def test_extract_dimensions(self):
        sample = str(_PPM_DIR / "2x2-rgbw.ppm")
        dims = get_dimensions(sample)
        assert dims[0] == 2
        assert dims[1] == 2

    def test_color_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            dims = get_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims[0],
                "height": dims[1],
                "pixels": pixel_count(str(f)),
                "unique_colors": ppm_unique_color_count(str(f)),
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-colors.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            dims = get_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims[0],
                "height": dims[1],
                "unique_colors": ppm_unique_color_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["unique_colors"] == back["unique_colors"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_PPM_DIR / "1x1-red.ppm")
        records = [{"file": "1x1-red.ppm", "pixels": pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_gradient_color_count(self, tmp_path):
        sample = str(_PPM_DIR / "3x1-gradient.ppm")
        colors = ppm_unique_color_count(sample)
        record = {"file": "3x1-gradient.ppm", "unique_colors": colors, "format": "ppm"}
        dest = tmp_path / "gradient.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["unique_colors"] >= 2
        assert loaded[0]["format"] == "ppm"

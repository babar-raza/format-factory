"""
tests/python/dogfood/test_dogfood_qoi_metadata_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-10
Dogfood export: QOI image parse -> extract metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import parse_qoi, qoi_dimensions, qoi_channel_count, qoi_unique_color_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiMetadataExport:
    """QOI -> metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_qoi_sample(self):
        sample = str(_QOI_DIR / "1x1-red.qoi")
        img = parse_qoi(sample)
        assert isinstance(img, dict)

    def test_extract_dimensions(self):
        sample = str(_QOI_DIR / "2x2-black.qoi")
        dims = qoi_dimensions(sample)
        assert dims["width"] == 2
        assert dims["height"] == 2

    def test_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_QOI_DIR.glob("*.qoi")):
            dims = qoi_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims["width"],
                "height": dims["height"],
                "channels": qoi_channel_count(str(f)),
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_QOI_DIR.glob("*.qoi")):
            dims = qoi_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims["width"],
                "height": dims["height"],
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["width"] == back["width"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_QOI_DIR / "4x1-gradient.qoi")
        dims = qoi_dimensions(sample)
        records = [{"file": "4x1-gradient.qoi", "pixels": dims["width"] * dims["height"]}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_unique_colors_in_export(self, tmp_path):
        sample = str(_QOI_DIR / "4x1-gradient.qoi")
        colors = qoi_unique_color_count(sample)
        record = {"file": "4x1-gradient.qoi", "unique_colors": colors, "format": "qoi"}
        dest = tmp_path / "colors.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["unique_colors"] == colors
        assert loaded[0]["format"] == "qoi"

"""
tests/python/dogfood/test_dogfood_qoi_blue_green_dominance_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-66
Dogfood export: QOI parse -> blue/green dominance analytics -> write as NDJSON -> verify.
Uses: qoi_avg_rgb_value, qoi_blue_dominant, qoi_green_dominant, qoi_row_count,
qoi_is_square, qoi_pixel_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    qoi_avg_rgb_value,
    qoi_blue_dominant,
    qoi_green_dominant,
    qoi_row_count,
    qoi_is_square,
    qoi_pixel_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _valid_qoi_files():
    return sorted(_QOI_DIR.glob("*.qoi"))


class TestQoiBlueGreenDominanceNdjsonExport:
    """QOI -> blue/green dominance analytics -> NDJSON export -> roundtrip verification."""

    def test_dominance_basics(self):
        sample = str(next(_QOI_DIR.glob("*.qoi")))
        avg_rgb = qoi_avg_rgb_value(sample)
        blue_dom = qoi_blue_dominant(sample)
        green_dom = qoi_green_dominant(sample)
        assert isinstance(avg_rgb, float)
        assert isinstance(blue_dom, bool)
        assert isinstance(green_dom, bool)

    def test_geometry_basics(self):
        sample = str(next(_QOI_DIR.glob("*.qoi")))
        row_count = qoi_row_count(sample)
        is_sq = qoi_is_square(sample)
        pixel_count = qoi_pixel_count(sample)
        assert row_count >= 0
        assert isinstance(is_sq, bool)
        assert pixel_count >= 0

    def test_dominance_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            avg_rgb = qoi_avg_rgb_value(path)
            blue_dom = qoi_blue_dominant(path)
            green_dom = qoi_green_dominant(path)
            row_count = qoi_row_count(path)
            is_sq = qoi_is_square(path)
            pixel_count = qoi_pixel_count(path)
            assert isinstance(avg_rgb, float), f"qoi_avg_rgb_value must be float for {f.name}"
            assert isinstance(blue_dom, bool), f"qoi_blue_dominant must be bool for {f.name}"
            assert isinstance(green_dom, bool), f"qoi_green_dominant must be bool for {f.name}"
            assert row_count >= 0, f"qoi_row_count must be >= 0 for {f.name}"
            assert isinstance(is_sq, bool), f"qoi_is_square must be bool for {f.name}"
            assert pixel_count >= 0, f"qoi_pixel_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_rgb_value": avg_rgb,
                "blue_dominant": blue_dom,
                "green_dominant": green_dom,
                "row_count": row_count,
                "is_square": is_sq,
                "pixel_count": pixel_count,
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-dominance.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            avg_rgb = qoi_avg_rgb_value(path)
            row_count = qoi_row_count(path)
            records.append({
                "file": f.name,
                "avg_rgb_value": avg_rgb,
                "row_count": row_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_rgb_value"] == back["avg_rgb_value"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_QOI_DIR.glob("*.qoi")))
        avg_rgb = qoi_avg_rgb_value(sample)
        blue_dom = qoi_blue_dominant(sample)
        records = [{"file": "sample.qoi", "avg_rgb_value": avg_rgb, "blue_dominant": blue_dom}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_blue_green_square_export(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            blue_dom = qoi_blue_dominant(path)
            green_dom = qoi_green_dominant(path)
            is_sq = qoi_is_square(path)
            avg_rgb = qoi_avg_rgb_value(path)
            assert isinstance(blue_dom, bool)
            assert isinstance(green_dom, bool)
            assert isinstance(is_sq, bool)
            assert isinstance(avg_rgb, float)
            records.append({
                "file": f.name,
                "blue_dominant": blue_dom,
                "green_dominant": green_dom,
                "is_square": is_sq,
                "avg_rgb_value": avg_rgb,
                "format": "qoi",
            })
        dest = tmp_path / "blue-green-square.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "qoi" for r in loaded)
        assert all(isinstance(r["blue_dominant"], bool) for r in loaded)

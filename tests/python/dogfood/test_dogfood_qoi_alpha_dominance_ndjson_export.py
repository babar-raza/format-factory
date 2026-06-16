"""
tests/python/dogfood/test_dogfood_qoi_alpha_dominance_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-49
Dogfood export: QOI parse -> alpha/dominance analytics -> write as NDJSON -> verify.
Uses: qoi_avg_rgb_value, qoi_has_alpha, qoi_red_dominance_ratio,
qoi_dimensions, qoi_pixel_count, qoi_channel_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    qoi_avg_rgb_value,
    qoi_has_alpha,
    qoi_red_dominance_ratio,
    qoi_dimensions,
    qoi_pixel_count,
    qoi_channel_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_qoi_files():
    return sorted(_QOI_DIR.glob("*.qoi"))


class TestQoiAlphaDominanceNdjsonExport:
    """QOI -> alpha/dominance analytics -> NDJSON export -> roundtrip verification."""

    def test_avg_rgb_and_has_alpha(self):
        sample = _ap(next(_QOI_DIR.glob("*.qoi")))
        avg_rgb = qoi_avg_rgb_value(sample)
        has_alpha = qoi_has_alpha(sample)
        assert avg_rgb >= 0.0
        assert isinstance(has_alpha, bool)

    def test_red_dominance_and_dimensions(self):
        sample = _ap(next(_QOI_DIR.glob("*.qoi")))
        dominance = qoi_red_dominance_ratio(sample)
        dims = qoi_dimensions(sample)
        px_count = qoi_pixel_count(sample)
        channels = qoi_channel_count(sample)
        assert dominance >= 0.0
        assert isinstance(dims, dict)
        assert px_count >= 0
        assert channels >= 0

    def test_alpha_dominance_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            avg_rgb = qoi_avg_rgb_value(path)
            has_alpha = qoi_has_alpha(path)
            dominance = qoi_red_dominance_ratio(path)
            dims = qoi_dimensions(path)
            px_count = qoi_pixel_count(path)
            channels = qoi_channel_count(path)
            assert avg_rgb >= 0.0, f"avg_rgb_value must be >= 0 for {f.name}"
            assert isinstance(has_alpha, bool), f"has_alpha must be bool for {f.name}"
            assert dominance >= 0.0, f"red_dominance_ratio must be >= 0 for {f.name}"
            assert isinstance(dims, dict), f"dimensions must be dict for {f.name}"
            assert px_count >= 0, f"pixel_count must be >= 0 for {f.name}"
            assert channels >= 0, f"channel_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_rgb_value": avg_rgb,
                "has_alpha": has_alpha,
                "red_dominance_ratio": dominance,
                "width": dims.get("width", 0),
                "height": dims.get("height", 0),
                "pixel_count": px_count,
                "channel_count": channels,
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-alpha-dominance.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "avg_rgb_value": qoi_avg_rgb_value(path),
                "red_dominance_ratio": qoi_red_dominance_ratio(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_rgb_value"] == back["avg_rgb_value"]
            assert orig["red_dominance_ratio"] == back["red_dominance_ratio"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_QOI_DIR.glob("*.qoi")))
        records = [{"file": "sample.qoi", "has_alpha": qoi_has_alpha(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_channel_rgb_export(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = _ap(f)
            avg_rgb = qoi_avg_rgb_value(path)
            has_alpha = qoi_has_alpha(path)
            channels = qoi_channel_count(path)
            assert avg_rgb >= 0.0
            assert isinstance(has_alpha, bool)
            assert channels >= 0
            records.append({
                "file": f.name,
                "avg_rgb_value": avg_rgb,
                "has_alpha": has_alpha,
                "channel_count": channels,
                "format": "qoi",
            })
        dest = tmp_path / "channel-rgb.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "qoi" for r in loaded)
        assert all(r["avg_rgb_value"] >= 0.0 for r in loaded)

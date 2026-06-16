"""
tests/python/dogfood/test_dogfood_multiformat_image_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-21
Cross-format dogfood: aggregate image dimensions and pixel counts from PPM + PBM + PGM + QOI
into a unified NDJSON export. Demonstrates image format interoperability.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import get_dimensions as ppm_dims, pixel_count as ppm_pixels
from pbm import get_dimensions as pbm_dims, pixel_count as pbm_pixels
from pgm import get_dimensions as pgm_dims, pixel_count as pgm_pixels
from qoi import qoi_dimensions, qoi_pixel_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _collect_image_records():
    records = []
    for f in sorted(_PPM_DIR.glob("*.ppm")):
        dims = ppm_dims(str(f))
        records.append({
            "file": f.name, "format": "ppm",
            "width": dims[0], "height": dims[1],
            "pixels": ppm_pixels(str(f)),
        })
    for f in sorted(_PBM_DIR.glob("*.pbm")):
        dims = pbm_dims(str(f))
        records.append({
            "file": f.name, "format": "pbm",
            "width": dims[0], "height": dims[1],
            "pixels": pbm_pixels(str(f)),
        })
    for f in sorted(_PGM_DIR.glob("*.pgm")):
        dims = pgm_dims(str(f))
        records.append({
            "file": f.name, "format": "pgm",
            "width": dims[0], "height": dims[1],
            "pixels": pgm_pixels(str(f)),
        })
    for f in sorted(_QOI_DIR.glob("*.qoi")):
        dims = qoi_dimensions(str(f))
        records.append({
            "file": f.name, "format": "qoi",
            "width": dims["width"], "height": dims["height"],
            "pixels": qoi_pixel_count(str(f)),
        })
    return records


class TestMultiformatImageNdjsonExport:
    """Cross-format image stats aggregation -> NDJSON -> verification."""

    def test_collects_from_four_formats(self):
        records = _collect_image_records()
        formats = {r["format"] for r in records}
        assert "ppm" in formats
        assert "pbm" in formats
        assert "pgm" in formats
        assert "qoi" in formats

    def test_minimum_record_count(self):
        records = _collect_image_records()
        assert len(records) >= 8

    def test_multiformat_to_ndjson(self, tmp_path):
        records = _collect_image_records()
        dest = tmp_path / "images.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)

    def test_ndjson_roundtrip(self, tmp_path):
        records = _collect_image_records()
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["pixels"] == back["pixels"]

    def test_json_lines_valid(self, tmp_path):
        records = _collect_image_records()[:3]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "format" in obj

    def test_aspect_ratio_cross_format(self, tmp_path):
        records = []
        for r in _collect_image_records():
            ratio = r["width"] / r["height"] if r["height"] > 0 else 0.0
            records.append({
                "file": r["file"], "format": r["format"],
                "aspect_ratio": ratio,
            })
        dest = tmp_path / "ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        formats = {r["format"] for r in loaded}
        assert len(formats) >= 4

"""
tests/python/dogfood/test_dogfood_fodp_text_density_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-25
Dogfood export: FODP parse -> text density / shape analytics -> write as NDJSON -> verify.
Uses deeper FODP analytics: text_per_slide, slide_text_density, average_shapes_per_slide, etc.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    fodp_total_text_length,
    fodp_text_per_slide,
    fodp_slide_text_density,
    fodp_average_shapes_per_slide,
    fodp_max_text_per_slide,
    fodp_total_notes_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


class TestFodpTextDensityNdjsonExport:
    """FODP -> text density / shape analytics -> NDJSON export -> roundtrip verification."""

    def test_total_text_length(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        length = fodp_total_text_length(sample)
        assert isinstance(length, int)
        assert length >= 0

    def test_text_per_slide(self):
        sample = str(_FODP_DIR / "two-slides-basic.fodp")
        texts = fodp_text_per_slide(sample)
        assert isinstance(texts, list)
        assert len(texts) == 2

    def test_text_density_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "total_text_length": fodp_total_text_length(str(f)),
                "text_density": fodp_slide_text_density(str(f)),
                "avg_shapes_per_slide": fodp_average_shapes_per_slide(str(f)),
                "max_text_per_slide": fodp_max_text_per_slide(str(f)),
                "total_notes_length": fodp_total_notes_length(str(f)),
                "source_format": "fodp",
            })
        dest = tmp_path / "fodp-text-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "total_text_length": fodp_total_text_length(str(f)),
                "text_density": fodp_slide_text_density(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_text_length"] == back["total_text_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_FODP_DIR / "minimal-presentation.fodp")
        records = [{"file": "minimal-presentation.fodp", "density": fodp_slide_text_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_shape_density_export(self, tmp_path):
        records = []
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "avg_shapes": fodp_average_shapes_per_slide(str(f)),
                "format": "fodp",
            })
        dest = tmp_path / "shapes.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodp" for r in loaded)

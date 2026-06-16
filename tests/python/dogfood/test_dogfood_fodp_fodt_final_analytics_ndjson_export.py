"""
tests/python/dogfood/test_dogfood_fodp_fodt_final_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-85
Dogfood export: FODP+FODT final analytics -> write as NDJSON -> verify.
Uses: fodp_is_single_slide, fodp_notes_density, fodp_has_titles,
      fodp_min_shapes_per_slide, fodt_vocabulary_richness, fodt_is_empty.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import fodp_is_single_slide, fodp_notes_density, fodp_has_titles, fodp_min_shapes_per_slide
from fodt import fodt_vocabulary_richness, fodt_is_empty, fodt_has_headings
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodp_files():
    return sorted(_FODP_DIR.glob("*.fodp"))


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodpFodtFinalAnalyticsNdjsonExport:
    """FODP+FODT -> final analytics -> NDJSON export -> roundtrip verification."""

    def test_fodp_final_basics(self):
        sample = _valid_fodp_files()[0]
        path = str(sample)
        is_single = fodp_is_single_slide(path)
        notes_density = fodp_notes_density(path)
        has_titles = fodp_has_titles(path)
        min_shapes = fodp_min_shapes_per_slide(path)
        assert isinstance(is_single, bool)
        assert isinstance(notes_density, float) and notes_density >= 0.0
        assert isinstance(has_titles, bool)
        assert isinstance(min_shapes, int) and min_shapes >= 0

    def test_fodt_final_basics(self):
        sample = _valid_fodt_files()[0]
        path = str(sample)
        vocab = fodt_vocabulary_richness(path)
        is_empty = fodt_is_empty(path)
        has_headings = fodt_has_headings(path)
        assert isinstance(vocab, float) and vocab >= 0.0
        assert isinstance(is_empty, bool)
        assert isinstance(has_headings, bool)

    def test_final_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            is_single = fodp_is_single_slide(path)
            notes_density = fodp_notes_density(path)
            has_titles = fodp_has_titles(path)
            min_shapes = fodp_min_shapes_per_slide(path)
            assert isinstance(is_single, bool), f"fodp_is_single_slide must be bool for {f.name}"
            assert isinstance(notes_density, float), f"fodp_notes_density must be float for {f.name}"
            assert isinstance(has_titles, bool), f"fodp_has_titles must be bool for {f.name}"
            assert isinstance(min_shapes, int), f"fodp_min_shapes_per_slide must be int for {f.name}"
            records.append({
                "file": f.name,
                "is_single_slide": is_single,
                "notes_density": notes_density,
                "has_titles": has_titles,
                "min_shapes_per_slide": min_shapes,
                "source_format": "fodp",
            })
        for f in _valid_fodt_files():
            path = str(f)
            vocab = fodt_vocabulary_richness(path)
            is_empty = fodt_is_empty(path)
            has_headings = fodt_has_headings(path)
            assert isinstance(vocab, float), f"fodt_vocabulary_richness must be float for {f.name}"
            assert isinstance(is_empty, bool), f"fodt_is_empty must be bool for {f.name}"
            assert isinstance(has_headings, bool), f"fodt_has_headings must be bool for {f.name}"
            records.append({
                "file": f.name,
                "vocabulary_richness": vocab,
                "is_empty": is_empty,
                "has_headings": has_headings,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodp-fodt-final-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 6

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            notes_density = fodp_notes_density(path)
            has_titles = fodp_has_titles(path)
            records.append({"file": f.name, "notes_density": notes_density, "has_titles": has_titles, "format": "fodp"})
        for f in _valid_fodt_files():
            path = str(f)
            vocab = fodt_vocabulary_richness(path)
            records.append({"file": f.name, "vocabulary_richness": vocab, "format": "fodt"})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]

    def test_json_lines_valid(self, tmp_path):
        sample_fodp = _valid_fodp_files()[0]
        sample_fodt = _valid_fodt_files()[0]
        is_single = fodp_is_single_slide(str(sample_fodp))
        vocab = fodt_vocabulary_richness(str(sample_fodt))
        records = [
            {"file": sample_fodp.name, "is_single_slide": is_single, "format": "fodp"},
            {"file": sample_fodt.name, "vocabulary_richness": vocab, "format": "fodt"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_fodp_fodt_combined_export(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            notes_density = fodp_notes_density(path)
            min_shapes = fodp_min_shapes_per_slide(path)
            records.append({
                "file": f.name,
                "notes_density": notes_density,
                "min_shapes": min_shapes,
                "format": "fodp",
            })
        for f in _valid_fodt_files():
            path = str(f)
            vocab = fodt_vocabulary_richness(path)
            is_empty = fodt_is_empty(path)
            has_headings = fodt_has_headings(path)
            records.append({
                "file": f.name,
                "vocabulary_richness": vocab,
                "is_empty": is_empty,
                "has_headings": has_headings,
                "format": "fodt",
            })
        dest = tmp_path / "combined.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 6
        fodp_records = [r for r in loaded if r["format"] == "fodp"]
        fodt_records = [r for r in loaded if r["format"] == "fodt"]
        assert all(isinstance(r["notes_density"], float) for r in fodp_records)
        assert all(isinstance(r["vocabulary_richness"], float) for r in fodt_records)

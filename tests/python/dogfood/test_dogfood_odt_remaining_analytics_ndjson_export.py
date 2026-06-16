"""
tests/python/dogfood/test_dogfood_odt_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-84
Dogfood export: ODT parse -> remaining analytics -> write as NDJSON -> verify.
Uses: probe_odt, odt_total_elements, odt_is_empty, odt_shortest_word,
      odt_paragraph_density, odt_heading_density.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    probe_odt,
    odt_total_elements,
    odt_is_empty,
    odt_shortest_word,
    odt_paragraph_density,
    odt_heading_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtRemainingAnalyticsNdjsonExport:
    """ODT -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_probe_odt_basics(self):
        sample = _valid_odt_files()[0]
        result = probe_odt(str(sample))
        assert isinstance(result, dict)

    def test_element_analytics_basics(self):
        sample = _valid_odt_files()[0]
        path = str(sample)
        total = odt_total_elements(path)
        empty = odt_is_empty(path)
        shortest = odt_shortest_word(path)
        assert isinstance(total, int) and total >= 0
        assert isinstance(empty, bool)
        assert isinstance(shortest, int) and shortest >= 0

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            probe = probe_odt(path)
            total_el = odt_total_elements(path)
            is_empty = odt_is_empty(path)
            shortest = odt_shortest_word(path)
            para_density = odt_paragraph_density(path)
            heading_density = odt_heading_density(path)
            assert isinstance(probe, dict), f"probe_odt must return dict for {f.name}"
            assert isinstance(total_el, int), f"odt_total_elements must return int for {f.name}"
            assert isinstance(is_empty, bool), f"odt_is_empty must return bool for {f.name}"
            assert isinstance(shortest, int), f"odt_shortest_word must return int for {f.name}"
            assert isinstance(para_density, float), f"odt_paragraph_density must return float for {f.name}"
            assert isinstance(heading_density, float), f"odt_heading_density must return float for {f.name}"
            records.append({
                "file": f.name,
                "probe_ok": isinstance(probe, dict),
                "total_elements": total_el,
                "is_empty": is_empty,
                "shortest_word": shortest,
                "paragraph_density": para_density,
                "heading_density": heading_density,
                "source_format": "odt",
            })
        dest = tmp_path / "odt-remaining-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            total_el = odt_total_elements(path)
            is_empty = odt_is_empty(path)
            records.append({
                "file": f.name,
                "total_elements": total_el,
                "is_empty": is_empty,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_elements"] == back["total_elements"]
            assert orig["is_empty"] == back["is_empty"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_odt_files()[0]
        path = str(sample)
        probe = probe_odt(path)
        total_el = odt_total_elements(path)
        records = [{"file": sample.name, "probe_ok": isinstance(probe, dict), "total_elements": total_el}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_density_analytics_export(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = str(f)
            para_density = odt_paragraph_density(path)
            heading_density = odt_heading_density(path)
            shortest = odt_shortest_word(path)
            assert para_density >= 0.0
            assert heading_density >= 0.0
            assert shortest >= 0
            records.append({
                "file": f.name,
                "paragraph_density": para_density,
                "heading_density": heading_density,
                "shortest_word": shortest,
                "format": "odt",
            })
        dest = tmp_path / "density-analytics.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "odt" for r in loaded)
        assert all(r["paragraph_density"] >= 0.0 for r in loaded)

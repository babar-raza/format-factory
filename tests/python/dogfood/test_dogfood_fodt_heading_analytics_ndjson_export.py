"""
tests/python/dogfood/test_dogfood_fodt_heading_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-36
Dogfood export: FODT parse -> heading/table/list analytics -> write as NDJSON -> verify.
Uses: document_heading_outline, document_heading_level_distribution, document_list_stats,
document_table_summary, document_table_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_heading_outline,
    document_heading_level_distribution,
    document_list_stats,
    document_table_summary,
    document_table_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


class TestFodtHeadingAnalyticsNdjsonExport:
    """FODT -> heading/table/list analytics -> NDJSON export -> roundtrip verification."""

    def test_heading_outline(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        outline = document_heading_outline(doc)
        assert isinstance(outline, list)

    def test_heading_distribution(self):
        sample = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        doc = parse_fodt(sample)
        dist = document_heading_level_distribution(doc)
        lst = document_list_stats(doc)
        assert isinstance(dist, dict)
        assert isinstance(lst, dict)

    def test_heading_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            outline = document_heading_outline(doc)
            dist = document_heading_level_distribution(doc)
            lst = document_list_stats(doc)
            tables = document_table_summary(doc)
            cells = document_table_cell_count(doc)
            assert isinstance(outline, list), f"heading_outline must be list for {f.name}"
            assert isinstance(dist, dict), f"heading_level_dist must be dict for {f.name}"
            assert isinstance(lst, dict), f"list_stats must be dict for {f.name}"
            assert isinstance(tables, list), f"table_summary must be list for {f.name}"
            assert isinstance(cells, dict), f"table_cell_count must be dict for {f.name}"
            records.append({
                "file": f.name,
                "heading_count": len(outline),
                "heading_levels": len(dist),
                "table_count": len(tables),
                "list_stats": lst,
                "table_cell_count": cells,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-headings.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            records.append({
                "file": f.name,
                "heading_count": len(document_heading_outline(doc)),
                "table_count": len(document_table_summary(doc)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["heading_count"] == back["heading_count"]

    def test_json_lines_valid(self, tmp_path):
        doc = parse_fodt(str(_FODT_DIR / "headings-and-paragraphs.fodt"))
        outline = document_heading_outline(doc)
        records = [{"file": "headings-and-paragraphs.fodt", "heading_count": len(outline)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_heading_level_export(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            doc = parse_fodt(str(f))
            dist = document_heading_level_distribution(doc)
            outline = document_heading_outline(doc)
            assert isinstance(dist, dict)
            assert isinstance(outline, list)
            records.append({
                "file": f.name,
                "heading_count": len(outline),
                "level_distribution": dist,
                "format": "fodt",
            })
        dest = tmp_path / "heading-levels.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fodt" for r in loaded)
        assert all(r["heading_count"] >= 0 for r in loaded)

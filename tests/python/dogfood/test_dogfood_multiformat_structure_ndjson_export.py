"""
tests/python/dogfood/test_dogfood_multiformat_structure_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-28
Dogfood export: Cross-format document structure comparison (ABW + FODT + FODP) -> NDJSON.
Compares paragraph/slide/section counts across document-oriented formats.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import abw_paragraph_count, abw_word_count
from fodt import parse_fodt, document_paragraph_count, document_total_words
from fodp import fodp_slide_count, fodp_total_text_length
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


class TestMultiformatStructureNdjsonExport:
    """Cross-format document structure -> NDJSON export -> roundtrip verification."""

    def test_abw_structure(self):
        sample = str(_ABW_DIR / "two-paragraphs.abw")
        paras = abw_paragraph_count(sample)
        assert paras >= 2

    def test_fodt_structure(self):
        sample = str(_FODT_DIR / "minimal-document.fodt")
        doc = parse_fodt(sample)
        paras = document_paragraph_count(doc)
        assert paras >= 1

    def test_cross_structure_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            records.append({
                "file": f.name,
                "format": "abw",
                "structural_units": abw_paragraph_count(str(f)),
                "word_count": abw_word_count(str(f)),
                "unit_type": "paragraph",
            })
        for f in sorted(_FODT_DIR.glob("*.fodt")):
            doc = parse_fodt(str(f))
            records.append({
                "file": f.name,
                "format": "fodt",
                "structural_units": document_paragraph_count(doc),
                "word_count": document_total_words(doc),
                "unit_type": "paragraph",
            })
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({
                "file": f.name,
                "format": "fodp",
                "structural_units": fodp_slide_count(str(f)),
                "word_count": fodp_total_text_length(str(f)),
                "unit_type": "slide",
            })
        dest = tmp_path / "multiformat-structure.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        formats = {r["format"] for r in records}
        assert len(formats) == 3, f"expected 3 formats, got {formats}"

    def test_ndjson_roundtrip(self, tmp_path):
        records = [
            {"file": "test.abw", "format": "abw", "units": abw_paragraph_count(str(_ABW_DIR / "two-paragraphs.abw"))},
            {"file": "test.fodp", "format": "fodp", "units": fodp_slide_count(str(_FODP_DIR / "two-slides-basic.fodp"))},
        ]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert loaded[0]["format"] == "abw"
        assert loaded[1]["format"] == "fodp"

    def test_json_lines_valid(self, tmp_path):
        records = [{"file": "t.abw", "format": "abw", "paras": abw_paragraph_count(str(_ABW_DIR / "minimal-document.abw"))}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_unit_type_coverage(self, tmp_path):
        records = []
        for f in sorted(_ABW_DIR.glob("*.abw")):
            records.append({"file": f.name, "format": "abw", "unit_type": "paragraph"})
        for f in sorted(_FODP_DIR.glob("*.fodp")):
            records.append({"file": f.name, "format": "fodp", "unit_type": "slide"})
        dest = tmp_path / "units.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        unit_types = {r["unit_type"] for r in loaded}
        assert "paragraph" in unit_types
        assert "slide" in unit_types

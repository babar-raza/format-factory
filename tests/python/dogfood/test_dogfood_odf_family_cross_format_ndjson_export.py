"""Dogfood test: ODF family cross-format analytics pipeline.

Exercises FODS and FODT libraries together to produce a unified NDJSON
analytics export combining spreadsheet and text document statistics.
This tests the "multi-format inventory" dogfood pattern.
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods, workbook_stats, workbook_type_distribution
from fodt import parse_fodt, document_paragraph_count, document_stats, document_word_count
from ndjson.ndjson_codec import write_ndjson


# ---- Minimal FODS fixture ----
_FODS_CONTENT = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Data">
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Name</text:p></table:table-cell>
          <table:table-cell office:value-type="string"><text:p>Value</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell office:value-type="string"><text:p>Alpha</text:p></table:table-cell>
          <table:table-cell office:value-type="float" office:value="42"><text:p>42</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
"""

# ---- Minimal FODT fixture ----
_FODT_CONTENT = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.text">
  <office:body>
    <office:text>
      <text:h text:outline-level="1">Introduction</text:h>
      <text:p>This is a sample document for cross-format testing.</text:p>
      <text:h text:outline-level="2">Details</text:h>
      <text:p>More content here with multiple words in each paragraph.</text:p>
      <text:p>A third paragraph for good measure.</text:p>
    </office:text>
  </office:body>
</office:document>
"""


@pytest.fixture
def fods_path(tmp_path):
    p = tmp_path / "test.fods"
    p.write_text(_FODS_CONTENT, encoding="utf-8")
    return p


@pytest.fixture
def fodt_path(tmp_path):
    p = tmp_path / "test.fodt"
    p.write_text(_FODT_CONTENT, encoding="utf-8")
    return p


def _build_inventory(fods_path, fodt_path):
    """Build a multi-format inventory from FODS and FODT files."""
    records = []

    # FODS analytics
    fods_doc = parse_fods(fods_path)
    stats = workbook_stats(fods_doc)
    records.append({
        "format": "FODS",
        "metric": "sheet_count",
        "value": stats.get("sheet_count", 0),
    })
    records.append({
        "format": "FODS",
        "metric": "cell_count",
        "value": stats.get("total_cells", 0),
    })
    type_dist = workbook_type_distribution(fods_doc)
    # Key might be "string" or total non-float types
    string_count = type_dist.get("string", 0) or sum(
        v for k, v in type_dist.items() if k != "float" and isinstance(v, (int, float))
    )
    records.append({
        "format": "FODS",
        "metric": "type_count",
        "value": len(type_dist),
    })

    # FODT analytics
    fodt_doc = parse_fodt(fodt_path)
    fodt_st = document_stats(fodt_doc)
    records.append({
        "format": "FODT",
        "metric": "paragraph_count",
        "value": fodt_st.get("paragraph_count", document_paragraph_count(fodt_doc)),
    })
    records.append({
        "format": "FODT",
        "metric": "heading_count",
        "value": fodt_st.get("heading_count", 0),
    })
    wc = document_word_count(fodt_doc)
    # document_word_count returns a dict with total_words key
    total_words = wc.get("total_words", 0) if isinstance(wc, dict) else wc
    records.append({
        "format": "FODT",
        "metric": "word_count",
        "value": total_words,
    })

    return records


class TestOdfFamilyCrossFormatPipeline:
    """Tests for the ODF family cross-format NDJSON export pipeline."""

    def test_inventory_has_both_formats(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        formats = {r["format"] for r in records}
        assert formats == {"FODS", "FODT"}

    def test_inventory_has_six_records(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        assert len(records) == 6

    def test_fods_sheet_count(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        sheet_rec = [r for r in records if r["metric"] == "sheet_count"][0]
        assert sheet_rec["value"] == 1

    def test_fods_cell_count(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        cell_rec = [r for r in records if r["metric"] == "cell_count"][0]
        assert cell_rec["value"] >= 4  # 2 rows x 2 cols

    def test_fods_type_count(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        type_rec = [r for r in records if r["metric"] == "type_count"][0]
        assert type_rec["value"] >= 1  # At least one type present

    def test_fodt_paragraph_count(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        para_rec = [r for r in records if r["metric"] == "paragraph_count"][0]
        assert para_rec["value"] >= 3  # 3 text:p elements

    def test_fodt_heading_count(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        heading_rec = [r for r in records if r["metric"] == "heading_count"][0]
        assert heading_rec["value"] == 2  # 2 text:h elements

    def test_fodt_word_count_positive(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        word_rec = [r for r in records if r["metric"] == "word_count"][0]
        assert word_rec["value"] > 0

    def test_ndjson_export_roundtrip(self, fods_path, fodt_path, tmp_path):
        """Full pipeline: build inventory -> export NDJSON -> reload -> verify."""
        records = _build_inventory(fods_path, fodt_path)
        ndjson_path = tmp_path / "odf-inventory.ndjson"
        write_ndjson(records, ndjson_path)

        # Reload and verify
        lines = ndjson_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 6
        reloaded = [json.loads(line) for line in lines]
        formats = {r["format"] for r in reloaded}
        assert formats == {"FODS", "FODT"}

    def test_ndjson_each_record_has_required_keys(self, fods_path, fodt_path, tmp_path):
        records = _build_inventory(fods_path, fodt_path)
        ndjson_path = tmp_path / "odf-inventory.ndjson"
        write_ndjson(records, ndjson_path)

        lines = ndjson_path.read_text(encoding="utf-8").strip().split("\n")
        for line in lines:
            rec = json.loads(line)
            assert "format" in rec
            assert "metric" in rec
            assert "value" in rec

    def test_values_are_numeric_or_nonnegative(self, fods_path, fodt_path):
        records = _build_inventory(fods_path, fodt_path)
        for r in records:
            assert isinstance(r["value"], (int, float))
            assert r["value"] >= 0

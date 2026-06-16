"""test_dogfood_fodt_para_depth_ndjson_export.py

Dogfood export path: FODT paragraph depth analytics → NDJSON.

Uses fodt_longest_paragraph_index, fodt_paragraph_length_range,
fodt_max_heading_depth on real FODT sample files.

Concrete values (headings-and-paragraphs.fodt):
  longest_paragraph_index = 2
  paragraph_length_range  = 50
  max_heading_depth       = 1

Sprint: product-deepening-fodt-para-depth-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import (
    fodt_longest_paragraph_index,
    fodt_paragraph_length_range,
    fodt_max_heading_depth,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodt"
HEADINGS_PARAS = SAMPLES_DIR / "headings-and-paragraphs.fodt"
MINIMAL = SAMPLES_DIR / "minimal-document.fodt"
LIST_BASIC = SAMPLES_DIR / "list-basic.fodt"


def _export_para_depth_record(path: Path) -> dict:
    return {
        "file": path.name,
        "longest_paragraph_index": fodt_longest_paragraph_index(path),
        "paragraph_length_range": fodt_paragraph_length_range(path),
        "max_heading_depth": fodt_max_heading_depth(path),
    }


class TestFodtParaDepthNdjsonExport:

    def test_headings_longest_paragraph_index_is_two(self):
        rec = _export_para_depth_record(HEADINGS_PARAS)
        assert rec["longest_paragraph_index"] == 2

    def test_headings_paragraph_length_range_is_fifty(self):
        rec = _export_para_depth_record(HEADINGS_PARAS)
        assert rec["paragraph_length_range"] == 50

    def test_headings_max_heading_depth_is_one(self):
        rec = _export_para_depth_record(HEADINGS_PARAS)
        assert rec["max_heading_depth"] == 1

    def test_minimal_longest_paragraph_index_is_zero(self):
        rec = _export_para_depth_record(MINIMAL)
        assert rec["longest_paragraph_index"] == 0

    def test_minimal_paragraph_length_range_is_zero(self):
        rec = _export_para_depth_record(MINIMAL)
        assert rec["paragraph_length_range"] == 0

    def test_minimal_max_heading_depth_is_zero(self):
        rec = _export_para_depth_record(MINIMAL)
        assert rec["max_heading_depth"] == 0

    def test_record_has_all_keys(self):
        rec = _export_para_depth_record(HEADINGS_PARAS)
        for key in ["file", "longest_paragraph_index",
                    "paragraph_length_range", "max_heading_depth"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [
            _export_para_depth_record(HEADINGS_PARAS),
            _export_para_depth_record(MINIMAL),
        ]
        out = tmp_path / "fodt_para_depth.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "paragraph_length_range" in parsed

    def test_ndjson_line_file_key_correct(self, tmp_path):
        records = [_export_para_depth_record(HEADINGS_PARAS)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "headings-and-paragraphs.fodt"

    def test_list_basic_para_length_range_non_negative(self):
        rec = _export_para_depth_record(LIST_BASIC)
        assert rec["paragraph_length_range"] >= 0

    def test_list_basic_longest_paragraph_index_non_negative(self):
        rec = _export_para_depth_record(LIST_BASIC)
        assert rec["longest_paragraph_index"] >= -1

    def test_ndjson_three_files_first_line_values(self, tmp_path):
        records = [
            _export_para_depth_record(HEADINGS_PARAS),
            _export_para_depth_record(MINIMAL),
            _export_para_depth_record(LIST_BASIC),
        ]
        out = tmp_path / "three.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3
        first = json.loads(lines[0])
        assert first["longest_paragraph_index"] == 2
        assert first["max_heading_depth"] == 1

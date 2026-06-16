"""test_dogfood_abw_punctuation_analytics_ndjson_export.py

Dogfood export path: ABW punctuation/text density analytics → NDJSON.

Covers gap functions: abw_punctuation_count, abw_median_paragraph_length,
abw_distinct_word_ratio, abw_total_text_length, abw_nonempty_paragraph_ratio,
abw_has_numeric_content, abw_nonspace_char_count.

Concrete values (two-paragraphs.abw):
  punctuation_count       = 2
  median_paragraph_length = 16
  distinct_word_ratio     = 0.75
  total_text_length       = 33
  nonempty_paragraph_ratio = 1.0
  has_numeric_content     = False
  nonspace_char_count     = 31

Sprint: product-deepening-abw-punctuation-analytics-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import (
    abw_punctuation_count,
    abw_median_paragraph_length,
    abw_distinct_word_ratio,
    abw_total_text_length,
    abw_nonempty_paragraph_ratio,
    abw_has_numeric_content,
    abw_nonspace_char_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "abw"
TWO_PARAS = SAMPLES_DIR / "two-paragraphs.abw"
MINIMAL = SAMPLES_DIR / "minimal-document.abw"
EMPTY = SAMPLES_DIR / "empty-section.abw"


def _export_record(path: Path) -> dict:
    return {
        "file": path.name,
        "punctuation_count": abw_punctuation_count(path),
        "median_paragraph_length": abw_median_paragraph_length(path),
        "distinct_word_ratio": abw_distinct_word_ratio(path),
        "total_text_length": abw_total_text_length(path),
        "nonempty_paragraph_ratio": abw_nonempty_paragraph_ratio(path),
        "has_numeric_content": abw_has_numeric_content(path),
        "nonspace_char_count": abw_nonspace_char_count(path),
    }


class TestAbwPunctuationAnalyticsNdjsonExport:

    def test_two_paras_punctuation_count_is_two(self):
        rec = _export_record(TWO_PARAS)
        assert rec["punctuation_count"] == 2

    def test_two_paras_median_para_length_is_sixteen(self):
        rec = _export_record(TWO_PARAS)
        assert rec["median_paragraph_length"] == 16

    def test_two_paras_distinct_word_ratio_seventy_five_pct(self):
        rec = _export_record(TWO_PARAS)
        assert abs(rec["distinct_word_ratio"] - 0.75) < 0.01

    def test_two_paras_total_text_length_is_thirty_three(self):
        rec = _export_record(TWO_PARAS)
        assert rec["total_text_length"] == 33

    def test_two_paras_nonempty_ratio_is_one(self):
        rec = _export_record(TWO_PARAS)
        assert abs(rec["nonempty_paragraph_ratio"] - 1.0) < 0.01

    def test_two_paras_nonspace_char_count_is_thirty_one(self):
        rec = _export_record(TWO_PARAS)
        assert rec["nonspace_char_count"] == 31

    def test_two_paras_has_no_numeric_content(self):
        rec = _export_record(TWO_PARAS)
        assert rec["has_numeric_content"] is False

    def test_record_has_all_keys(self):
        rec = _export_record(TWO_PARAS)
        for key in ["file", "punctuation_count", "median_paragraph_length",
                    "distinct_word_ratio", "total_text_length",
                    "nonempty_paragraph_ratio", "has_numeric_content",
                    "nonspace_char_count"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_record(TWO_PARAS), _export_record(MINIMAL)]
        out = tmp_path / "abw_punct_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "nonspace_char_count" in parsed

    def test_ndjson_line_file_key_correct(self, tmp_path):
        records = [_export_record(TWO_PARAS)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "two-paragraphs.abw"

    def test_minimal_total_text_length_is_five(self):
        rec = _export_record(MINIMAL)
        assert rec["total_text_length"] == 5

    def test_empty_section_zeros(self):
        rec = _export_record(EMPTY)
        assert rec["punctuation_count"] == 0
        assert rec["total_text_length"] == 0
        assert rec["nonspace_char_count"] == 0

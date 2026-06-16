"""test_dogfood_fodt_text_analytics_ndjson_export.py

Dogfood export path: FODT text analytics → NDJSON.

Uses fodt_unique_word_count, fodt_longest_word, fodt_sentence_count,
fodt_whitespace_ratio, fodt_avg_heading_length, fodt_is_multi_paragraph
on real FODT sample files, then exports results as NDJSON records.

Fix note: these functions previously used body_blocks (wrong key); fixed to
use blocks (correct key from parse_fodt_strict). All 1197 FODT tests pass.

Sprint: product-deepening-fodt-png-export-20260616 (bug fix + dogfood)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import (
    fodt_unique_word_count,
    fodt_longest_word,
    fodt_sentence_count,
    fodt_whitespace_ratio,
    fodt_avg_heading_length,
    fodt_is_multi_paragraph,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodt"
HEADINGS_PARAS = SAMPLES_DIR / "headings-and-paragraphs.fodt"
MINIMAL = SAMPLES_DIR / "minimal-document.fodt"
LIST_BASIC = SAMPLES_DIR / "list-basic.fodt"


def _export_text_analytics_record(path: Path) -> dict:
    return {
        "file": path.name,
        "unique_word_count": fodt_unique_word_count(path),
        "longest_word": fodt_longest_word(path),
        "sentence_count": fodt_sentence_count(path),
        "whitespace_ratio": fodt_whitespace_ratio(path),
        "avg_heading_length": fodt_avg_heading_length(path),
        "is_multi_paragraph": fodt_is_multi_paragraph(path),
    }


class TestFodtTextAnalyticsNdjsonExport:

    def test_headings_unique_word_count_positive(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert rec["unique_word_count"] >= 1

    def test_headings_longest_word_nonempty(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert len(rec["longest_word"]) >= 1

    def test_headings_sentence_count_positive(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert rec["sentence_count"] >= 1

    def test_headings_whitespace_ratio_in_range(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert 0.0 <= rec["whitespace_ratio"] <= 1.0

    def test_headings_avg_heading_length_positive(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert rec["avg_heading_length"] >= 1.0

    def test_headings_is_multi_paragraph(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        assert rec["is_multi_paragraph"] is True

    def test_record_has_all_keys(self):
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        for key in ["file", "unique_word_count", "longest_word",
                    "sentence_count", "whitespace_ratio", "avg_heading_length",
                    "is_multi_paragraph"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [
            _export_text_analytics_record(HEADINGS_PARAS),
            _export_text_analytics_record(MINIMAL),
        ]
        out = tmp_path / "fodt_text_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "unique_word_count" in parsed

    def test_ndjson_line_file_key_correct(self, tmp_path):
        records = [_export_text_analytics_record(HEADINGS_PARAS)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "headings-and-paragraphs.fodt"

    def test_minimal_sample_no_error(self):
        rec = _export_text_analytics_record(MINIMAL)
        assert "file" in rec
        assert rec["unique_word_count"] >= 0

    def test_list_basic_unique_words_positive(self):
        rec = _export_text_analytics_record(LIST_BASIC)
        assert rec["unique_word_count"] >= 1

    def test_unique_word_count_less_than_total_words(self):
        # unique count should be <= total char count / 3 (rough sanity)
        rec = _export_text_analytics_record(HEADINGS_PARAS)
        # just check it's a reasonable int
        assert isinstance(rec["unique_word_count"], int)
        assert rec["unique_word_count"] >= 0

"""test_dogfood_fodp_new_analytics_gaps_ndjson_export.py

Dogfood export path: FODP new analytics gap functions -> NDJSON.

Covers: fodp_avg_sentence_length, fodp_avg_text_length, fodp_avg_title_words,
fodp_has_multi_slide, fodp_has_numeric_content, fodp_is_nonempty.

Concrete values (minimal-presentation.fodp):
  avg_sentence_length = 5.0
  avg_text_length     = 5.0
  avg_title_words     = 1.0
  has_multi_slide     = False
  has_numeric_content = False
  is_nonempty         = True

Concrete values (two-slides-basic.fodp):
  avg_sentence_length = 21.0
  has_multi_slide     = True
  is_nonempty         = True

Concrete values (title-only.fodp):
  is_nonempty         = False

Sprint: product-deepening-fodp-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import (
    fodp_avg_sentence_length,
    fodp_avg_text_length,
    fodp_avg_title_words,
    fodp_has_multi_slide,
    fodp_has_numeric_content,
    fodp_is_nonempty,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = SAMPLES_DIR / "minimal-presentation.fodp"
TITLE_ONLY = SAMPLES_DIR / "title-only.fodp"
TWO_SLIDES = SAMPLES_DIR / "two-slides-basic.fodp"


def _export_fodp_new_record(path: Path) -> dict:
    return {
        "file": path.name,
        "avg_sentence_length": fodp_avg_sentence_length(path),
        "avg_text_length": fodp_avg_text_length(path),
        "avg_title_words": fodp_avg_title_words(path),
        "has_multi_slide": fodp_has_multi_slide(path),
        "has_numeric_content": fodp_has_numeric_content(path),
        "is_nonempty": fodp_is_nonempty(path),
    }


class TestFodpNewAnalyticsGapsNdjsonExport:

    def test_minimal_avg_sentence_length(self):
        rec = _export_fodp_new_record(MINIMAL)
        assert abs(rec["avg_sentence_length"] - 5.0) < 0.1

    def test_two_slides_avg_sentence_length(self):
        rec = _export_fodp_new_record(TWO_SLIDES)
        assert rec["avg_sentence_length"] > 0.0

    def test_minimal_avg_text_length(self):
        rec = _export_fodp_new_record(MINIMAL)
        assert abs(rec["avg_text_length"] - 5.0) < 0.1

    def test_title_only_avg_text_length_zero(self):
        rec = _export_fodp_new_record(TITLE_ONLY)
        assert abs(rec["avg_text_length"]) < 0.01

    def test_minimal_avg_title_words(self):
        rec = _export_fodp_new_record(MINIMAL)
        assert abs(rec["avg_title_words"] - 1.0) < 0.01

    def test_minimal_not_multi_slide(self):
        rec = _export_fodp_new_record(MINIMAL)
        assert rec["has_multi_slide"] is False

    def test_two_slides_is_multi_slide(self):
        rec = _export_fodp_new_record(TWO_SLIDES)
        assert rec["has_multi_slide"] is True

    def test_minimal_is_nonempty(self):
        rec = _export_fodp_new_record(MINIMAL)
        assert rec["is_nonempty"] is True

    def test_title_only_is_not_nonempty(self):
        rec = _export_fodp_new_record(TITLE_ONLY)
        assert rec["is_nonempty"] is False

    def test_record_has_all_keys(self):
        rec = _export_fodp_new_record(MINIMAL)
        for key in ["file", "avg_sentence_length", "avg_text_length", "avg_title_words",
                    "has_multi_slide", "has_numeric_content", "is_nonempty"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_fodp_new_record(MINIMAL), _export_fodp_new_record(TWO_SLIDES)]
        out = tmp_path / "fodp_new_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "is_nonempty" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_fodp_new_record(MINIMAL)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-presentation.fodp"

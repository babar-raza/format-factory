"""
tests/python/dogfood/test_dogfood_fodt_abw_sylk_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-54
Dogfood export: FODT + ABW + SYLK remaining uncovered analytics -> NDJSON -> verify.
FODT uses: fodt_avg_words_per_paragraph, fodt_is_single_paragraph.
ABW uses: abw_avg_words_per_paragraph, abw_has_unicode,
          abw_is_single_paragraph, abw_sentence_density.
SYLK uses: sylk_data_density, sylk_has_numeric_cells,
           sylk_is_single_row, sylk_max_string_length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_avg_words_per_paragraph, fodt_is_single_paragraph
from abw.abw_codec import (
    abw_avg_words_per_paragraph, abw_has_unicode,
    abw_is_single_paragraph, abw_sentence_density,
)
from sylk.sylk_analytics import sylk_data_density, sylk_has_numeric_cells, sylk_is_single_row, sylk_max_string_length
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


class TestFodtAbwSylkRemainingAnalyticsNdjsonExport:
    """FODT + ABW + SYLK remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_fodt_remaining_basics(self):
        s_min = str(_FODT_DIR / "minimal-document.fodt")
        s_head = str(_FODT_DIR / "headings-and-paragraphs.fodt")
        s_list = str(_FODT_DIR / "list-basic.fodt")
        assert fodt_avg_words_per_paragraph(s_min) == 2.0
        assert fodt_is_single_paragraph(s_min) is True
        assert fodt_avg_words_per_paragraph(s_head) == 11.0
        assert fodt_is_single_paragraph(s_head) is False
        assert fodt_avg_words_per_paragraph(s_list) == 3.0
        assert fodt_is_single_paragraph(s_list) is False

    def test_abw_remaining_basics(self):
        s_min = str(_ABW_DIR / "minimal-document.abw")
        s_two = str(_ABW_DIR / "two-paragraphs.abw")
        s_empty = str(_ABW_DIR / "empty-section.abw")
        assert abw_avg_words_per_paragraph(s_min) == 1.0
        assert abw_is_single_paragraph(s_min) is True
        assert abw_has_unicode(s_min) is False
        assert abw_sentence_density(s_min) == 0.0
        assert abw_avg_words_per_paragraph(s_two) == 2.0
        assert abw_is_single_paragraph(s_two) is False
        assert abw_sentence_density(s_two) == 1.0
        assert abw_avg_words_per_paragraph(s_empty) == 0.0
        assert abw_sentence_density(s_empty) == 0.0

    def test_sylk_remaining_basics(self):
        s_min = str(_SYLK_DIR / "minimal-2x2.slk")
        s_num = str(_SYLK_DIR / "numeric-row.slk")
        s_single = str(_SYLK_DIR / "single-cell.slk")
        assert sylk_data_density(s_min) == 1.0
        assert sylk_has_numeric_cells(s_min) is True
        assert sylk_is_single_row(s_min) is False
        assert sylk_max_string_length(s_min) == 5
        assert sylk_data_density(s_num) == 1.0
        assert sylk_has_numeric_cells(s_num) is True
        assert sylk_is_single_row(s_num) is True
        assert sylk_max_string_length(s_num) == 0
        assert sylk_is_single_row(s_single) is True

    def test_fodt_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            avg_words = fodt_avg_words_per_paragraph(path)
            is_single = fodt_is_single_paragraph(path)
            assert isinstance(avg_words, (int, float)), f"avg_words_per_paragraph must be numeric for {f.name}"
            assert isinstance(is_single, bool), f"is_single_paragraph must be bool for {f.name}"
            records.append({
                "file": f.name,
                "avg_words_per_paragraph": float(avg_words),
                "is_single_paragraph": is_single,
                "source_format": "fodt",
            })
        dest = tmp_path / "fodt-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_abw_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            records.append({
                "file": f.name,
                "avg_words_per_paragraph": float(abw_avg_words_per_paragraph(path)),
                "has_unicode": abw_has_unicode(path),
                "is_single_paragraph": abw_is_single_paragraph(path),
                "sentence_density": float(abw_sentence_density(path)),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 2

    def test_sylk_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_sylk_files():
            path = str(f)
            records.append({
                "file": f.name,
                "data_density": sylk_data_density(path),
                "has_numeric_cells": sylk_has_numeric_cells(path),
                "is_single_row": sylk_is_single_row(path),
                "max_string_length": sylk_max_string_length(path),
                "source_format": "sylk",
            })
        dest = tmp_path / "sylk-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodt_files():
            path = str(f)
            records.append({
                "file": f.name,
                "avg_words_per_paragraph": float(fodt_avg_words_per_paragraph(path)),
                "is_single_paragraph": fodt_is_single_paragraph(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_words_per_paragraph"] == back["avg_words_per_paragraph"]
            assert orig["is_single_paragraph"] == back["is_single_paragraph"]

    def test_json_lines_valid(self, tmp_path):
        s_fodt = str(_FODT_DIR / "minimal-document.fodt")
        s_abw = str(_ABW_DIR / "two-paragraphs.abw")
        s_sylk = str(_SYLK_DIR / "numeric-row.slk")
        records = [
            {"file": "minimal-document.fodt", "avg_words": fodt_avg_words_per_paragraph(s_fodt), "format": "fodt"},
            {"file": "two-paragraphs.abw", "sentence_density": abw_sentence_density(s_abw), "format": "abw"},
            {"file": "numeric-row.slk", "data_density": sylk_data_density(s_sylk), "format": "sylk"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

"""Tests for abw_typed_children_to_ndjson dogfood export.

Verifies that ABW paragraphs are exported as typed NDJSON records
using AbwDocument.typed_children() (D2 DOM API).

GAP ref: GAP-ABW-DOM-MATURITY-D2-001
Sprint: FORENSICS-HEALING-SPRINT-001 / TC-DOGFOOD-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

MINIMAL = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARAS = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_typed_children_to_ndjson import abw_typed_children_to_ndjson
from ndjson.ndjson_codec import load_ndjson


class TestAbwTypedChildrenToNdjson:
    def test_returns_integer_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        result = abw_typed_children_to_ndjson(MINIMAL, dest)
        assert isinstance(result, int)

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(MINIMAL, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(MINIMAL, dest)
        records = load_ndjson(str(dest))
        assert isinstance(records, list)

    def test_two_paragraphs_file_yields_two_records(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        count = abw_typed_children_to_ndjson(TWO_PARAS, dest)
        assert count == 2

    def test_records_have_typed_fields(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(TWO_PARAS, dest)
        records = load_ndjson(str(dest))
        for rec in records:
            assert "index" in rec
            assert "text" in rec
            assert "word_count" in rec
            assert "char_count" in rec

    def test_word_count_matches_text(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(TWO_PARAS, dest)
        records = load_ndjson(str(dest))
        for rec in records:
            expected_wc = len(rec["text"].split()) if rec["text"].strip() else 0
            assert rec["word_count"] == expected_wc

    def test_char_count_matches_text(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(TWO_PARAS, dest)
        records = load_ndjson(str(dest))
        for rec in records:
            assert rec["char_count"] == len(rec["text"])

    def test_uses_ff_ndjson_writer(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        abw_typed_children_to_ndjson(MINIMAL, dest)
        lines = dest.read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)

    def test_parent_dirs_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "deep" / "nested" / "out.ndjson"
        abw_typed_children_to_ndjson(MINIMAL, dest)
        assert dest.exists()

    def test_skip_empty_true_skips_empty_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.ndjson"
        count = abw_typed_children_to_ndjson(MINIMAL, dest, skip_empty=True)
        records = load_ndjson(str(dest))
        for rec in records:
            assert rec["text"].strip() != ""
        assert count == len(records)

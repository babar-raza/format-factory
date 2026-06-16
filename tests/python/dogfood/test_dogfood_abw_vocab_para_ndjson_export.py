"""
tests/python/dogfood/test_dogfood_abw_vocab_para_ndjson_export.py

Sprint: PRODUCT-DEEPENING-DOGFOOD-ABW-VOCAB-20260616
Dogfood export: ABW parse -> vocabulary/paragraph analytics -> write as NDJSON -> verify.
Uses: abw_vocabulary_richness, abw_average_paragraph_length,
abw_min_paragraph_length, abw_char_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    abw_average_paragraph_length,
    abw_char_count,
    abw_min_paragraph_length,
    abw_vocabulary_richness,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwVocabParaNdjsonExport:
    """ABW -> vocabulary/paragraph analytics -> NDJSON export -> roundtrip verification."""

    def test_vocabulary_richness_bounds(self):
        for f in _valid_abw_files():
            richness = abw_vocabulary_richness(_ap(f))
            assert 0.0 <= richness <= 1.0, f"vocabulary_richness must be in [0,1] for {f.name}"

    def test_concrete_values_minimal(self):
        path = _ap(_ABW_DIR / "minimal-document.abw")
        assert abs(abw_vocabulary_richness(path) - 1.0) < 1e-6
        assert abs(abw_average_paragraph_length(path) - 5.0) < 1e-6
        assert abw_min_paragraph_length(path) == 5
        assert abw_char_count(path) == 5

    def test_concrete_values_two_paragraphs(self):
        path = _ap(_ABW_DIR / "two-paragraphs.abw")
        assert abs(abw_vocabulary_richness(path) - 0.75) < 1e-6
        assert abs(abw_average_paragraph_length(path) - 16.5) < 1e-6
        assert abw_min_paragraph_length(path) == 16
        assert abw_char_count(path) == 33

    def test_average_para_length_all_files(self):
        for f in _valid_abw_files():
            path = _ap(f)
            avg = abw_average_paragraph_length(path)
            min_len = abw_min_paragraph_length(path)
            chars = abw_char_count(path)
            assert avg >= 0.0, f"avg_paragraph_length must be >= 0 for {f.name}"
            assert min_len >= 0, f"min_paragraph_length must be >= 0 for {f.name}"
            assert chars >= 0, f"char_count must be >= 0 for {f.name}"

    def test_vocab_para_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = _ap(f)
            richness = abw_vocabulary_richness(path)
            avg_para = abw_average_paragraph_length(path)
            min_para = abw_min_paragraph_length(path)
            chars = abw_char_count(path)

            assert 0.0 <= richness <= 1.0, f"vocab_richness bounds for {f.name}"
            assert avg_para >= 0.0, f"avg_paragraph_length >= 0 for {f.name}"
            assert min_para >= 0, f"min_paragraph_length >= 0 for {f.name}"
            assert chars >= 0, f"char_count >= 0 for {f.name}"

            records.append({
                "file": f.name,
                "vocabulary_richness": richness,
                "average_paragraph_length": avg_para,
                "min_paragraph_length": min_para,
                "char_count": chars,
                "source_format": "abw",
            })

        dest = tmp_path / "abw-vocab-para.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "vocabulary_richness": abw_vocabulary_richness(path),
                "average_paragraph_length": abw_average_paragraph_length(path),
                "char_count": abw_char_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert abs(orig["vocabulary_richness"] - back["vocabulary_richness"]) < 1e-9
            assert abs(orig["average_paragraph_length"] - back["average_paragraph_length"]) < 1e-9
            assert orig["char_count"] == back["char_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_ABW_DIR.glob("*.abw")))
        records = [{
            "file": "sample.abw",
            "vocabulary_richness": abw_vocabulary_richness(sample),
            "format": "abw",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert obj["format"] == "abw"

    def test_vocab_richness_pipeline(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = _ap(f)
            richness = abw_vocabulary_richness(path)
            avg_para = abw_average_paragraph_length(path)
            records.append({
                "file": f.name,
                "vocabulary_richness": richness,
                "average_paragraph_length": avg_para,
                "format": "abw",
            })
        dest = tmp_path / "vocab-richness.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "abw" for r in loaded)
        assert all(0.0 <= r["vocabulary_richness"] <= 1.0 for r in loaded)
        assert all(r["average_paragraph_length"] >= 0.0 for r in loaded)

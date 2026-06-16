"""
tests/python/dogfood/test_dogfood_odt_vocab_sentence_ndjson_export.py

Sprint: PRODUCT-DEEPENING-DOGFOOD-ODT-VOCAB-20260616
Dogfood export: ODT parse -> vocabulary/sentence analytics -> write as NDJSON -> verify.
Uses: odt_vocabulary_richness, odt_words_per_sentence, odt_sentence_count,
odt_chars_per_word, odt_unique_word_count, odt_longest_paragraph.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_chars_per_word,
    odt_longest_paragraph,
    odt_sentence_count,
    odt_unique_word_count,
    odt_vocabulary_richness,
    odt_words_per_sentence,
)
from ndjson.ndjson_codec import load_ndjson, write_ndjson


_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


class TestOdtVocabSentenceNdjsonExport:
    """ODT -> vocabulary/sentence analytics -> NDJSON export -> roundtrip verification."""

    def test_vocabulary_richness_and_unique_words(self):
        sample = _ap(next(_ODT_DIR.glob("*.odt")))
        richness = odt_vocabulary_richness(sample)
        unique = odt_unique_word_count(sample)
        assert 0.0 <= richness <= 1.0, f"vocabulary_richness must be in [0,1], got {richness}"
        assert unique >= 0, f"unique_word_count must be >= 0, got {unique}"

    def test_sentence_and_words_per_sentence(self):
        sample = _ap(_ODT_DIR / "minimal-document.odt")
        sents = odt_sentence_count(sample)
        wps = odt_words_per_sentence(sample)
        assert sents >= 0, f"sentence_count must be >= 0, got {sents}"
        assert wps >= 0.0, f"words_per_sentence must be >= 0, got {wps}"

    def test_concrete_values_minimal_document(self):
        sample = _ap(_ODT_DIR / "minimal-document.odt")
        assert odt_sentence_count(sample) == 1
        assert odt_unique_word_count(sample) == 2
        assert abs(odt_vocabulary_richness(sample) - 1.0) < 1e-6
        assert odt_longest_paragraph(sample) == 13

    def test_concrete_values_two_paragraphs(self):
        sample = _ap(_ODT_DIR / "two-paragraphs.odt")
        assert odt_sentence_count(sample) == 2
        assert odt_unique_word_count(sample) == 3
        assert abs(odt_vocabulary_richness(sample) - 0.75) < 1e-6
        assert odt_longest_paragraph(sample) == 17

    def test_chars_per_word_and_longest_paragraph(self):
        for f in _valid_odt_files():
            path = _ap(f)
            cpw = odt_chars_per_word(path)
            longest = odt_longest_paragraph(path)
            assert cpw >= 0.0, f"chars_per_word must be >= 0 for {f.name}"
            assert longest >= 0, f"longest_paragraph must be >= 0 for {f.name}"

    def test_vocab_sentence_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = _ap(f)
            richness = odt_vocabulary_richness(path)
            wps = odt_words_per_sentence(path)
            sents = odt_sentence_count(path)
            cpw = odt_chars_per_word(path)
            unique = odt_unique_word_count(path)
            longest_p = odt_longest_paragraph(path)

            assert 0.0 <= richness <= 1.0, f"vocab_richness bounds failed for {f.name}"
            assert wps >= 0.0, f"words_per_sentence must be >= 0 for {f.name}"
            assert sents >= 0, f"sentence_count must be >= 0 for {f.name}"
            assert cpw >= 0.0, f"chars_per_word must be >= 0 for {f.name}"
            assert unique >= 0, f"unique_word_count must be >= 0 for {f.name}"
            assert longest_p >= 0, f"longest_paragraph must be >= 0 for {f.name}"

            records.append({
                "file": f.name,
                "vocabulary_richness": richness,
                "words_per_sentence": wps,
                "sentence_count": sents,
                "chars_per_word": cpw,
                "unique_word_count": unique,
                "longest_paragraph": longest_p,
                "source_format": "odt",
            })

        dest = tmp_path / "odt-vocab-sentence.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "vocabulary_richness": odt_vocabulary_richness(path),
                "sentence_count": odt_sentence_count(path),
                "unique_word_count": odt_unique_word_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert abs(orig["vocabulary_richness"] - back["vocabulary_richness"]) < 1e-9
            assert orig["sentence_count"] == back["sentence_count"]
            assert orig["unique_word_count"] == back["unique_word_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_ODT_DIR.glob("*.odt")))
        records = [{
            "file": "sample.odt",
            "vocabulary_richness": odt_vocabulary_richness(sample),
            "unique_word_count": odt_unique_word_count(sample),
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sentence_density_pipeline(self, tmp_path):
        records = []
        for f in _valid_odt_files():
            path = _ap(f)
            sents = odt_sentence_count(path)
            unique = odt_unique_word_count(path)
            richness = odt_vocabulary_richness(path)
            records.append({
                "file": f.name,
                "sentence_count": sents,
                "unique_word_count": unique,
                "vocabulary_richness": richness,
                "format": "odt",
            })
        dest = tmp_path / "sentence-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 2
        assert all(r["format"] == "odt" for r in loaded)
        assert all(r["sentence_count"] >= 0 for r in loaded)
        assert all(0.0 <= r["vocabulary_richness"] <= 1.0 for r in loaded)

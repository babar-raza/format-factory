"""
tests/python/dogfood/test_dogfood_abw_final_ndjson_final_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-90
Dogfood export: ABW final analytics + NDJSON final -> write as NDJSON -> verify.
Uses: abw_heading_count, abw_vocabulary_richness, abw_average_paragraph_length,
      abw_is_empty, ndjson_max_string_length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import abw_heading_count, abw_vocabulary_richness, abw_average_paragraph_length, abw_is_empty
from ndjson import ndjson_max_string_length, write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"

_STRING_DATA = [
    {"id": 1, "text": "short"},
    {"id": 2, "text": "a longer string value here"},
    {"id": 3, "text": "medium length"},
]


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


def _make_ndjson_file(tmp_path, records, name="data.ndjson"):
    dest = tmp_path / name
    write_ndjson(records, str(dest))
    return str(dest)


class TestAbwFinalNdjsonFinalNdjsonExport:
    """ABW final + NDJSON final analytics -> NDJSON export -> roundtrip verification."""

    def test_abw_final_basics(self):
        sample = _valid_abw_files()[0]
        path = str(sample)
        hc = abw_heading_count(path)
        vocab = abw_vocabulary_richness(path)
        avg_para = abw_average_paragraph_length(path)
        is_empty = abw_is_empty(path)
        assert isinstance(hc, int) and hc >= 0
        assert isinstance(vocab, float) and vocab >= 0.0
        assert isinstance(avg_para, float) and avg_para >= 0.0
        assert isinstance(is_empty, bool)

    def test_ndjson_max_string_length_basics(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _STRING_DATA)
        max_sl = ndjson_max_string_length(src)
        assert isinstance(max_sl, int) and max_sl >= 0
        # "a longer string value here" has 26 chars
        assert max_sl >= 5, "max_string_length should be at least 5"

    def test_combined_to_ndjson(self, tmp_path):
        src = _make_ndjson_file(tmp_path, _STRING_DATA)
        max_sl = ndjson_max_string_length(src)
        assert isinstance(max_sl, int) and max_sl >= 0
        records = []
        for f in _valid_abw_files():
            path = str(f)
            hc = abw_heading_count(path)
            vocab = abw_vocabulary_richness(path)
            avg_para = abw_average_paragraph_length(path)
            is_empty = abw_is_empty(path)
            assert isinstance(hc, int), f"abw_heading_count must be int for {f.name}"
            assert isinstance(vocab, float), f"abw_vocabulary_richness must be float for {f.name}"
            assert isinstance(avg_para, float), f"abw_average_paragraph_length must be float for {f.name}"
            assert isinstance(is_empty, bool), f"abw_is_empty must be bool for {f.name}"
            records.append({
                "file": f.name,
                "heading_count": hc,
                "vocabulary_richness": vocab,
                "average_paragraph_length": avg_para,
                "is_empty": is_empty,
                "ndjson_max_string_length": max_sl,
                "source_format": "abw",
            })
        dest = tmp_path / "abw-final-ndjson-final.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            hc = abw_heading_count(path)
            is_empty = abw_is_empty(path)
            records.append({"file": f.name, "heading_count": hc, "is_empty": is_empty})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["heading_count"] == back["heading_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_abw_files()[0]
        hc = abw_heading_count(str(sample))
        vocab = abw_vocabulary_richness(str(sample))
        records = [{"file": sample.name, "heading_count": hc, "vocabulary_richness": vocab}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_abw_vocabulary_avg_para_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            vocab = abw_vocabulary_richness(path)
            avg_para = abw_average_paragraph_length(path)
            assert vocab >= 0.0
            assert avg_para >= 0.0
            records.append({
                "file": f.name,
                "vocabulary_richness": vocab,
                "average_paragraph_length": avg_para,
                "format": "abw",
            })
        dest = tmp_path / "vocab-avg-para.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["vocabulary_richness"] >= 0.0 for r in loaded)

"""
tests/python/dogfood/test_dogfood_abw_metadata_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-67
Dogfood export: ABW parse -> metadata/section analytics -> write as NDJSON -> verify.
Uses: load, get_section_count, get_paragraph_count, extract_text,
get_metadata, word_frequency.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    get_section_count,
    get_paragraph_count,
    extract_text,
    get_metadata,
    word_frequency,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwMetadataAnalyticsNdjsonExport:
    """ABW -> metadata/section analytics -> NDJSON export -> roundtrip verification."""

    def test_section_and_paragraph_count(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        sec_count = get_section_count(sample)
        para_count = get_paragraph_count(sample)
        assert sec_count >= 0
        assert para_count >= 0

    def test_extract_text_and_metadata(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        texts = extract_text(sample)
        meta = get_metadata(sample)
        assert isinstance(texts, list)
        assert isinstance(meta, dict)

    def test_metadata_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            sec_count = get_section_count(path)
            para_count = get_paragraph_count(path)
            texts = extract_text(path)
            meta = get_metadata(path)
            freq = word_frequency(model)
            assert sec_count >= 0, f"get_section_count must be >= 0 for {f.name}"
            assert para_count >= 0, f"get_paragraph_count must be >= 0 for {f.name}"
            assert isinstance(texts, list), f"extract_text must be list for {f.name}"
            assert isinstance(meta, dict), f"get_metadata must be dict for {f.name}"
            assert isinstance(freq, dict), f"word_frequency must be dict for {f.name}"
            records.append({
                "file": f.name,
                "section_count": sec_count,
                "paragraph_count": para_count,
                "text_block_count": len(texts),
                "metadata_key_count": len(meta),
                "unique_word_freq_count": len(freq),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            sec_count = get_section_count(path)
            para_count = get_paragraph_count(path)
            records.append({
                "file": f.name,
                "section_count": sec_count,
                "paragraph_count": para_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["section_count"] == back["section_count"]
            assert orig["paragraph_count"] == back["paragraph_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        sec_count = get_section_count(sample)
        texts = extract_text(sample)
        records = [{"file": "sample.abw", "section_count": sec_count, "text_block_count": len(texts)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_section_metadata_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            sec_count = get_section_count(path)
            para_count = get_paragraph_count(path)
            meta = get_metadata(path)
            texts = extract_text(path)
            assert sec_count >= 0
            assert para_count >= 0
            assert isinstance(meta, dict)
            assert isinstance(texts, list)
            records.append({
                "file": f.name,
                "section_count": sec_count,
                "paragraph_count": para_count,
                "metadata_key_count": len(meta),
                "text_block_count": len(texts),
                "format": "abw",
            })
        dest = tmp_path / "section-metadata.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(r["section_count"] >= 0 for r in loaded)

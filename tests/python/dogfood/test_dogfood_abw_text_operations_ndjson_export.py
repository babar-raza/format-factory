"""
tests/python/dogfood/test_dogfood_abw_text_operations_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-75
Dogfood export: ABW parse -> text operations -> write as NDJSON -> verify.
Uses: load, export_to_csv, export_to_markdown, abw_min_paragraph_length,
abw_has_content, join_paragraphs, split_paragraphs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    export_to_csv,
    export_to_markdown,
    abw_min_paragraph_length,
    abw_has_content,
    join_paragraphs,
    split_paragraphs,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _valid_abw_files():
    return sorted(_ABW_DIR.glob("*.abw"))


class TestAbwTextOperationsNdjsonExport:
    """ABW -> text operations -> NDJSON export -> roundtrip verification."""

    def test_export_basics(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        csv_str = export_to_csv(sample)
        model = load(sample)
        md_str = export_to_markdown(model)
        assert isinstance(csv_str, str)
        assert isinstance(md_str, str)

    def test_paragraph_ops_basics(self):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        min_len = abw_min_paragraph_length(sample)
        has_content = abw_has_content(sample)
        model = load(sample)
        joined = join_paragraphs(model)
        assert min_len >= 0
        assert isinstance(has_content, bool)
        assert isinstance(joined, str)

    def test_text_operations_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            csv_str = export_to_csv(path)
            md_str = export_to_markdown(model)
            min_len = abw_min_paragraph_length(path)
            has_content = abw_has_content(path)
            joined = join_paragraphs(model)
            chunks = split_paragraphs(model, 2) if model.get("paragraphs") else []
            assert isinstance(csv_str, str), f"export_to_csv must be str for {f.name}"
            assert isinstance(md_str, str), f"export_to_markdown must be str for {f.name}"
            assert min_len >= 0, f"abw_min_paragraph_length must be >= 0 for {f.name}"
            assert isinstance(has_content, bool), f"abw_has_content must be bool for {f.name}"
            assert isinstance(joined, str), f"join_paragraphs must be str for {f.name}"
            assert isinstance(chunks, list), f"split_paragraphs must be list for {f.name}"
            records.append({
                "file": f.name,
                "csv_length": len(csv_str),
                "markdown_length": len(md_str),
                "min_paragraph_length": min_len,
                "has_content": has_content,
                "joined_length": len(joined),
                "chunk_count": len(chunks),
                "source_format": "abw",
            })
        dest = tmp_path / "abw-text-ops.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            csv_str = export_to_csv(path)
            min_len = abw_min_paragraph_length(path)
            records.append({
                "file": f.name,
                "csv_length": len(csv_str),
                "min_paragraph_length": min_len,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["csv_length"] == back["csv_length"]
            assert orig["min_paragraph_length"] == back["min_paragraph_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ABW_DIR.glob("*.abw")))
        csv_str = export_to_csv(sample)
        has_content = abw_has_content(sample)
        records = [{"file": "sample.abw", "csv_length": len(csv_str), "has_content": has_content}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_markdown_join_export(self, tmp_path):
        records = []
        for f in _valid_abw_files():
            path = str(f)
            model = load(path)
            md_str = export_to_markdown(model)
            joined = join_paragraphs(model)
            has_content = abw_has_content(path)
            assert isinstance(md_str, str)
            assert isinstance(joined, str)
            assert isinstance(has_content, bool)
            records.append({
                "file": f.name,
                "markdown_length": len(md_str),
                "joined_length": len(joined),
                "has_content": has_content,
                "format": "abw",
            })
        dest = tmp_path / "markdown-join.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "abw" for r in loaded)
        assert all(isinstance(r["has_content"], bool) for r in loaded)

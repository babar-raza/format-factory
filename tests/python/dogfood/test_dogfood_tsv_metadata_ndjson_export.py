"""
tests/python/dogfood/test_dogfood_tsv_metadata_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-14
Dogfood export: TSV parse -> extract metadata -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import parse_tsv, count_rows, column_count, count_distinct_values
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    """Return TSV files that are valid (skip known invalid)."""
    return [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]


class TestTsvMetadataNdjsonExport:
    """TSV -> metadata extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_tsv_sample(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        doc = parse_tsv(sample)
        assert isinstance(doc, dict)

    def test_row_and_column_counts(self):
        sample = str(_TSV_DIR / "minimal-2x2.tsv")
        assert count_rows(sample) >= 1
        assert column_count(sample) >= 1

    def test_metadata_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            records.append({
                "file": f.name,
                "rows": count_rows(str(f)),
                "cols": column_count(str(f)),
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-metadata.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            records.append({
                "file": f.name,
                "rows": count_rows(str(f)),
                "cols": column_count(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["rows"] == back["rows"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_TSV_DIR / "single-cell.tsv")
        records = [{"file": "single-cell.tsv", "rows": count_rows(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_multi_column_metadata(self, tmp_path):
        sample = str(_TSV_DIR / "multi-column.tsv")
        record = {
            "file": "multi-column.tsv",
            "rows": count_rows(sample),
            "cols": column_count(sample),
            "format": "tsv",
        }
        dest = tmp_path / "multi.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["cols"] >= 2
        assert loaded[0]["format"] == "tsv"

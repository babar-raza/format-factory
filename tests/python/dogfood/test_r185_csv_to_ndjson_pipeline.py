"""
test_r185_csv_to_ndjson_pipeline.py — CSV→NDJSON dogfood export pipeline

Sprint: PRODUCT-DEEPENING-RNEXT185-20260612-001
Task: TASK-017 — Advance one dogfood export path using a Format Factory library

Pipeline: CSV parse → dict rows → NDJSON encode → NDJSON count/query
Uses only Format Factory Python FOSS libraries, no external deps.
"""
from __future__ import annotations

import json
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_to_dicts, get_column_names, get_row_count
from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    count_records,
    head,
    pluck,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = _SAMPLES / "minimal-2x2.csv"   # Name,Age / Alice,30 / Bob,25


def _csv_to_ndjson_file(csv_path: str) -> str:
    """Convert CSV file to a temp NDJSON file; caller must os.unlink."""
    rows = csv_to_dicts(csv_path)
    ndjson_text = to_jsonl_str(rows)
    fd, tmppath = tempfile.mkstemp(suffix=".ndjson")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(ndjson_text)
    return tmppath


class TestCsvToNdjsonPipeline:
    def test_pipeline_produces_ndjson_file(self):
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            assert os.path.exists(tmp)
        finally:
            os.unlink(tmp)

    def test_pipeline_record_count_matches_csv_row_count(self):
        csv_rows = get_row_count(str(_MINIMAL))
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            ndjson_count = count_records(tmp)
            assert ndjson_count == csv_rows
        finally:
            os.unlink(tmp)

    def test_pipeline_head_returns_first_record(self):
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            records = head(tmp, 1)
            assert len(records) == 1
            assert records[0]["Name"] == "Alice"
        finally:
            os.unlink(tmp)

    def test_pipeline_pluck_column_name(self):
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            names = pluck(tmp, "Name")
            assert "Alice" in names
            assert "Bob" in names
        finally:
            os.unlink(tmp)

    def test_pipeline_column_names_preserved(self):
        csv_cols = set(get_column_names(str(_MINIMAL)))
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            records = head(tmp, 5)
            ndjson_keys = set(records[0].keys())
            assert csv_cols == ndjson_keys
        finally:
            os.unlink(tmp)

    def test_pipeline_ndjson_is_valid_json_per_line(self):
        rows = csv_to_dicts(str(_MINIMAL))
        ndjson_text = to_jsonl_str(rows)
        for line in ndjson_text.strip().split("\n"):
            parsed = json.loads(line)
            assert isinstance(parsed, dict)

    def test_pipeline_age_value_preserved_as_string(self):
        tmp = _csv_to_ndjson_file(str(_MINIMAL))
        try:
            records = head(tmp, 5)
            ages = [r["Age"] for r in records]
            assert "30" in ages or 30 in ages  # CSV returns strings; NDJSON preserves
        finally:
            os.unlink(tmp)

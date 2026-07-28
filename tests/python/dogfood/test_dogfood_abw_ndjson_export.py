"""
test_dogfood_abw_ndjson_export.py -- Dogfood export path proof.

Sprint: REWORK-MEGATRAIN-CONTINUATION-001
TASK-017: Advance one dogfood export path using a Format Factory library.
Added: 2026-06-10

Uses ABW and NDJSON codecs to create data, export to CSV, and verify
the exported CSV is valid and parseable.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import create_abw, write_abw, export_to_csv as abw_export_csv
from src.python.ndjson.ndjson_codec import (
    load_ndjson,
    to_jsonl_str,
    export_to_csv as ndjson_export_csv,
)
from src.python.ff_csv.csv_parser import parse_csv


def _write_file(content: str, suffix: str) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_abw_to_csv_dogfood():
    """Create ABW document, write to file, export to CSV, parse the CSV."""
    model = create_abw(["Revenue Report", "Q1: $100k", "Q2: $150k", "Q3: $200k"])
    with tempfile.TemporaryDirectory() as tmp:
        abw_path = Path(tmp) / "report.abw"
        write_abw(model, abw_path)
        csv_text = abw_export_csv(abw_path)
        assert isinstance(csv_text, str)
        assert len(csv_text) > 0
        # Write CSV and parse it back
        csv_path = _write_file(csv_text, ".csv")
        try:
            result = parse_csv(csv_path)
            assert isinstance(result, dict)
            assert result["row_count"] >= 1
        finally:
            csv_path.unlink(missing_ok=True)


def test_ndjson_to_csv_dogfood():
    """Create NDJSON data, export to CSV, parse the CSV."""
    records = [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 87},
        {"name": "Carol", "score": 92},
    ]
    ndjson_text = to_jsonl_str(records)
    ndjson_path = _write_file(ndjson_text, ".ndjson")
    try:
        csv_text = ndjson_export_csv(ndjson_path)
        assert isinstance(csv_text, str)
        assert "Alice" in csv_text
        # Write CSV and parse it back
        csv_path = _write_file(csv_text, ".csv")
        try:
            result = parse_csv(csv_path)
            assert result["row_count"] >= 3
        finally:
            csv_path.unlink(missing_ok=True)
    finally:
        ndjson_path.unlink(missing_ok=True)


def test_ndjson_roundtrip_then_csv():
    """NDJSON load -> serialize -> reload -> export CSV pipeline."""
    records = [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}]
    ndjson_text = to_jsonl_str(records)
    path = _write_file(ndjson_text, ".ndjson")
    try:
        loaded = load_ndjson(path)
        assert len(loaded) == 2
        csv_out = ndjson_export_csv(path)
        assert "1" in csv_out
        assert "2" in csv_out
    finally:
        path.unlink(missing_ok=True)

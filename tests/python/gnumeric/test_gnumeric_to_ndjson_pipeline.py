"""
test_gnumeric_to_ndjson_pipeline.py -- Dogfood Gnumeric to NDJSON records pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-41
Tests export_to_csv from Gnumeric, build NDJSON records from Gnumeric data,
write+reload, get_record_count, and filter on exported records.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    get_sheet_names,
    load,
    get_sheet_as_rows,
)
from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    get_record_count,
    filter_records,
    sum_field,
)

_SHEETS = [
    {
        "name": "Sales",
        "rows": [
            ["product", "qty", "price"],
            ["Widget", "10", "5.0"],
            ["Gadget", "20", "3.5"],
            ["Doohickey", "5", "12.0"],
        ],
    }
]
_MODEL = create_gnumeric(_SHEETS)


def _write_gnumeric(tmp_path):
    dest = tmp_path / "sales.gnumeric"
    write_gnumeric(_MODEL, str(dest))
    return dest


def test_gnumeric_csv_export_has_header(tmp_path):
    dest = _write_gnumeric(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "product" in csv_str
    assert "Widget" in csv_str


def _gnumeric_to_records(dest):
    """Load gnumeric file and convert first sheet rows to list of dicts."""
    model = load(str(dest))
    all_rows = get_sheet_as_rows(model, 0)
    headers = all_rows[0]
    return [dict(zip(headers, row)) for row in all_rows[1:]]


def test_gnumeric_to_ndjson_record_count(tmp_path):
    dest = _write_gnumeric(tmp_path)
    records = _gnumeric_to_records(dest)
    ndjson_dest = tmp_path / "records.ndjson"
    write_ndjson(records, str(ndjson_dest))
    assert get_record_count(str(ndjson_dest)) == 3


def test_gnumeric_to_ndjson_field_present(tmp_path):
    dest = _write_gnumeric(tmp_path)
    records = _gnumeric_to_records(dest)
    ndjson_dest = tmp_path / "records.ndjson"
    write_ndjson(records, str(ndjson_dest))
    loaded = load_ndjson(str(ndjson_dest))
    assert loaded[0]["product"] == "Widget"


def test_gnumeric_to_ndjson_filter(tmp_path):
    dest = _write_gnumeric(tmp_path)
    records = _gnumeric_to_records(dest)
    ndjson_dest = tmp_path / "records.ndjson"
    write_ndjson(records, str(ndjson_dest))
    filtered = filter_records(str(ndjson_dest), "product", "Gadget")
    assert len(filtered) == 1
    assert filtered[0]["qty"] == "20"


def test_gnumeric_sheet_names(tmp_path):
    dest = _write_gnumeric(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Sales" in names

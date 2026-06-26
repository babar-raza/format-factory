"""
NDJSON example: Read, query, and export Newline-Delimited JSON records.

Usage:
    python read_and_query.py [path/to/file.ndjson]

If no path is given, creates a minimal in-memory example.
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
try:
    from ndjson import (
    load_ndjson,
    write_ndjson,
    probe_ndjson,
    get_record_count,
    get_field_names,
    filter_records,
    field_stats,
)
except ImportError:
    sys.path.insert(0, str(_REPO))
    from src.python.ndjson import (
        load_ndjson,
        write_ndjson,
        probe_ndjson,
        get_record_count,
        get_field_names,
        filter_records,
        field_stats,
    )


# --- Create or use sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    cleanup = False
else:
    # Create a minimal sample in temp
    sample_path = tempfile.mktemp(suffix=".ndjson")
    cleanup = True
    records = [
        {"id": 1, "name": "Alice", "score": 95.0},
        {"id": 2, "name": "Bob", "score": 82.5},
        {"id": 3, "name": "Carol", "score": 91.0},
        {"id": 4, "name": "Dave", "score": 78.0},
    ]
    write_ndjson(records, sample_path)

try:
    # --- Probe ---
    is_valid = probe_ndjson(sample_path)
    print(f"File: {sample_path}")
    print(f"  Valid NDJSON: {is_valid}")

    # --- Basic stats ---
    count = get_record_count(sample_path)
    fields = get_field_names(sample_path)
    print(f"  Record count: {count}")
    print(f"  Fields: {fields}")

    # --- Load records ---
    records = load_ndjson(sample_path)
    print(f"\n  First record: {records[0]}")

    # --- Filter ---
    high_scorers = filter_records(sample_path, lambda r: r.get("score", 0) >= 85)
    print(f"\n  Records with score >= 85: {len(high_scorers)}")
    for r in high_scorers:
        print(f"    {r}")

    # --- Field statistics ---
    if "score" in fields:
        stats = field_stats(sample_path, "score")
        print(f"\n  Score field stats: {stats}")

finally:
    if cleanup and os.path.exists(sample_path):
        os.unlink(sample_path)

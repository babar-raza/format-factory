"""
TSV example: Read, transform, and export Tab-Separated Values data.

Usage:
    python read_and_transform.py [path/to/file.tsv]

If no path is given, creates a minimal in-memory example.
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
try:
    from tsv import (
    load_tsv,
    write_tsv,
    probe_tsv,
    get_headers,
    count_rows,
)
except ImportError:
    sys.path.insert(0, str(_REPO))
    from src.python.tsv import (
        load_tsv,
        write_tsv,
        probe_tsv,
        get_headers,
        count_rows,
    )


# --- Create or use sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    cleanup = False
else:
    sample_path = tempfile.mktemp(suffix=".tsv")
    cleanup = True
    headers = ["name", "department", "salary"]
    rows = [
        ["Alice", "Engineering", "95000"],
        ["Bob", "Marketing", "82000"],
        ["Carol", "Engineering", "91000"],
        ["Dave", "Marketing", "78000"],
        ["Eve", "Engineering", "105000"],
    ]
    write_tsv(rows, sample_path, headers=headers)

try:
    # --- Probe ---
    probe_result = probe_tsv(sample_path)
    print(f"File: {sample_path}")
    print(f"  Valid TSV: {probe_result.get('delimiter') == chr(9) if isinstance(probe_result, dict) else probe_result}")

    # --- Basic stats ---
    headers = get_headers(sample_path)
    row_count = count_rows(sample_path)
    print(f"  Headers: {headers}")
    print(f"  Row count: {row_count}")

    # --- Load model ---
    model = load_tsv(sample_path)
    data_rows = model["rows"]
    print(f"\n  First row: {data_rows[0]}")

    # --- Filter Engineering rows ---
    if headers and "department" in headers:
        dept_idx = headers.index("department")
        eng_rows = [r for r in data_rows if r[dept_idx] == "Engineering"]
        print(f"\n  Engineering rows: {len(eng_rows)}")
        for r in eng_rows:
            print(f"    {r}")

    # --- Transform: add 10% bonus column ---
    if headers and "salary" in headers:
        sal_idx = headers.index("salary")
        bonus_rows = []
        for r in data_rows:
            try:
                bonus = str(int(int(r[sal_idx]) * 0.10))
            except (ValueError, IndexError):
                bonus = "0"
            bonus_rows.append(r + [bonus])
        bonus_headers = headers + ["bonus"]

        out_path = tempfile.mktemp(suffix="_with_bonus.tsv")
        write_tsv(bonus_rows, out_path, headers=bonus_headers)
        print(f"\n  Wrote transformed file with bonus column: {out_path}")
        out_headers = get_headers(out_path)
        print(f"  Output headers: {out_headers}")
        os.unlink(out_path)

finally:
    if cleanup and os.path.exists(sample_path):
        os.unlink(sample_path)

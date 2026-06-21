"""
SYLK example: Read, inspect, and query Symbolic Link (SYLK) spreadsheet data.

Usage:
    python read_and_inspect.py [path/to/file.slk]

If no path is given, creates a minimal in-memory example.
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "sylk"))

import sylk_parser as sylk

# --- Create or use sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
    cleanup = False
else:
    sample_path = tempfile.mktemp(suffix=".slk")
    cleanup = True
    content = (
        "ID;P\n"
        'C;X1;Y1;K"Product"\n'
        'C;X2;Y1;K"Units"\n'
        'C;X3;Y1;K"Revenue"\n'
        'C;X1;Y2;K"Widget"\n'
        "C;X2;Y2;K120\n"
        "C;X3;Y2;K3600\n"
        'C;X1;Y3;K"Gadget"\n'
        "C;X2;Y3;K85\n"
        "C;X3;Y3;K4250\n"
        'C;X1;Y4;K"Doohickey"\n'
        "C;X2;Y4;K200\n"
        "C;X3;Y4;K5000\n"
        "E"
    )
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(content)

try:
    # --- Probe ---
    probe = sylk.probe_sylk(sample_path)
    print(f"File: {sample_path}")
    print(f"  Valid header: {probe.get('valid_header')}")
    print(f"  ID line: {probe.get('id_line')}")

    # --- Parse ---
    doc = sylk.parse_sylk(sample_path)
    print(f"\n  Parse OK: {doc.get('ok')}")
    print(f"  Cell count: {doc.get('cell_count')}")

    # --- Shape analytics ---
    rows = sylk.get_row_count(sample_path)
    cols = sylk.get_column_count(sample_path)
    is_rect = sylk.sylk_is_rectangular(sample_path)
    has_hdr = sylk.sylk_has_header(sample_path)
    print(f"\n  Rows: {rows}  Cols: {cols}  Rectangular: {is_rect}  Has header: {has_hdr}")

    # --- Cell values ---
    all_vals = sylk.get_all_values(sample_path)
    print(f"\n  All values ({len(all_vals)}): {all_vals}")

    col_vals = sylk.get_column_values(sample_path, 2)
    print(f"\n  Column 2 (Units): {col_vals}")

    # --- Numeric analytics ---
    numeric_count = sylk.sylk_numeric_cell_count(sample_path)
    numeric_sum = sylk.sylk_numeric_sum(sample_path)
    numeric_min = sylk.sylk_min_numeric_value(sample_path)
    numeric_max = sylk.sylk_max_numeric_value(sample_path)
    print(f"\n  Numeric cells: {numeric_count}")
    print(f"  Sum of all numeric values: {numeric_sum}")
    print(f"  Min numeric value: {numeric_min}")
    print(f"  Max numeric value: {numeric_max}")

    # --- Density analytics ---
    density = sylk.sylk_data_density(sample_path)
    nonempty_ratio = sylk.sylk_nonempty_cell_ratio(sample_path)
    print(f"\n  Data density: {density:.3f}  Non-empty ratio: {nonempty_ratio:.3f}")

    # --- Capabilities ---
    caps = sylk.get_capabilities()
    print(f"\n  Format: {caps.get('format')}  Version: {caps.get('version')}")
    print(f"  Operations: {caps.get('operations', [])[:5]}")

finally:
    if cleanup and os.path.exists(sample_path):
        os.unlink(sample_path)

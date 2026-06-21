"""
Gnumeric example: Read, inspect, and query multi-sheet Gnumeric spreadsheet data.

Usage:
    python read_and_inspect.py [path/to/file.gnumeric]

If no path is given, uses the bundled sample_sales_report.gnumeric.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import gnumeric

# --- Select file ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
else:
    sample_path = str(Path(__file__).parent / "sample_sales_report.gnumeric")

print(f"File: {sample_path}")

# --- Probe ---
valid = gnumeric.probe_gnumeric(sample_path)
print(f"  Valid gnumeric: {valid}")

# --- Load model ---
model = gnumeric.load(sample_path)
print(f"  Parse OK: {'is_gnumeric' in model}")
print(f"  Sheet count: {model.get('sheet_count')}")

# --- Sheet names ---
sheet_names = gnumeric.get_sheet_names(sample_path)
print(f"  Sheet names: {sheet_names}")
is_multi = gnumeric.gnumeric_is_multi_sheet(sample_path)
print(f"  Is multi-sheet: {is_multi}")

# --- Sheet 0 dimensions ---
rows = gnumeric.get_row_count(model, 0)
cols = gnumeric.get_column_count(model, 0)
print(f"\n  Sheet '{sheet_names[0]}': {rows} rows x {cols} cols")

# --- Cell analytics for sheet 0 ---
numeric_count = gnumeric.gnumeric_numeric_cell_count(model, 0)
summary = gnumeric.gnumeric_sheet_summary(model, 0)
print(f"  Numeric cells: {numeric_count}")
print(f"  Sheet summary: {summary}")

# --- File-level analytics ---
total_sum = gnumeric.gnumeric_numeric_sum_all(sample_path)
density = gnumeric.gnumeric_data_density(sample_path)
nonempty_ratio = gnumeric.gnumeric_nonempty_cell_ratio(sample_path)
print(f"\n  Sum of all numeric values: {total_sum}")
print(f"  Data density: {density:.3f}")
print(f"  Non-empty cell ratio: {nonempty_ratio:.3f}")

# --- Sheet metadata for all sheets ---
meta = gnumeric.get_sheet_metadata(sample_path)
print(f"\n  Sheet metadata ({len(meta)} sheets):")
for m in meta:
    print(f"    Sheet '{m['name']}': {m['cell_count']} cells")

# --- CSV export of sheet 0 ---
csv_out = gnumeric.export_to_csv(sample_path, sheet_index=0)
lines = csv_out.strip().splitlines()
print(f"\n  CSV export of '{sheet_names[0]}' ({len(lines)} rows):")
for line in lines[:3]:
    print(f"    {line}")
if len(lines) > 3:
    print(f"    ... ({len(lines) - 3} more rows)")

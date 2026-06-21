"""
FODS example: Read and inspect a Flat OpenDocument Spreadsheet.

Usage:
    python read_and_inspect.py [path/to/file.fods]

If no path is given, uses the built-in minimal sample.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict

# --- Locate sample ---
if len(sys.argv) > 1:
    sample_path = sys.argv[1]
else:
    sample_path = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")

if not Path(sample_path).exists():
    print(f"File not found: {sample_path}")
    sys.exit(1)

# --- Parse the workbook ---
workbook = parse_fods_strict(sample_path)

# --- Inspect top-level info ---
print(f"Workbook: {sample_path}")
print(f"  Sheet count: {workbook['sheet_count']}")

# --- Inspect each sheet ---
for sheet in workbook.get("sheets", []):
    print(f"\n  Sheet: {sheet['name']!r}")
    rows = sheet.get("rows", [])
    print(f"    Row count: {len(rows)}")
    for row_idx, row in enumerate(rows):
        cells = row.get("cells", [])
        row_summary = []
        for cell in cells:
            vtype = cell.get("value_type", "?")
            value = cell.get("value")
            row_summary.append(f"{vtype}:{value!r}")
        print(f"    Row {row_idx}: {', '.join(row_summary)}")

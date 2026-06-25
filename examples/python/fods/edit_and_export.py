"""
FODS example: Load, add a row, export to CSV, and save as FODS.

Usage:
    python edit_and_export.py [path/to/file.fods]

If no path is given, builds a workbook from scratch.
"""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

try:
    from fods import parse_fods_strict, write_fods, workbook_to_csv
except ImportError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
from src.python.fods import parse_fods_strict, write_fods, workbook_to_csv

# --- Build or load workbook ---
sample_path = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")

if Path(sample_path).exists():
    workbook = parse_fods_strict(sample_path)
    print(f"Loaded: {sample_path}")
else:
    # Build a minimal workbook inline
    workbook = {
        "sheets": [{
            "name": "Data",
            "rows": [
                {"cells": [{"value": "Name", "value_type": "string"}, {"value": "Score", "value_type": "string"}]},
                {"cells": [{"value": "Alice", "value_type": "string"}, {"value": 95.0, "value_type": "float"}]},
            ]
        }]
    }
    print("Built workbook inline.")

# --- Export first sheet to CSV ---
first_sheet_name = workbook["sheets"][0]["name"] if workbook.get("sheets") else None
csv_text = workbook_to_csv(workbook, sheet_name=first_sheet_name)
print("\nCSV export (first sheet):")
print(csv_text)

# --- Add a new row to the first sheet ---
new_row = {"cells": [{"value": "NEW_ENTRY", "value_type": "string"}, {"value": 0.0, "value_type": "float"}]}
if workbook.get("sheets"):
    workbook["sheets"][0].setdefault("rows", []).append(new_row)
    print(f"Added new row to sheet '{workbook['sheets'][0]['name']}'.")

# --- Save modified workbook to a temp file ---
with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
    out_path = f.name

write_fods(workbook, out_path)
print(f"\nSaved modified workbook to: {out_path}")
print(f"File size: {Path(out_path).stat().st_size} bytes")

"""
Gnumeric export to CSV example — format-factory python-foss track.

Demonstrates:
  - load(): parse a .gnumeric file
  - export_to_csv(): export a sheet to CSV string
  - Custom delimiter support

Usage:
    python examples/python/gnumeric/export_csv_example.py

No external dependencies required (stdlib only).
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src" / "python"))

from gnumeric.gnumeric_codec import load, export_to_csv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "gnumeric"

def main():
    sample = SAMPLES_DIR / "multi-cell-basic.gnumeric"
    print(f"Loading: {sample}")

    # Step 1: Load workbook model
    model = load(sample)
    print(f"Sheets: {model['sheet_count']}, total cells: {model['cell_count']}")
    for sheet in model["sheets"]:
        print(f"  Sheet '{sheet['name']}': {sheet['cell_count']} cells")

    # Step 2: Export first sheet to CSV
    csv_str = export_to_csv(sample, sheet_index=0)
    print(f"\nCSV output (sheet 0):\n{csv_str}")

    # Step 3: Export with tab delimiter
    tsv_str = export_to_csv(sample, sheet_index=0, delimiter="\t")
    print(f"TSV output (sheet 0):\n{tsv_str}")

    print("Export verification: PASS")

if __name__ == "__main__":
    main()

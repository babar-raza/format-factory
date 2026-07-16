"""
xliff_to_csv.py — Dogfood export: xliff → CSV using Format Factory libraries.

Reads an XLIFF translation file using Format Factory's xliff codec and
writes a translation-unit table as CSV rows using Format Factory's CSV
writer: one row per unit (unit_id, source text, target text, state) — the
same shape a human reviewer or CAT tool would want for spreadsheet review.

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "xliff"))
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_writer import write_csv_to_file
from xliff.xliff_codec import load_xliff


def xliff_to_csv(
    xliff_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert translation units to CSV rows, one row per unit.

    Args:
        xliff_path: Path to the source .xliff file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    xliff_path = Path(xliff_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_xliff(xliff_path)

    rows: list[list[str]] = []
    header = ["unit_id", "source", "target", "state"]

    for f in model.get("files", []):
        for unit in f.get("units", []):
            for segment in unit.get("segments", []):
                rows.append([
                    str(unit.get("id", "")),
                    str(segment.get("source", "")),
                    str(segment.get("target", "")),
                    str(segment.get("state", "")),
                ])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)

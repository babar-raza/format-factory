"""
ubl_to_csv.py — Dogfood export: ubl → CSV using Format Factory libraries.

Reads a UBL Invoice/CreditNote/Order using Format Factory's ubl codec and
writes its line items as CSV rows using Format Factory's CSV writer: one
row per line (id, quantity, amount, item_name) — the accounting/ERP
integration shape.

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "ubl"))
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_writer import write_csv_to_file
from ubl.ubl_codec import load_ubl


def ubl_to_csv(
    ubl_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert UBL line items to CSV rows, one row per line.

    Args:
        ubl_path: Path to the source UBL .xml file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    ubl_path = Path(ubl_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_ubl(ubl_path)
    lines = model.get("lines", [])

    rows: list[list[str]] = []
    header = ["id", "quantity", "amount", "item_name"]

    for line in lines:
        rows.append([
            str(line.get("id", "")),
            str(line.get("quantity", "")),
            str(line.get("amount", "")),
            str(line.get("item_name", "")),
        ])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)

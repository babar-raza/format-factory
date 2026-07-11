"""
ndjson_to_dif.py — Dogfood export: NDJSON → DIF using Format Factory libraries.

Sprint: NDJSON-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import load_ndjson  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def ndjson_to_dif(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "NDJSON Export",
) -> int:
    """Convert an NDJSON file to a DIF file, one row per record."""
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    dif_rows = []
    for rec in records:
        if isinstance(rec, dict):
            cells = [DifCell(value=f"{k}={v}", value_type="string") for k, v in rec.items()]
        else:
            cells = [DifCell(value=str(rec), value_type="string")]
        dif_rows.append(cells)

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["ndjson_to_dif"]

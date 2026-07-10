"""
abw_to_ndjson.py

Dogfood export: ABW -> NDJSON

Converts an AbiWord (.abw) document into NDJSON records using:
  - Format Factory abw library (load) as the source reader
  - Format Factory ndjson library (write_ndjson) as the target writer

Each non-empty paragraph in the ABW document becomes one NDJSON record.

Sprint: ABW-TO-NDJSON-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-NDJSON-DOGFOOD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "abw"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))

from abw.abw_codec import load as load_abw  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def abw_to_ndjson(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    include_paragraph_index: bool = True,
    skip_empty: bool = True,
) -> int:
    """
    Convert an ABW document to NDJSON records using Format Factory writers.

    Each paragraph in the ABW document becomes one NDJSON record with
    fields: paragraph_index, text.

    Parameters
    ----------
    abw_path:
        Path to the source .abw file.
    dest_path:
        Path to write the target .ndjson file.
    include_paragraph_index:
        If True, adds a 0-based paragraph_index field to each record.
    skip_empty:
        If True (default), paragraphs with empty text are skipped.

    Returns
    -------
    int
        Number of NDJSON records written.
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)

    model = load_abw(abw_path)  # Format Factory abw reader
    paragraphs: list[str] = model.get("paragraphs", [])

    records: list[dict] = []
    para_idx = 0
    for text in paragraphs:
        if skip_empty and not text:
            para_idx += 1
            continue
        record: dict = {"text": text}
        if include_paragraph_index:
            record["paragraph_index"] = para_idx
        records.append(record)
        para_idx += 1

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    write_ndjson(records, dest_path)  # Format Factory ndjson writer
    return len(records)


__all__ = ["abw_to_ndjson"]

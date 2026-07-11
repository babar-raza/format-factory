"""
tsv_to_toml.py — Dogfood export: TSV → TOML using Format Factory libraries.

Reads a TSV file using Format Factory's TSV parser and writes the rows
as a TOML file using Format Factory's TOML writer.

Each TSV row (with its header) becomes a [[rows]] array table entry in TOML.

Sprint: TSV-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def tsv_to_toml(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "rows",
) -> int:
    """Convert a TSV file to a TOML file, one [[rows]] entry per data row.

    Headers become the TOML key names within each array table entry.
    When no headers are present, columns are named col_0, col_1, etc.

    Args:
        tsv_path: Path to the source .tsv file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of data rows written.
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    toml_rows = []
    for row in rows:
        if headers:
            entry = {headers[i]: str(row[i]) if i < len(row) else "" for i in range(len(headers))}
        else:
            entry = {f"col_{i}": str(v) for i, v in enumerate(row)}
        toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(rows)


__all__ = ["tsv_to_toml"]

"""
ipynb_to_csv.py — Dogfood export: ipynb → CSV using Format Factory libraries.

Reads a Jupyter Notebook using Format Factory's ipynb codec and writes a
cell inventory as CSV rows using Format Factory's CSV writer: one row per
cell (index, cell_type, a source preview, and output count).

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ipynb.ipynb_codec import load_ipynb
from ff_csv.csv_writer import write_csv_to_file

_PREVIEW_LEN = 60


def _source_preview(source) -> str:
    text = "".join(source) if isinstance(source, list) else str(source or "")
    text = text.replace("\n", " ").strip()
    return text[:_PREVIEW_LEN]


def ipynb_to_csv(
    ipynb_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert notebook cells to CSV rows, one row per cell.

    Args:
        ipynb_path: Path to the source .ipynb file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    ipynb_path = Path(ipynb_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_ipynb(ipynb_path)
    cells = model.get("cells", [])

    rows: list[list[str]] = []
    header = ["index", "cell_type", "source_preview", "output_count"]

    for idx, cell in enumerate(cells):
        outputs = cell.get("outputs", []) or []
        rows.append([
            str(idx),
            str(cell.get("cell_type", "")),
            _source_preview(cell.get("source")),
            str(len(outputs)),
        ])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)

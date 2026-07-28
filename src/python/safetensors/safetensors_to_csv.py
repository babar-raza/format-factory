"""
safetensors_to_csv.py — Dogfood export: safetensors → CSV using Format
Factory libraries.

Reads a SafeTensors checkpoint using Format Factory's safetensors codec and
writes a tensor manifest as CSV rows using Format Factory's CSV writer: one
row per tensor (name, dtype, shape, byte size).

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from safetensors.safetensors_codec import load_safetensors
from ff_csv.csv_writer import write_csv_to_file


def safetensors_to_csv(
    safetensors_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert a tensor manifest to CSV rows, one row per tensor.

    Args:
        safetensors_path: Path to the source .safetensors file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    safetensors_path = Path(safetensors_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_safetensors(safetensors_path)
    tensors = model.get("tensors", {})

    rows: list[list[str]] = []
    header = ["name", "dtype", "shape", "byte_size"]

    for name, info in tensors.items():
        offsets = info.get("data_offsets", [0, 0])
        byte_size = offsets[1] - offsets[0] if len(offsets) == 2 else 0
        shape = "x".join(str(s) for s in info.get("shape", []))
        rows.append([name, str(info.get("dtype", "")), shape, str(byte_size)])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)

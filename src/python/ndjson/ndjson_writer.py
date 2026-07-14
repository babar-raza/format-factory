"""
ndjson_writer.py — NDJSON writer for format-factory-ndjson.

Public API:
  write_ndjson(records, path) — writes NDJSON to file
  write_ndjson_str(records)   — returns NDJSON string

Each record is serialized as a JSON object on its own line.
Raises NdjsonWriteError if any record is not JSON-serializable.
"""

from __future__ import annotations

import json
from pathlib import Path


class NdjsonWriteError(Exception):
    """Raised when NDJSON output fails."""


def write_ndjson_str(records: list[dict]) -> str:
    """Serialize records to NDJSON string (one JSON object per line).

    Args:
        records: List of dicts, each JSON-serializable.

    Returns:
        NDJSON string with LF line endings.

    Raises:
        NdjsonWriteError: If any record is not JSON-serializable.
    """
    if records is None:
        raise NdjsonWriteError("records must not be None")

    lines: list[str] = []
    for i, record in enumerate(records):
        try:
            lines.append(json.dumps(record, ensure_ascii=False))
        except (TypeError, ValueError) as exc:
            raise NdjsonWriteError(
                f"Record at index {i} is not JSON-serializable: {exc}"
            ) from exc

    return "\n".join(lines) + "\n" if lines else ""


def write_ndjson(records: list[dict], path: str | Path) -> None:
    """Write NDJSON records to a file. Creates parent dirs as needed. UTF-8, no BOM."""
    if not path:
        raise NdjsonWriteError("path must not be empty")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = write_ndjson_str(records)
    p.write_text(content, encoding="utf-8")

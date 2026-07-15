"""Jupyter Notebook (.ipynb) codec — probe, load, write.

Implements the minimum viable codec for nbformat v4.x notebooks.
Detection: valid JSON with ``nbformat`` key at root level.
Parsing: stdlib ``json`` module only.

Spec reference: FACT-IPYNB-001
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

from ipynb.exceptions import IpynbParseError, IpynbWriteError

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "nbformat_v4",
    "cell_types_code_markdown_raw",
    "cell_outputs",
    "notebook_metadata",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "nbformat_v1",
    "nbformat_v2",
    "nbformat_v3",
    "cell_attachments",
    "widget_state",
    "streaming_parse",
]

SourceType = Union[str, Path, bytes]


def _read_source(source: SourceType) -> str:
    """Read source into a string."""
    if isinstance(source, bytes):
        return source.decode("utf-8")
    path = Path(source)
    if path.exists():
        size = path.stat().st_size
        if size > MAX_FILE_SIZE:
            raise IpynbParseError(
                f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes"
            )
        return path.read_text(encoding="utf-8")
    if isinstance(source, str) and source.strip().startswith("{"):
        return source
    raise IpynbParseError(f"Cannot read source: {source!r}")


def probe_ipynb(source: SourceType) -> bool:
    """Return True if source is a valid Jupyter Notebook.

    Never raises — returns False on any error.
    """
    try:
        text = _read_source(source)
        data = json.loads(text)
        return isinstance(data, dict) and "nbformat" in data
    except Exception:
        return False


def load_ipynb(source: SourceType) -> dict[str, Any]:
    """Parse a Jupyter Notebook and return a canonical model dict.

    Returns a dict with keys: nbformat, nbformat_minor, metadata, cells.
    Each cell has: cell_type, source, metadata, and optionally outputs.
    """
    text = _read_source(source)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IpynbParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise IpynbParseError(f"Expected JSON object, got {type(data).__name__}")

    if "nbformat" not in data:
        raise IpynbParseError("Missing required key: nbformat")

    nbformat = data.get("nbformat", 0)
    nbformat_minor = data.get("nbformat_minor", 0)
    metadata = data.get("metadata", {})
    raw_cells = data.get("cells", [])

    cells: list[dict[str, Any]] = []
    for i, raw_cell in enumerate(raw_cells):
        if not isinstance(raw_cell, dict):
            raise IpynbParseError(f"Cell {i} is not a JSON object")
        cell: dict[str, Any] = {
            "cell_type": raw_cell.get("cell_type", "raw"),
            "source": raw_cell.get("source", ""),
            "metadata": raw_cell.get("metadata", {}),
        }
        if cell["cell_type"] == "code":
            cell["outputs"] = raw_cell.get("outputs", [])
            cell["execution_count"] = raw_cell.get("execution_count")
        cells.append(cell)

    return {
        "nbformat": nbformat,
        "nbformat_minor": nbformat_minor,
        "metadata": metadata,
        "cells": cells,
    }


def write_ipynb(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize a notebook model dict to nbformat v4 JSON.

    If dest is provided, writes to that path and returns the JSON string.
    Otherwise returns the JSON string only.
    """
    nbformat = model.get("nbformat", 4)
    nbformat_minor = model.get("nbformat_minor", 5)
    metadata = model.get("metadata", {})
    cells = model.get("cells", [])

    out_cells: list[dict[str, Any]] = []
    for cell in cells:
        out_cell: dict[str, Any] = {
            "cell_type": cell.get("cell_type", "raw"),
            "source": cell.get("source", ""),
            "metadata": cell.get("metadata", {}),
        }
        if out_cell["cell_type"] == "code":
            out_cell["outputs"] = cell.get("outputs", [])
            out_cell["execution_count"] = cell.get("execution_count")
        out_cells.append(out_cell)

    notebook = {
        "nbformat": nbformat,
        "nbformat_minor": nbformat_minor,
        "metadata": metadata,
        "cells": out_cells,
    }

    try:
        result = json.dumps(notebook, indent=1, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise IpynbWriteError(f"Cannot serialize notebook: {exc}") from exc

    if dest is not None:
        path = Path(dest)
        try:
            path.write_text(result + "\n", encoding="utf-8")
        except OSError as exc:
            raise IpynbWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_cell_count(model: dict[str, Any]) -> int:
    """Return the number of cells in a notebook model."""
    return len(model.get("cells", []))


def get_code_cells(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only code cells from a notebook model."""
    return [c for c in model.get("cells", []) if c.get("cell_type") == "code"]


def get_markdown_cells(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only markdown cells from a notebook model."""
    return [c for c in model.get("cells", []) if c.get("cell_type") == "markdown"]


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load a notebook, write it, and reload to prove round-trip fidelity."""
    model = load_ipynb(source)
    write_ipynb(model, dest)
    return load_ipynb(dest)


def ipynb_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for an ipynb source (installed-package proof)."""
    model = load_ipynb(source)
    return {
        "format": "ipynb",
        "loaded": True,
        "nbformat": model.get("nbformat"),
        "cell_count": get_cell_count(model),
        "code_cell_count": len(get_code_cells(model)),
        "markdown_cell_count": len(get_markdown_cells(model)),
    }

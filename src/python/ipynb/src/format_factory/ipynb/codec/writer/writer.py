"""Deterministic Jupyter Notebook JSON writer."""

from __future__ import annotations

import json
from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import Any, Mapping, TextIO

from ...errors import IpynbWriteError
from ...model import IpynbDocument
from ...security import IPYNB_DEFAULT_LIMITS
from ..reader import Source, ensure_cell_id, load

Destination = str | PathLike[str] | TextIO


def _as_mapping(value: IpynbDocument | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, IpynbDocument):
        return value.raw
    if isinstance(value, Mapping):
        return value
    raise TypeError("document must be an IpynbDocument or mapping")


def _profile_version(profile: str | None) -> tuple[int, int]:
    selected = profile or "4.5"
    if selected.startswith("nbformat-"):
        selected = selected.removeprefix("nbformat-")
    if selected not in {"4.0", "4.1", "4.2", "4.3", "4.4", "4.5"}:
        raise ValueError("profile must be one of nbformat 4.0 through 4.5")
    major, minor = selected.split(".", 1)
    return int(major), int(minor)


def _normalized(
    value: IpynbDocument | Mapping[str, Any], *, profile: str | None
) -> dict[str, Any]:
    source = deepcopy(dict(_as_mapping(value)))
    major, minor = _profile_version(profile)
    source["nbformat"] = major
    source["nbformat_minor"] = minor
    source.setdefault("metadata", {})
    raw_cells = source.setdefault("cells", [])
    if not isinstance(raw_cells, list):
        raise IpynbWriteError("cells must be an array")

    used_ids: set[str] = set()
    cells: list[dict[str, Any]] = []
    for index, raw_cell in enumerate(raw_cells):
        if not isinstance(raw_cell, dict):
            raise IpynbWriteError(f"cell {index} must be an object")
        cell = dict(raw_cell)
        cell.setdefault("cell_type", "raw")
        cell.setdefault("metadata", {})
        cell.setdefault("source", "")
        if cell["cell_type"] == "code":
            cell.setdefault("outputs", [])
            cell.setdefault("execution_count", None)
        if minor >= 5:
            ensure_cell_id(cell, used_ids)
        else:
            cell.pop("id", None)
        cells.append(cell)
    source["cells"] = cells
    return source


def dumps(
    document: IpynbDocument | Mapping[str, Any],
    *,
    profile: str | None = None,
) -> str:
    """Serialize a notebook with stable ordering and whitespace."""
    try:
        result = json.dumps(
            _normalized(document, profile=profile),
            ensure_ascii=False,
            indent=1,
            sort_keys=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("profile must"):
            raise
        raise IpynbWriteError(f"cannot serialize notebook: {exc}") from exc
    IPYNB_DEFAULT_LIMITS.enforce("max_output_bytes", len(result.encode("utf-8")))
    return result


def dump(
    document: IpynbDocument | Mapping[str, Any],
    destination: Destination,
    *,
    profile: str | None = None,
) -> None:
    text = dumps(document, profile=profile) + "\n"
    if hasattr(destination, "write"):
        try:
            written = destination.write(text)
        except (OSError, UnicodeError) as exc:
            raise IpynbWriteError(f"cannot write notebook: {exc}") from exc
        if written is not None and written != len(text):
            raise IpynbWriteError("notebook destination accepted a partial write")
        return
    path = Path(destination)
    try:
        path.write_text(text, encoding="utf-8", newline="\n")
    except (OSError, UnicodeError) as exc:
        raise IpynbWriteError(f"cannot write notebook to {path}: {exc}") from exc


def write_ipynb(
    model: IpynbDocument | Mapping[str, Any],
    dest: Destination | None = None,
) -> str:
    text = dumps(model)
    if dest is not None:
        dump(model, dest)
    return text


def get_cell_count(model: IpynbDocument | Mapping[str, Any]) -> int:
    return len(_as_mapping(model).get("cells", []))


def get_code_cells(
    model: IpynbDocument | Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        cell
        for cell in _as_mapping(model).get("cells", [])
        if isinstance(cell, dict) and cell.get("cell_type") == "code"
    ]


def get_markdown_cells(
    model: IpynbDocument | Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        cell
        for cell in _as_mapping(model).get("cells", [])
        if isinstance(cell, dict) and cell.get("cell_type") == "markdown"
    ]


def roundtrip(source: Source, dest: Destination) -> dict[str, Any]:
    document = load(source, mode="preservation")
    dump(document, dest)
    return load(dest, mode="preservation").raw


def ipynb_installed_workflow(source: Source) -> dict[str, Any]:
    document = load(source, mode="preservation")
    return {
        "format": "ipynb",
        "loaded": True,
        "nbformat": document.nbformat,
        "cell_count": document.cell_count,
        "code_cell_count": len(document.code_cells),
        "markdown_cell_count": len(document.markdown_cells),
    }

"""Bounded Jupyter Notebook JSON reader."""

from __future__ import annotations

import json
import hashlib
import re
from os import PathLike
from pathlib import Path
from typing import Any, TextIO

from format_factory.core import ProbeResult, ResourceLimits

from ...errors import IpynbParseError
from ...model import IpynbDocument
from ...security import effective_limits

CELL_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
Source = str | bytes | PathLike[str] | TextIO


def _depth(value: Any, current: int = 0) -> int:
    if isinstance(value, dict):
        return max((_depth(item, current + 1) for item in value.values()), default=current)
    if isinstance(value, list):
        return max((_depth(item, current + 1) for item in value), default=current)
    return current


def _read_source(source: Source, limits: ResourceLimits) -> str:
    if isinstance(source, bytes):
        limits.enforce("max_input_bytes", len(source))
        try:
            return source.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IpynbParseError(f"notebook is not valid UTF-8: {exc}") from exc
    if hasattr(source, "read"):
        text = source.read()
        if not isinstance(text, str):
            raise TypeError("notebook text stream read() must return str")
        limits.enforce("max_input_bytes", len(text.encode("utf-8")))
        return text
    if isinstance(source, str) and source.lstrip().startswith(("{", "[")):
        limits.enforce("max_input_bytes", len(source.encode("utf-8")))
        return source
    path = Path(source)
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise IpynbParseError(f"cannot read notebook source {source!r}: {exc}") from exc
    limits.enforce("max_input_bytes", size)
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise IpynbParseError(f"cannot read notebook source {source!r}: {exc}") from exc


def _generate_cell_id(used_ids: set[str]) -> str:
    return _generate_cell_id_for({}, used_ids)


def _generate_cell_id_for(
    cell: dict[str, Any], used_ids: set[str]
) -> str:
    """Return a deterministic valid ID for ``cell``.

    The collision counter is part of the digest input, so equivalent inputs
    produce equivalent normalized notebooks across clean runs.
    """
    canonical = json.dumps(
        {key: value for key, value in cell.items() if key != "id"},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=repr,
    ).encode("utf-8")
    counter = 0
    while True:
        digest = hashlib.sha256(canonical + counter.to_bytes(8, "big")).hexdigest()
        candidate = digest[:16]
        if candidate not in used_ids:
            return candidate
        counter += 1


def ensure_cell_id(cell: dict[str, Any], used_ids: set[str]) -> dict[str, Any]:
    cell_id = cell.get("id")
    if (
        not isinstance(cell_id, str)
        or CELL_ID_PATTERN.fullmatch(cell_id) is None
        or cell_id in used_ids
    ):
        cell_id = _generate_cell_id_for(cell, used_ids)
    cell["id"] = cell_id
    used_ids.add(cell_id)
    return cell


def _parse(
    text: str, *, mode: str, limits: ResourceLimits
) -> dict[str, Any]:
    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IpynbParseError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise IpynbParseError("notebook root must be a JSON object")
    if _depth(data) > limits.max_nesting_depth:
        raise IpynbParseError(
            f"notebook nesting exceeds configured limit {limits.max_nesting_depth}"
        )
    if "nbformat" not in data:
        raise IpynbParseError("missing required key: nbformat")
    major = data.get("nbformat")
    minor = data.get("nbformat_minor", 0)
    if isinstance(major, bool) or not isinstance(major, int):
        raise IpynbParseError("nbformat must be an integer")
    if isinstance(minor, bool) or not isinstance(minor, int) or minor < 0:
        raise IpynbParseError("nbformat_minor must be a non-negative integer")
    if mode == "strict" and (major != 4 or minor > 5):
        raise IpynbParseError(
            f"strict profile supports nbformat 4.0 through 4.5, got {major}.{minor}"
        )
    metadata = data.get("metadata", {})
    raw_cells = data.get("cells", [])
    if not isinstance(metadata, dict):
        raise IpynbParseError("metadata must be an object")
    if not isinstance(raw_cells, list):
        raise IpynbParseError("cells must be an array")

    notebook = dict(data)
    notebook["metadata"] = dict(metadata)
    cells: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for index, raw_cell in enumerate(raw_cells):
        if not isinstance(raw_cell, dict):
            raise IpynbParseError(f"cell {index} is not a JSON object")
        cell = dict(raw_cell)
        cell.setdefault("cell_type", "raw")
        cell.setdefault("source", "")
        cell.setdefault("metadata", {})
        if not isinstance(cell["metadata"], dict):
            raise IpynbParseError(f"cell {index} metadata must be an object")
        if cell["cell_type"] == "code":
            cell.setdefault("outputs", [])
            cell.setdefault("execution_count", None)
        ensure_cell_id(cell, used_ids)
        cells.append(cell)
    notebook["cells"] = cells
    notebook.setdefault("nbformat_minor", 0)
    return notebook


def loads(
    data: str | bytes,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> IpynbDocument:
    selected = effective_limits(limits)
    return IpynbDocument(_parse(_read_source(data, selected), mode=mode, limits=selected))


def load(
    source: Source,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> IpynbDocument:
    selected = effective_limits(limits)
    return IpynbDocument(
        _parse(_read_source(source, selected), mode=mode, limits=selected)
    )


def load_ipynb(
    source: Source, *, limits: ResourceLimits | None = None
) -> dict[str, Any]:
    return load(source, mode="preservation", limits=limits).raw


def probe(
    source: Source, *, limits: ResourceLimits | None = None
) -> ProbeResult:
    try:
        document = load(source, mode="preservation", limits=limits)
    except Exception as exc:
        return ProbeResult(False, 0.0, "ipynb", reason=str(exc))
    confidence = 1.0 if document.nbformat == 4 else 0.5
    return ProbeResult(
        True,
        confidence,
        "ipynb",
        profile=f"nbformat-{document.nbformat}.{document.nbformat_minor}",
    )


def probe_ipynb(source: Source, *, limits: ResourceLimits | None = None) -> bool:
    return bool(probe(source, limits=limits))

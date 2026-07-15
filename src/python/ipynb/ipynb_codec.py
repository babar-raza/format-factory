"""Jupyter Notebook (.ipynb) codec — probe, load, write.

Implements the minimum viable codec for nbformat v4.x notebooks.
Detection: valid JSON with ``nbformat`` key at root level.
Parsing: stdlib ``json`` module only.

Spec reference: FACT-IPYNB-001
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Union

from ipynb.exceptions import IpynbParseError, IpynbValidationError, IpynbWriteError
from ipynb.spec.notebook.output import Output

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

# nbformat >=4.5 requires every cell to carry a unique id matching this
# pattern (see FACT-IPYNB-101 / cell id spec citation).
CELL_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

# The four valid values of a code cell output's `output_type` field, and the
# fields that are required for each (FACT-IPYNB-105 / nbformat validator
# equivalent).
VALID_OUTPUT_TYPES = ("stream", "display_data", "execute_result", "error")
REQUIRED_OUTPUT_FIELDS: dict[str, tuple[str, ...]] = {
    "stream": ("name", "text"),
    "display_data": ("data",),
    "execute_result": ("data", "execution_count"),
    "error": ("ename", "evalue", "traceback"),
}

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "nbformat_v4",
    "cell_types_code_markdown_raw",
    "cell_outputs",
    "notebook_metadata",
    "size_guard",
    "cell_id_preservation",
    "cell_attachments",
    "output_mime_bundle_api",
    "structural_mutation_api",
    "schema_validation",
]

UNSUPPORTED_FEATURES = [
    "nbformat_v1",
    "nbformat_v2",
    "nbformat_v3",
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


def _generate_cell_id(used_ids: set[str]) -> str:
    """Generate a spec-compliant cell id, unique within ``used_ids``.

    Uses a short hex UUID fragment, which always satisfies
    ``^[a-zA-Z0-9_-]{1,64}$``. Regenerates on the (astronomically unlikely)
    event of a collision.
    """
    while True:
        candidate = uuid.uuid4().hex[:8]
        if candidate not in used_ids:
            return candidate


def ensure_cell_id(cell: dict[str, Any], used_ids: set[str]) -> dict[str, Any]:
    """Ensure ``cell`` has a valid, unique ``id`` field (FACT-IPYNB-101).

    nbformat >=4.5 requires every cell to have an ``id`` matching
    ``^[a-zA-Z0-9_-]{1,64}$`` that is unique within its notebook. This
    function:

    - Leaves an existing valid, not-yet-seen cell id untouched.
    - Generates a new id when the cell has no id, a malformed id, or an id
      that collides with one already seen in this notebook (``used_ids``).

    ``used_ids`` is mutated in place to record the id assigned to ``cell``,
    so callers should thread the same set across every cell in a notebook
    to guarantee per-notebook uniqueness. Returns ``cell`` (mutated in
    place) for convenient chaining.
    """
    cell_id = cell.get("id")
    if not isinstance(cell_id, str) or not CELL_ID_PATTERN.match(cell_id) or cell_id in used_ids:
        cell_id = _generate_cell_id(used_ids)
    cell["id"] = cell_id
    used_ids.add(cell_id)
    return cell


def load_ipynb(source: SourceType) -> dict[str, Any]:
    """Parse a Jupyter Notebook and return a canonical model dict.

    Returns a dict with keys: nbformat, nbformat_minor, metadata, cells.
    Each cell has: cell_type, id, source, metadata, and optionally outputs
    + execution_count (code cells) or attachments (markdown/raw cells).

    Every cell is guaranteed a valid, notebook-unique ``id`` — an existing
    id is preserved unchanged; a missing/invalid/colliding id is replaced
    with a freshly generated one (see ``ensure_cell_id``).
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
    used_ids: set[str] = set()
    for i, raw_cell in enumerate(raw_cells):
        if not isinstance(raw_cell, dict):
            raise IpynbParseError(f"Cell {i} is not a JSON object")
        cell_type = raw_cell.get("cell_type", "raw")
        cell: dict[str, Any] = {
            "cell_type": cell_type,
            "id": raw_cell.get("id"),
            "source": raw_cell.get("source", ""),
            "metadata": raw_cell.get("metadata", {}),
        }
        if cell_type == "code":
            cell["outputs"] = raw_cell.get("outputs", [])
            cell["execution_count"] = raw_cell.get("execution_count")
        elif "attachments" in raw_cell:
            # attachments is a sibling of metadata, valid only on
            # markdown/raw cells (FACT-IPYNB-102).
            cell["attachments"] = raw_cell["attachments"]
        ensure_cell_id(cell, used_ids)
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

    Every output cell is guaranteed a valid, notebook-unique ``id`` on
    write — this makes ``write_ipynb`` safe to call directly on
    caller-constructed cells (e.g. from ``IpynbDocument.add_cell``) that
    have no id yet, in addition to cells that already have one from a
    prior ``load_ipynb`` call.
    """
    nbformat = model.get("nbformat", 4)
    nbformat_minor = model.get("nbformat_minor", 5)
    metadata = model.get("metadata", {})
    cells = model.get("cells", [])

    out_cells: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for cell in cells:
        cell_type = cell.get("cell_type", "raw")
        out_cell: dict[str, Any] = {
            "cell_type": cell_type,
            "id": cell.get("id"),
            "source": cell.get("source", ""),
            "metadata": cell.get("metadata", {}),
        }
        if cell_type == "code":
            out_cell["outputs"] = cell.get("outputs", [])
            out_cell["execution_count"] = cell.get("execution_count")
        elif "attachments" in cell:
            out_cell["attachments"] = cell["attachments"]
        ensure_cell_id(out_cell, used_ids)
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


# --- Output MIME-bundle API (FACT-IPYNB-103) --------------------------------
#
# These are thin, codec-level wrappers over ``ipynb.spec.notebook.output.
# Output`` — Output is the single real implementation of MIME-bundle
# add/get/remove; these functions just make it convenient to call against a
# raw output dict (as stored on a cell's ``outputs`` list) without the
# caller needing to import/construct an Output instance itself. Because
# Output wraps the same dict object it was given, mutations made through
# these functions are reflected directly in the cell's outputs list.


def get_output_representation(output: dict[str, Any], mime_type: str) -> Any:
    """Return the value for ``mime_type`` in an output's MIME ``data`` bundle.

    Returns None if the output has no ``data`` bundle or does not carry
    that MIME type. Applies to ``display_data``/``execute_result`` outputs.
    """
    return Output(output).get_representation(mime_type)


def add_output_representation(output: dict[str, Any], mime_type: str, value: Any) -> dict[str, Any]:
    """Add or replace a MIME representation in an output's ``data`` bundle.

    Mutates ``output`` in place (creating a ``data`` dict if absent) and
    returns it for convenience.
    """
    Output(output).add_representation(mime_type, value)
    return output


def remove_output_mime_type(output: dict[str, Any], mime_type: str) -> bool:
    """Remove a MIME representation from an output's ``data`` bundle.

    Mutates ``output`` in place. Returns True if ``mime_type`` was present
    and removed, False otherwise (no-op).
    """
    return Output(output).remove_representation(mime_type)


# --- Schema/structural validation (FACT-IPYNB-105) --------------------------


def validate_notebook_schema(model: dict[str, Any]) -> list[str]:
    """Validate structural correctness of a parsed notebook model.

    Checks:
      - cell id uniqueness within the notebook
      - cell id format compliance (``^[a-zA-Z0-9_-]{1,64}$``)
      - code cell output ``output_type`` is one of the 4 valid values
        (stream, display_data, execute_result, error)
      - required fields are present per output_type (stream needs
        name+text; display_data needs data; execute_result needs
        data+execution_count; error needs ename+evalue+traceback)

    Returns a list of human-readable error strings; an empty list means
    the notebook is structurally valid. Never raises — use
    ``validate_notebook`` for a raising variant.
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, cell in enumerate(model.get("cells", [])):
        cell_id = cell.get("id")
        if not isinstance(cell_id, str) or not CELL_ID_PATTERN.match(cell_id):
            errors.append(
                f"Cell {i}: invalid or missing id {cell_id!r} "
                f"(must match {CELL_ID_PATTERN.pattern!r})"
            )
        elif cell_id in seen_ids:
            errors.append(f"Cell {i}: duplicate cell id {cell_id!r}")
        else:
            seen_ids.add(cell_id)

        if cell.get("cell_type") != "code":
            continue
        for j, output in enumerate(cell.get("outputs", [])):
            output_type = output.get("output_type")
            if output_type not in VALID_OUTPUT_TYPES:
                errors.append(
                    f"Cell {i} output {j}: invalid output_type {output_type!r} "
                    f"(must be one of {VALID_OUTPUT_TYPES})"
                )
                continue
            for field in REQUIRED_OUTPUT_FIELDS[output_type]:
                if field not in output:
                    errors.append(
                        f"Cell {i} output {j}: {output_type!r} output missing "
                        f"required field {field!r}"
                    )

    return errors


def validate_notebook(model: dict[str, Any]) -> None:
    """Validate ``model`` and raise ``IpynbValidationError`` on any failure.

    Raising variant of ``validate_notebook_schema`` — the error message
    joins every individual finding so a single failure surfaces the full
    picture, not just the first problem.
    """
    errors = validate_notebook_schema(model)
    if errors:
        raise IpynbValidationError("; ".join(errors))

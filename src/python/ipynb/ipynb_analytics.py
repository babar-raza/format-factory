"""ipynb analytics — path/bytes based Jupyter Notebook statistics.

Each function operates on a freshly re-parsed notebook model obtained via
``load_ipynb`` (a path, bytes, or JSON string source) — never on a
pre-built domain model object.

Spec facts:
    FACT-IPYNB-002 — cell shape (cell_type, source, metadata, outputs)
    FACT-IPYNB-003 — output shape (output_type: stream, display_data,
                     execute_result, error)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from ipynb.ipynb_codec import load_ipynb

spec_qname = "ipynb:notebook"
spec_fact_ref = "FACT-IPYNB-001"

SourceType = Union[str, Path, bytes]


def _source_text_length(source: Any) -> int:
    """Return the character length of a cell ``source`` field.

    nbformat permits ``source`` to be either a single string or a list of
    line strings (the common on-disk form). Both are handled uniformly.
    """
    if isinstance(source, list):
        return sum(len(line) for line in source if isinstance(line, str))
    if isinstance(source, str):
        return len(source)
    return 0


def ipynb_cell_type_histogram(source: SourceType) -> dict[str, int]:
    """Return a count of cells grouped by ``cell_type``.

    Returns an empty dict for a notebook with no cells.

    Spec: each cell has a cell_type field, one of code/markdown/raw
    (FACT-IPYNB-002).
    """
    model = load_ipynb(source)
    histogram: dict[str, int] = {}
    for cell in model.get("cells", []):
        cell_type = cell.get("cell_type", "raw")
        histogram[cell_type] = histogram.get(cell_type, 0) + 1
    return histogram


def ipynb_output_type_histogram(source: SourceType) -> dict[str, int]:
    """Return a count of code-cell outputs grouped by ``output_type``.

    Only code cells carry outputs; markdown/raw cells are skipped.
    Returns an empty dict when there are no code cells or no outputs.

    Spec: outputs are arrays of output_type objects — stream,
    display_data, execute_result, error (FACT-IPYNB-003).
    """
    model = load_ipynb(source)
    histogram: dict[str, int] = {}
    for cell in model.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for output in cell.get("outputs", []):
            output_type = output.get("output_type", "unknown")
            histogram[output_type] = histogram.get(output_type, 0) + 1
    return histogram


def ipynb_average_source_length(source: SourceType) -> float:
    """Return the average character length of cell ``source`` across all cells.

    Returns 0.0 for a notebook with no cells. Handles both string and
    list-of-lines ``source`` representations.

    Spec: each cell has a source field, string or list of strings
    (FACT-IPYNB-002).
    """
    model = load_ipynb(source)
    cells = model.get("cells", [])
    if not cells:
        return 0.0
    total = sum(_source_text_length(cell.get("source", "")) for cell in cells)
    return total / len(cells)


def ipynb_has_execution_errors(source: SourceType) -> bool:
    """Return True if any code cell output has ``output_type == "error"``.

    Returns False for a notebook with no cells, no code cells, or no
    error outputs.

    Spec: error is one of the four output_type variants, carrying ename,
    evalue, and traceback (FACT-IPYNB-003).
    """
    model = load_ipynb(source)
    for cell in model.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                return True
    return False

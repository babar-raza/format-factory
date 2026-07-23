"""Profile-aware structural validation for nbformat 4.x notebooks."""

from __future__ import annotations

from typing import Any, Mapping

from format_factory.core import (
    Diagnostic,
    ResourceLimits,
    Severity,
    SourceLocation,
    ValidationReport,
)

from ..codec.reader import CELL_ID_PATTERN, Source, load
from ..errors import IpynbError, IpynbValidationError
from ..model import IpynbDocument

VALID_CELL_TYPES = frozenset({"code", "markdown", "raw"})
REQUIRED_OUTPUT_FIELDS: dict[str, tuple[str, ...]] = {
    "stream": ("name", "text"),
    "display_data": ("data", "metadata"),
    "execute_result": ("data", "metadata", "execution_count"),
    "error": ("ename", "evalue", "traceback"),
}
VALID_OUTPUT_TYPES = frozenset(REQUIRED_OUTPUT_FIELDS)


def _mapping(
    value: IpynbDocument | Mapping[str, Any] | Source,
    *,
    limits: ResourceLimits | None,
) -> Mapping[str, Any]:
    if isinstance(value, IpynbDocument):
        return value.raw
    if isinstance(value, Mapping):
        return value
    return load(value, mode="preservation", limits=limits).raw


def _diagnostic(
    code: str, message: str, path: tuple[str | int, ...]
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity=Severity.ERROR,
        location=SourceLocation(path=path),
    )


def validate(
    value: IpynbDocument | Mapping[str, Any] | Source,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    diagnostics: list[Diagnostic] = []
    try:
        model = _mapping(value, limits=limits)
    except (IpynbError, OSError, TypeError, ValueError) as exc:
        return ValidationReport([_diagnostic("IPYNB_PARSE", str(exc), ())])

    major = model.get("nbformat")
    minor = model.get("nbformat_minor", 0)
    if major != 4 or isinstance(major, bool):
        diagnostics.append(
            _diagnostic("IPYNB_VERSION", "nbformat must equal 4", ("nbformat",))
        )
    if isinstance(minor, bool) or not isinstance(minor, int) or not 0 <= minor <= 5:
        diagnostics.append(
            _diagnostic(
                "IPYNB_MINOR_VERSION",
                "nbformat_minor must be an integer from 0 through 5",
                ("nbformat_minor",),
            )
        )
    if profile is not None:
        selected = profile.removeprefix("nbformat-")
        if selected not in {f"4.{item}" for item in range(6)}:
            raise ValueError("profile must be one of nbformat 4.0 through 4.5")
        if (major, minor) != (4, int(selected.split(".")[1])):
            diagnostics.append(
                _diagnostic(
                    "IPYNB_PROFILE",
                    f"document does not match requested profile {selected}",
                    ("nbformat_minor",),
                )
            )

    metadata = model.get("metadata")
    if not isinstance(metadata, Mapping):
        diagnostics.append(
            _diagnostic("IPYNB_METADATA", "metadata must be an object", ("metadata",))
        )
    cells = model.get("cells")
    if not isinstance(cells, list):
        diagnostics.append(
            _diagnostic("IPYNB_CELLS", "cells must be an array", ("cells",))
        )
        return ValidationReport(diagnostics)

    seen_ids: set[str] = set()
    require_ids = isinstance(minor, int) and not isinstance(minor, bool) and minor >= 5
    for cell_index, cell in enumerate(cells):
        cell_path = ("cells", cell_index)
        if not isinstance(cell, Mapping):
            diagnostics.append(
                _diagnostic("IPYNB_CELL", "cell must be an object", cell_path)
            )
            continue
        cell_type = cell.get("cell_type")
        if cell_type not in VALID_CELL_TYPES:
            diagnostics.append(
                _diagnostic(
                    "IPYNB_CELL_TYPE",
                    f"invalid cell_type {cell_type!r}",
                    (*cell_path, "cell_type"),
                )
            )
        cell_id = cell.get("id")
        if require_ids or cell_id is not None:
            if not isinstance(cell_id, str) or CELL_ID_PATTERN.fullmatch(cell_id) is None:
                diagnostics.append(
                    _diagnostic(
                        "IPYNB_CELL_ID",
                        f"invalid or missing cell id {cell_id!r}",
                        (*cell_path, "id"),
                    )
                )
            elif cell_id in seen_ids:
                diagnostics.append(
                    _diagnostic(
                        "IPYNB_CELL_ID_DUPLICATE",
                        f"duplicate cell id {cell_id!r}",
                        (*cell_path, "id"),
                    )
                )
            else:
                seen_ids.add(cell_id)
        if not isinstance(cell.get("metadata"), Mapping):
            diagnostics.append(
                _diagnostic(
                    "IPYNB_CELL_METADATA",
                    "cell metadata must be an object",
                    (*cell_path, "metadata"),
                )
            )
        if not isinstance(cell.get("source"), (str, list)):
            diagnostics.append(
                _diagnostic(
                    "IPYNB_CELL_SOURCE",
                    "cell source must be a string or string array",
                    (*cell_path, "source"),
                )
            )
        if cell_type != "code":
            continue
        outputs = cell.get("outputs")
        if not isinstance(outputs, list):
            diagnostics.append(
                _diagnostic(
                    "IPYNB_OUTPUTS",
                    "code-cell outputs must be an array",
                    (*cell_path, "outputs"),
                )
            )
            continue
        for output_index, output in enumerate(outputs):
            output_path = (*cell_path, "outputs", output_index)
            if not isinstance(output, Mapping):
                diagnostics.append(
                    _diagnostic("IPYNB_OUTPUT", "output must be an object", output_path)
                )
                continue
            output_type = output.get("output_type")
            if output_type not in VALID_OUTPUT_TYPES:
                diagnostics.append(
                    _diagnostic(
                        "IPYNB_OUTPUT_TYPE",
                        f"invalid output_type {output_type!r}",
                        (*output_path, "output_type"),
                    )
                )
                continue
            for field in REQUIRED_OUTPUT_FIELDS[str(output_type)]:
                if field not in output:
                    diagnostics.append(
                        _diagnostic(
                            "IPYNB_OUTPUT_REQUIRED",
                            f"{output_type!r} output is missing {field!r}",
                            (*output_path, field),
                        )
                    )
    return ValidationReport(diagnostics)


def validate_notebook_schema(model: Mapping[str, Any]) -> list[str]:
    return [item.message for item in validate(model).errors]


def validate_notebook(model: Mapping[str, Any]) -> None:
    errors = validate_notebook_schema(model)
    if errors:
        raise IpynbValidationError("; ".join(errors))

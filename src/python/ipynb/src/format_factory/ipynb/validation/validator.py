"""Profile-aware structural and semantic validation for nbformat 4.x."""

from __future__ import annotations

from typing import Any, Mapping

from format_factory.core import ResourceLimits, ValidationReport

from ..codec.reader import Source, load
from ..errors import IpynbError, IpynbValidationError
from ..model import IpynbDocument
from .rules import (
    KNOWN_CELL_TYPES,
    KNOWN_OUTPUT_TYPES,
    diagnostic,
    select_profile,
    validate_model,
)

VALID_CELL_TYPES = KNOWN_CELL_TYPES
VALID_OUTPUT_TYPES = KNOWN_OUTPUT_TYPES
REQUIRED_OUTPUT_FIELDS: dict[str, tuple[str, ...]] = {
    "stream": ("name", "text"),
    "display_data": ("data", "metadata"),
    "execute_result": ("data", "metadata", "execution_count"),
    "error": ("ename", "evalue", "traceback"),
}


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


def validate(
    value: IpynbDocument | Mapping[str, Any] | Source,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Validate using the declared, current, or an explicit nbformat profile.

    The default is ``declared``. A future 4.x minor uses the 4.5 structural
    baseline and reports forward-compatible constructs as warnings. The
    ``current`` profile requires an exact 4.5 declaration.
    """

    try:
        model = _mapping(value, limits=limits)
    except (IpynbError, OSError, TypeError, ValueError) as exc:
        return ValidationReport([diagnostic("IPYNB_PARSE", str(exc), ())])

    selected, diagnostics = select_profile(model, profile)
    diagnostics.extend(validate_model(model, selected))
    return ValidationReport(diagnostics)


def validate_notebook_schema(model: Mapping[str, Any]) -> list[str]:
    return [item.message for item in validate(model).errors]


def validate_notebook(model: Mapping[str, Any]) -> None:
    errors = validate_notebook_schema(model)
    if errors:
        raise IpynbValidationError("; ".join(errors))

"""NRRD document invariant validation."""

from __future__ import annotations

from typing import Any, Mapping

from format_factory.core import Diagnostic, ResourceLimits, ValidationReport

from ..codec.payload import checked_element_count, dtype_info
from ..model import NrrdDocument
from ..security import effective_limits


def validate(
    value: NrrdDocument | Mapping[str, Any],
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Return stable diagnostics instead of hiding violations."""

    diagnostics: list[Diagnostic] = []
    try:
        document = (
            value if isinstance(value, NrrdDocument) else NrrdDocument.from_mapping(value)
        )
    except (TypeError, ValueError) as exc:
        return ValidationReport([Diagnostic("nrrd.model.invalid", str(exc))])
    if profile is not None and profile not in {
        f"NRRD000{item}" for item in range(1, 6)
    }:
        diagnostics.append(
            Diagnostic("nrrd.profile.unsupported", f"unsupported profile {profile!r}")
        )
    try:
        dimension = document.dimension
        sizes = document.sizes
        if dimension != len(sizes):
            diagnostics.append(
                Diagnostic(
                    "nrrd.dimension.mismatch",
                    "dimension does not equal the number of axis sizes",
                )
            )
        dtype_info(document.nrrd_type)
        count = checked_element_count(sizes, effective_limits(limits))
        if len(document.array) != count:
            diagnostics.append(
                Diagnostic(
                    "nrrd.array.length",
                    f"expected {count} values, got {len(document.array)}",
                )
            )
        if document.kinds and len(document.kinds) != dimension:
            diagnostics.append(
                Diagnostic(
                    "nrrd.kinds.length",
                    "kinds must contain one entry per axis",
                )
            )
    except (KeyError, TypeError, ValueError) as exc:
        diagnostics.append(Diagnostic("nrrd.header.invalid", str(exc)))
    return ValidationReport(diagnostics)

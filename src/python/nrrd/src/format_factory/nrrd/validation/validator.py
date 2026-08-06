"""NRRD document invariant validation."""

from __future__ import annotations

from typing import Any, Mapping

from format_factory.core import Diagnostic, ResourceLimits, ValidationReport

from ..codec.payload import (
    checked_element_count,
    dtype_info,
    expected_binary_size,
    is_block_type,
    parse_block_size,
)
from ..errors import NrrdParseError
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
        block_size = None
        if is_block_type(document.nrrd_type):
            block_size = parse_block_size(document.header.get("block size"))
            if document.encoding in {"ascii", "text", "txt"}:
                diagnostics.append(
                    Diagnostic(
                        "nrrd.block.encoding",
                        "block type is not valid with ASCII encoding",
                    )
                )
        else:
            dtype_info(document.nrrd_type)
        count = checked_element_count(sizes, effective_limits(limits))
        expected_payload_size = expected_binary_size(
            document.nrrd_type,
            sizes,
            effective_limits(limits),
            block_size=block_size,
        )
        if len(document.payload) != expected_payload_size:
            diagnostics.append(
                Diagnostic(
                    "nrrd.payload.length",
                    "decoded payload length does not match declared type and sizes",
                )
            )
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
        for field_name, arity in document.per_axis_field_arities().items():
            if field_name == "kinds":
                continue  # already reported above with its own diagnostic code
            if arity != dimension:
                diagnostics.append(
                    Diagnostic(
                        "nrrd.axis_field.arity",
                        f"{field_name!r} declares {arity} value(s), expected one "
                        f"per axis ({dimension})",
                    )
                )
    except (KeyError, TypeError, ValueError, NrrdParseError) as exc:
        diagnostics.append(Diagnostic("nrrd.header.invalid", str(exc)))
    return ValidationReport(diagnostics)

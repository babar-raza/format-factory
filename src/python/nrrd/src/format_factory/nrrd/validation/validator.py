"""NRRD document invariant validation."""

from __future__ import annotations

from typing import Any, Mapping

from format_factory.core import Diagnostic, ResourceLimits, ValidationReport

from ..codec.kinds import KIND_REQUIRED_SIZE, KIND_UNKNOWN_MARKERS, canonical_kind
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
from ..space import build_space_transform


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
    valid_profiles = {f"NRRD000{item}" for item in range(1, 6)}
    if profile is not None and profile not in valid_profiles:
        diagnostics.append(
            Diagnostic("nrrd.profile.unsupported", f"unsupported profile {profile!r}")
        )
    target_profile = profile if profile in valid_profiles else f"NRRD000{document.version}"
    if target_profile in valid_profiles:
        target_version = int(target_profile[-1])
        minimal_version = document.minimal_version_for()
        if target_version < minimal_version:
            # NRRD-VERSION-001/NRRD-LIFECYCLE-001: a declared (or requested)
            # version too old for the populated fields must be flagged, not
            # silently accepted or silently upgraded.
            blocking = ", ".join(
                sorted(
                    {
                        name
                        for gate, name in document.version_requirements()
                        if gate > target_version
                    }
                )
            )
            diagnostics.append(
                Diagnostic(
                    "nrrd.version.insufficient",
                    f"{target_profile} cannot represent this document: {blocking} "
                    f"requires NRRD000{minimal_version} or newer",
                )
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
        elif document.kinds:
            for index, kind in enumerate(document.kinds):
                if kind in KIND_UNKNOWN_MARKERS:
                    continue
                canonical = canonical_kind(kind)
                if canonical is None:
                    diagnostics.append(
                        Diagnostic(
                            "nrrd.kinds.unrecognized",
                            f"axis {index} declares kind {kind!r}, not a recognized "
                            "kind or alias (preserved as opaque text, not rejected; "
                            'use "???" or "none" for an explicitly unknown kind)',
                        )
                    )
                    continue
                required = KIND_REQUIRED_SIZE[canonical]
                if required is not None and index < len(sizes) and sizes[index] != required:
                    diagnostics.append(
                        Diagnostic(
                            "nrrd.kinds.size_mismatch",
                            f"axis {index} has kind {kind!r} (canonically "
                            f"{canonical!r}), which requires size {required}, but "
                            f"the declared size is {sizes[index]}",
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
        # NRRD-VALIDATE-001: space/space dimension/space origin/space
        # directions mutual consistency, as a non-fatal diagnostic rather
        # than the exception build_space_transform() raises on its own —
        # both "space directions" and "space origin" are required inputs
        # to that function, so this check only runs when a document
        # declares both (space metadata is otherwise entirely optional).
        space_directions = document.header.get("space directions")
        space_origin = document.header.get("space origin")
        if space_directions is not None and space_origin is not None:
            try:
                build_space_transform(
                    space_directions=space_directions,
                    space_origin=space_origin,
                    space_dimension=document.header.get("space dimension"),
                    space=document.header.get("space"),
                    axis_count=dimension,
                )
            except NrrdParseError as exc:
                diagnostics.append(Diagnostic("nrrd.space.inconsistent", str(exc)))
    except (KeyError, TypeError, ValueError, NrrdParseError) as exc:
        diagnostics.append(Diagnostic("nrrd.header.invalid", str(exc)))
    return ValidationReport(diagnostics)

"""ORA-STACK-001 — the ordered nested layer tree.

A stack's children are stored in *visual* order: "its first child is the
uppermost item in visual layer order". That is the one rule a reader cannot get
wrong without inverting every image it renders, so the tree preserves document
order exactly and never sorts.

Attribute defaults come from the contract's normative rules and are applied at
construction, so a caller never has to distinguish "absent" from "explicitly
default" to composite correctly. ORA-PRESERVE-001 separately requires that
distinction to remain discoverable for callers who DO care about it (round-trip
fidelity tooling, diffing, re-serialization decisions): `OraNode.explicit_attributes`
records which of x/y/opacity/visibility/composite-op/isolation the source XML
actually wrote, alongside (not instead of) the always-defaulted value every
existing compositing consumer already reads unaffected.

ORA-LAYER-001 / ORA-GROUP-001: "reject invalid values without altering the
document" applies to construction, not only to XML parsing -- editing via
`dataclasses.replace()` calls `__init__` again, which runs `__post_init__`,
so the same domain checks `codec/stack_xml.py` applies while parsing apply
here too. `codec/stack_xml.py` calls the validators defined here rather than
keeping its own copies, so parser and model can never silently diverge on
what counts as a valid opacity, visibility, or layer/text source path.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..errors import OraValidationError
from .composite_ops import DEFAULT_COMPOSITE_OP, CompositeOpInfo
from .composite_ops import composite_op_info as _composite_op_info

#: "Stack and layer visibility accepts only visible or hidden and defaults to
#: visible when omitted."
VISIBILITY_VALUES = frozenset({"visible", "hidden"})
DEFAULT_VISIBILITY = "visible"


def validate_opacity(value: float, *, label: str = "opacity") -> None:
    """"Stack and layer opacity is a floating-point value in the inclusive
    range zero through one." Both endpoints are legal; NaN is not."""
    if value != value:  # NaN compares unequal to itself.
        raise OraValidationError(f"{label} must be a number, got NaN")
    if not 0.0 <= value <= 1.0:
        raise OraValidationError(
            f"{label} must be within the inclusive range 0 through 1, got {value}"
        )


def validate_visibility(value: str, *, label: str = "visibility") -> None:
    if value not in VISIBILITY_VALUES:
        raise OraValidationError(
            f"{label} accepts only {sorted(VISIBILITY_VALUES)}, got {value!r}"
        )


def validate_src(raw: str, *, element: str) -> str:
    """A src is an archive-root-relative member path, so it can escape exactly
    the way a member name can. Shared by the parser and the model so a
    layer/text source can never be constructed unsafely by either route."""
    if not raw:
        raise OraValidationError(f"<{element}> has an empty src attribute")
    if raw.startswith("/") or "\\" in raw or (len(raw) >= 2 and raw[1] == ":"):
        raise OraValidationError(
            f"<{element}> src {raw!r} is not an archive-root-relative path"
        )
    if ".." in raw.split("/"):
        raise OraValidationError(
            f"<{element}> src {raw!r} traverses outside the archive root"
        )
    return raw


@dataclass(frozen=True)
class OraNode:
    """Attributes common to every stack, layer and text element.

    "Non-root stacks and layers use signed integer x and y positions whose
    default values are zero." Positions are signed because content may hang off
    the canvas edge; clamping them at parse time would destroy pixels a
    round-trip is required to preserve.
    """

    name: str | None = None
    x: int = 0
    y: int = 0
    opacity: float = 1.0
    visibility: str = DEFAULT_VISIBILITY
    composite_op: str = DEFAULT_COMPOSITE_OP
    #: ORA-PRESERVE-001: which of this node's own default-having attributes
    #: (x, y, opacity, visibility, composite-op, and -- on OraStack --
    #: isolation) the source XML actually wrote, versus a value this
    #: dataclass supplied because the attribute was absent. Populated once
    #: by the parser (codec/stack_xml.py); empty for a node built directly
    #: in memory, since nothing was parsed for it to record.
    explicit_attributes: frozenset[str] = frozenset()

    @property
    def is_visible(self) -> bool:
        return self.visibility == "visible"

    @property
    def composite_op_details(self) -> CompositeOpInfo | None:
        """The composite-op value's documented blend function and
        Porter-Duff operator, or ``None`` if it falls outside the spec's
        current table -- composite-op is a deliberately open vocabulary,
        so an unrecognized value is preserved content, not an error."""
        return _composite_op_info(self.composite_op)

    def was_explicit(self, attribute: str) -> bool:
        """Whether `attribute` (by its XML name, e.g. "composite-op") was
        actually present in the source XML, as opposed to this dataclass
        having supplied its own default because the attribute was absent."""
        return attribute in self.explicit_attributes

    def __post_init__(self) -> None:
        validate_opacity(self.opacity)
        validate_visibility(self.visibility)


@dataclass(frozen=True)
class OraLayer(OraNode):
    """A raster layer. "Every layer element requires a src attribute identifying
    the separate archive member that stores the graphical layer.\""""

    src: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        validate_src(self.src, element="layer")


@dataclass(frozen=True)
class OraText(OraNode):
    """A text element.

    Modelled but not interpreted: text is outside the baseline reading profile,
    and inventing semantics for it would be worse than preserving it opaquely.
    """

    src: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.src is not None:
            validate_src(self.src, element="text")


@dataclass(frozen=True)
class OraStack(OraNode):
    """A group of nodes, in visual order with the uppermost first."""

    children: tuple["OraStack | OraLayer | OraText", ...] = field(default_factory=tuple)

    @property
    def is_isolated_group(self) -> bool:
        """ORA-ISOLATION-001, profile 0.0.4+.

        "a non-root stack is isolated when isolation is isolate, opacity is
        below one, or composite-op differs from svg:src-over."

        Exposed here because the condition is derived purely from this node's
        own attributes; whether the node is a *non-root* stack is the caller's
        context, so this answers the attribute half only.
        """
        return (
            self.isolation == "isolate"
            or self.opacity < 1.0
            or self.composite_op != DEFAULT_COMPOSITE_OP
        )

    isolation: str = "auto"


OraChild = OraStack | OraLayer | OraText

__all__ = [
    "DEFAULT_COMPOSITE_OP",
    "DEFAULT_VISIBILITY",
    "VISIBILITY_VALUES",
    "OraChild",
    "OraLayer",
    "OraNode",
    "OraStack",
    "OraText",
    "validate_opacity",
    "validate_src",
    "validate_visibility",
]

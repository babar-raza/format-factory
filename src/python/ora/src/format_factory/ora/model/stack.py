"""ORA-STACK-001 — the ordered nested layer tree.

A stack's children are stored in *visual* order: "its first child is the
uppermost item in visual layer order". That is the one rule a reader cannot get
wrong without inverting every image it renders, so the tree preserves document
order exactly and never sorts.

Attribute defaults come from the contract's normative rules and are applied at
construction, so a caller never has to distinguish "absent" from "explicitly
default" to composite correctly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: "The composite-op attribute defaults to svg:src-over..."
DEFAULT_COMPOSITE_OP = "svg:src-over"

#: "Stack and layer visibility accepts only visible or hidden and defaults to
#: visible when omitted."
VISIBILITY_VALUES = frozenset({"visible", "hidden"})
DEFAULT_VISIBILITY = "visible"


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

    @property
    def is_visible(self) -> bool:
        return self.visibility == "visible"


@dataclass(frozen=True)
class OraLayer(OraNode):
    """A raster layer. "Every layer element requires a src attribute identifying
    the separate archive member that stores the graphical layer.\""""

    src: str = ""


@dataclass(frozen=True)
class OraText(OraNode):
    """A text element.

    Modelled but not interpreted: text is outside the baseline reading profile,
    and inventing semantics for it would be worse than preserving it opaquely.
    """

    src: str | None = None


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
]

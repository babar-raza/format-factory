"""ORA-COMPOSITE-001 / ORA-STACK-001 / ORA-LAYER-001 / ORA-GROUP-001 /
ORA-EDIT-001 / ORA-RENDER-001 -- "The composite-op attribute defaults to
svg:src-over and selects a documented blend function combined with a
Porter-Duff compositing operator."

The registry below is transcribed directly from the Layer Stack
Specification's own composite-op table (the pinned, authority-locked spec
source under ``.local/format-contracts/acquired/ora/src-ora-003.bin``,
"composite-op attribute" section) -- not invented from memory.

The same spec text also states: "In the future other compositing modes
might be added, and a way for applications to define new modes will be
specified." composite-op is therefore a deliberately open vocabulary, and
:func:`composite_op_info` returns ``None`` for a value outside this table
rather than raising -- an unrecognized value is forward-compatible content
to preserve, not a defect to reject.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_COMPOSITE_OP = "svg:src-over"


@dataclass(frozen=True)
class CompositeOpInfo:
    """A composite-op value's documented meaning."""

    blending_function: str
    compositing_operator: str


_SOURCE_OVER = "Source Over"

COMPOSITE_OP_REGISTRY: dict[str, CompositeOpInfo] = {
    "svg:src-over": CompositeOpInfo("Normal", _SOURCE_OVER),
    "svg:multiply": CompositeOpInfo("Multiply", _SOURCE_OVER),
    "svg:screen": CompositeOpInfo("Screen", _SOURCE_OVER),
    "svg:overlay": CompositeOpInfo("Overlay", _SOURCE_OVER),
    "svg:darken": CompositeOpInfo("Darken", _SOURCE_OVER),
    "svg:lighten": CompositeOpInfo("Lighten", _SOURCE_OVER),
    "svg:color-dodge": CompositeOpInfo("Color Dodge", _SOURCE_OVER),
    "svg:color-burn": CompositeOpInfo("Color Burn", _SOURCE_OVER),
    "svg:hard-light": CompositeOpInfo("Hard Light", _SOURCE_OVER),
    "svg:soft-light": CompositeOpInfo("Soft Light", _SOURCE_OVER),
    "svg:difference": CompositeOpInfo("Difference", _SOURCE_OVER),
    "svg:color": CompositeOpInfo("Color", _SOURCE_OVER),
    "svg:luminosity": CompositeOpInfo("Luminosity", _SOURCE_OVER),
    "svg:hue": CompositeOpInfo("Hue", _SOURCE_OVER),
    "svg:saturation": CompositeOpInfo("Saturation", _SOURCE_OVER),
    "svg:plus": CompositeOpInfo("Normal", "Lighter"),
    "svg:dst-in": CompositeOpInfo("Normal", "Destination In"),
    "svg:dst-out": CompositeOpInfo("Normal", "Destination Out"),
    "svg:src-atop": CompositeOpInfo("Normal", "Source Atop"),
    "svg:dst-atop": CompositeOpInfo("Normal", "Destination Atop"),
}


def composite_op_info(value: str) -> CompositeOpInfo | None:
    """Look up a composite-op value's documented blend function and
    Porter-Duff operator. Returns ``None`` for a value outside the spec's
    current table -- composite-op is a deliberately open, forward
    -compatible vocabulary, so an unrecognized value is not an error."""
    return COMPOSITE_OP_REGISTRY.get(value)


__all__ = [
    "COMPOSITE_OP_REGISTRY",
    "DEFAULT_COMPOSITE_OP",
    "CompositeOpInfo",
    "composite_op_info",
]

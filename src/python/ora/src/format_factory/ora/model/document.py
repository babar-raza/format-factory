"""ORA-DOCUMENT-001 — the image document and canvas model.

"The root image element requires positive integer w and h attributes and a
version string identifying the OpenRaster specification profile."

"Since profile 0.0.3, xres and yres are optional positive integer
pixels-per-inch values that must be specified together and default to 72."

"Reject invalid values without altering the document" applies to
construction, not only to XML parsing (see model/stack.py's identical
rule for `OraNode`): `dataclasses.replace()` calls `__init__` again, which
runs `__post_init__`, so a caller building or editing an `OraDocument`
directly is held to the same w/h/xres/yres domain invariants
codec/stack_xml.py's parser enforces, not a laxer in-memory one. The one
invariant `__post_init__` deliberately does NOT re-check is "xres and yres
must be specified together": once constructed, xres/yres are always both
present (defaulted to 72 when absent), so "specified together" is a
property of the XML wire form the parser reads, not of the constructed
value -- there is no absent/present distinction left to validate here.
Canvas-area overflow (`checked_product` against a caller's resource
budget) is likewise a parse-time resource-limit concern, not a domain
invariant of the value itself, and stays in codec/stack_xml.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import OraValidationError
from .stack import OraStack

#: The specification's resolution default when xres/yres are absent.
DEFAULT_RESOLUTION_PPI = 72


def _require_positive(value: int, *, label: str) -> None:
    if value <= 0:
        raise OraValidationError(f"{label} must be a positive integer, got {value}")


@dataclass(frozen=True)
class OraDocument:
    """A parsed OpenRaster document: canvas, profile, resolution, root stack."""

    width: int
    height: int
    version: str
    root: OraStack
    xres: int = DEFAULT_RESOLUTION_PPI
    yres: int = DEFAULT_RESOLUTION_PPI
    #: Non-empty only when codec/stack_xml.py's own parse_stack(mode=TOLERANT)
    #: recovered from a defect STRICT mode would have refused (currently: a
    #: missing root version attribute). Always empty for a document built
    #: directly in memory or parsed under STRICT mode.
    recovery_actions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_positive(self.width, label="width")
        _require_positive(self.height, label="height")
        if not self.version:
            raise OraValidationError("version must be a non-empty string")
        _require_positive(self.xres, label="xres")
        _require_positive(self.yres, label="yres")

    @property
    def pixel_count(self) -> int:
        """Canvas area. Validated with checked arithmetic at parse time, so this
        is safe to use for allocation sizing."""
        return self.width * self.height


__all__ = ["DEFAULT_RESOLUTION_PPI", "OraDocument"]

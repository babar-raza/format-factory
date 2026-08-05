"""Parse `stack.xml` into an OpenRaster document (ORA-STACK-001, ORA-DOCUMENT-001).

This reads untrusted XML out of an untrusted archive, so it is bounded and
suspicious before it is convenient:

* a doctype is refused outright rather than bounded, because entity expansion is
  the classic XML denial-of-service and file-disclosure vector and "no doctype"
  is far easier to prove than "safe doctype";
* node count and nesting depth are checked against the caller's
  `ResourceLimits` while walking, not after building a full tree;
* the canvas area is validated with `checked_product`, because `w * h` is a
  number callers allocate against.

Attribute parsing is strict on purpose. Every accessor below refuses values the
specification does not allow instead of coercing them, since a silently coerced
opacity or visibility changes the rendered image without telling anyone.
"""

from __future__ import annotations

import re
from xml.etree import ElementTree

from format_factory.core import DEFAULT_LIMITS, CheckedArithmeticError, ResourceLimits, checked_product, reject_unsafe_xml

from ..errors import OraLimitError, OraValidationError
from ..model.document import DEFAULT_RESOLUTION_PPI, OraDocument
from ..model.stack import (
    DEFAULT_COMPOSITE_OP,
    DEFAULT_VISIBILITY,
    VISIBILITY_VALUES,
    OraChild,
    OraLayer,
    OraStack,
    OraText,
)

ROOT_ELEMENT = "image"

#: Strict decimal integer. `int()` alone would accept " 8", "+8", "8_0" and
#: unicode digits, none of which the specification permits.
_INTEGER = re.compile(r"^-?[0-9]+$")


def _require(element: ElementTree.Element, attribute: str) -> str:
    value = element.get(attribute)
    if value is None:
        raise OraValidationError(
            f"<{element.tag}> is missing the required {attribute!r} attribute"
        )
    return value


def _positive_integer(raw: str, *, label: str) -> int:
    if not _INTEGER.match(raw):
        raise OraValidationError(f"{label} must be a decimal integer, got {raw!r}")
    value = int(raw)
    if value <= 0:
        raise OraValidationError(f"{label} must be positive, got {value}")
    return value


def _signed_integer(raw: str, *, label: str) -> int:
    if not _INTEGER.match(raw):
        raise OraValidationError(f"{label} must be a decimal integer, got {raw!r}")
    return int(raw)


def _opacity(raw: str | None) -> float:
    """"Stack and layer opacity is a floating-point value in the inclusive range
    zero through one." Both endpoints are legal; NaN is not."""
    if raw is None:
        return 1.0
    try:
        value = float(raw)
    except ValueError as exc:
        raise OraValidationError(f"opacity must be a number, got {raw!r}") from exc
    if value != value:  # NaN compares unequal to itself and would pass < / >
        raise OraValidationError("opacity must be a number, got NaN")
    if not 0.0 <= value <= 1.0:
        raise OraValidationError(
            f"opacity must be within the inclusive range 0 through 1, got {value}"
        )
    return value


def _visibility(raw: str | None) -> str:
    if raw is None:
        return DEFAULT_VISIBILITY
    if raw not in VISIBILITY_VALUES:
        raise OraValidationError(
            f"visibility accepts only {sorted(VISIBILITY_VALUES)}, got {raw!r}"
        )
    return raw


def _validate_src(raw: str, *, element: str) -> str:
    """A src is an archive-root-relative member path, so it can escape exactly
    the way a member name can. The container refuses traversing member names;
    this refuses the same escape arriving through an attribute."""
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


def _common(element: ElementTree.Element) -> dict[str, object]:
    return {
        "name": element.get("name"),
        "x": _signed_integer(element.get("x", "0"), label=f"<{element.tag}> x"),
        "y": _signed_integer(element.get("y", "0"), label=f"<{element.tag}> y"),
        "opacity": _opacity(element.get("opacity")),
        "visibility": _visibility(element.get("visibility")),
        "composite_op": element.get("composite-op", DEFAULT_COMPOSITE_OP),
    }


class _Walker:
    """Builds the tree while counting nodes and depth against the limits."""

    def __init__(self, limits: ResourceLimits) -> None:
        self.limits = limits
        self.nodes = 0

    def _count(self) -> None:
        self.nodes += 1
        if self.nodes > self.limits.max_xml_nodes:
            raise OraLimitError(
                f"stack.xml declares more than {self.limits.max_xml_nodes} nodes"
            )

    def child(self, element: ElementTree.Element, depth: int) -> OraChild:
        self._count()
        if depth > self.limits.max_nesting_depth:
            raise OraLimitError(
                f"stack.xml nests deeper than the limit of "
                f"{self.limits.max_nesting_depth}"
            )

        if element.tag == "stack":
            return self.stack(element, depth)
        if element.tag == "layer":
            return OraLayer(
                src=_validate_src(_require(element, "src"), element="layer"),
                **_common(element),  # type: ignore[arg-type]
            )
        if element.tag == "text":
            source = element.get("src")
            return OraText(
                src=_validate_src(source, element="text") if source else None,
                **_common(element),  # type: ignore[arg-type]
            )
        raise OraValidationError(
            f"<{element.tag}> is not a permitted stack child; a stack element "
            "contains nested stack, layer, or text elements"
        )

    def stack(self, element: ElementTree.Element, depth: int) -> OraStack:
        # Document order IS visual order, uppermost first. Never sorted.
        children = tuple(self.child(child, depth + 1) for child in element)
        return OraStack(
            children=children,
            isolation=element.get("isolation", "auto"),
            **_common(element),  # type: ignore[arg-type]
        )


def _resolution(element: ElementTree.Element) -> tuple[int, int]:
    """"optional positive integer pixels-per-inch values that must be specified
    together and default to 72."

    One alone is an error rather than a half-default: defaulting the missing
    half would silently invent a resolution the document never declared, and a
    non-square-pixel document would be rendered wrong without complaint.
    """
    xres, yres = element.get("xres"), element.get("yres")
    if xres is None and yres is None:
        return DEFAULT_RESOLUTION_PPI, DEFAULT_RESOLUTION_PPI
    if xres is None:
        raise OraValidationError("yres was specified without xres; both are required together")
    if yres is None:
        raise OraValidationError("xres was specified without yres; both are required together")
    return (
        _positive_integer(xres, label="xres"),
        _positive_integer(yres, label="yres"),
    )


def parse_stack(payload: bytes, *, limits: ResourceLimits = DEFAULT_LIMITS) -> OraDocument:
    """Parse `stack.xml` bytes into an `OraDocument`."""
    if len(payload) > limits.max_header_bytes:
        raise OraLimitError(
            f"stack.xml is {len(payload)} bytes, over the limit of "
            f"{limits.max_header_bytes}"
        )

    reject_unsafe_xml(payload, error_class=OraValidationError)

    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise OraValidationError(f"stack.xml is not well-formed XML: {exc}") from exc

    if root.tag != ROOT_ELEMENT:
        raise OraValidationError(
            f"stack.xml root element must be <{ROOT_ELEMENT}>, got <{root.tag}>"
        )

    width = _positive_integer(_require(root, "w"), label="image w")
    height = _positive_integer(_require(root, "h"), label="image h")
    version = _require(root, "version")
    xres, yres = _resolution(root)

    # w*h is a number callers allocate against, so it is bounded before it is
    # believed. The ceiling is the caller's own decompressed-bytes budget.
    try:
        checked_product(
            (width, height), ceiling=limits.max_decompressed_bytes, label="canvas pixel count"
        )
    except CheckedArithmeticError as exc:
        raise OraLimitError(f"canvas is too large: {exc}") from exc

    stacks = [child for child in root if child.tag == "stack"]
    if len(stacks) != 1:
        raise OraValidationError(
            f"<image> must contain exactly one root <stack>, found {len(stacks)}"
        )

    walker = _Walker(limits)
    return OraDocument(
        width=width,
        height=height,
        version=version,
        xres=xres,
        yres=yres,
        root=walker.stack(stacks[0], 0),
    )


__all__ = ["ROOT_ELEMENT", "parse_stack"]

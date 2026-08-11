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
from ..modes import ReadMode

#: Used only when ReadMode.TOLERANT recovers a root <image> with no version
#: attribute. Deliberately not a real OpenRaster version string (those are
#: dotted-numeric, e.g. "0.0.5") so it can never be mistaken for one --
#: OraDocument.version stays a non-empty str (its own __post_init__ invariant)
#: without this package inventing a specific profile the document never
#: declared.
UNSPECIFIED_VERSION = "unspecified (ReadMode.TOLERANT recovery)"
from ..model.stack import (
    DEFAULT_COMPOSITE_OP,
    DEFAULT_VISIBILITY,
    OraChild,
    OraLayer,
    OraStack,
    OraText,
    validate_opacity,
    validate_src,
    validate_visibility,
)

ROOT_ELEMENT = "image"

#: Strict decimal integer. `int()` alone would accept " 8", "+8", "8_0" and
#: unicode digits, none of which the specification permits.
_INTEGER = re.compile(r"^-?[0-9]+$")

#: The XML declaration's encoding pseudo-attribute, if present, must appear on
#: the very first line per the XML spec -- this only ever looks at a short
#: prefix of the payload, never the whole document.
_XML_DECLARATION_ENCODING = re.compile(rb'^<\?xml\b[^>]*\bencoding=["\']([^"\']+)["\']')


def _require_utf8(payload: bytes) -> None:
    """"The required stack.xml archive member is a UTF-8 encoded XML
    document." `ElementTree.fromstring` alone does not enforce this -- it
    happily parses any encoding its declaration names, and silently accepts
    non-UTF-8 bytes when no declaration is present at all (falling back to
    Python's permissive default decoding). Both are spec violations this
    package refuses explicitly rather than passing through mishandled."""
    declared = _XML_DECLARATION_ENCODING.match(payload)
    if declared is not None and declared.group(1).decode("ascii", "replace").lower() != "utf-8":
        raise OraValidationError(
            f"stack.xml must be UTF-8 encoded, got encoding={declared.group(1)!r}"
        )
    try:
        payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OraValidationError(f"stack.xml is not valid UTF-8: {exc}") from exc


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
    zero through one." Both endpoints are legal; NaN is not.

    Range/NaN enforcement delegates to `model.stack.validate_opacity` -- the
    same check `OraNode.__post_init__` runs on every construction, parser or
    programmatic -- so the two routes cannot silently diverge.
    """
    if raw is None:
        return 1.0
    try:
        value = float(raw)
    except ValueError as exc:
        raise OraValidationError(f"opacity must be a number, got {raw!r}") from exc
    validate_opacity(value)
    return value


def _visibility(raw: str | None) -> str:
    if raw is None:
        return DEFAULT_VISIBILITY
    validate_visibility(raw)
    return raw


#: XML attribute name -> OraNode field name, for every default-having
#: attribute ORA-PRESERVE-001's explicit_attributes tracks. "composite-op"
#: is the XML spelling; the dataclass field is "composite_op".
_TRACKED_ATTRIBUTES = {
    "x": "x",
    "y": "y",
    "opacity": "opacity",
    "visibility": "visibility",
    "composite-op": "composite_op",
}


def _explicit_attributes(
    element: ElementTree.Element, *, extra_tracked: tuple[str, ...] = ()
) -> frozenset[str]:
    """Which of _TRACKED_ATTRIBUTES' own XML names (plus any stack-specific
    `extra_tracked` names, e.g. "isolation") this element's attrib actually
    contains -- computed once, at the same point every other default-having
    value is read, so it can never drift from what _common()/isolation
    parsing itself considers "present"."""
    tracked = tuple(_TRACKED_ATTRIBUTES) + extra_tracked
    return frozenset(xml_name for xml_name in tracked if xml_name in element.attrib)


def _common(
    element: ElementTree.Element, *, extra_tracked: tuple[str, ...] = ()
) -> dict[str, object]:
    return {
        "name": element.get("name"),
        "x": _signed_integer(element.get("x", "0"), label=f"<{element.tag}> x"),
        "y": _signed_integer(element.get("y", "0"), label=f"<{element.tag}> y"),
        "opacity": _opacity(element.get("opacity")),
        "visibility": _visibility(element.get("visibility")),
        "composite_op": element.get("composite-op", DEFAULT_COMPOSITE_OP),
        "explicit_attributes": _explicit_attributes(element, extra_tracked=extra_tracked),
    }


class _Walker:
    """Builds the tree while counting nodes, depth, and cumulative
    attribute count against the limits -- each checked immediately after
    being updated, not after the full tree is built. Matches the identical
    attribute-count vector already proven for the equivalent ubl and xliff
    readers' own tree-limit walks."""

    def __init__(self, limits: ResourceLimits) -> None:
        self.limits = limits
        self.nodes = 0
        self.attributes = 0

    def count_element(self, element: ElementTree.Element) -> None:
        """Count one element's node and its own attributes against the
        limits. Called for every element this walker ever sees, including
        the <image> root and the top-level <stack> -- neither is reachable
        through child()'s own recursive dispatch, so parse_stack calls this
        directly for both before handing the top stack to stack()."""
        self.nodes += 1
        if self.nodes > self.limits.max_xml_nodes:
            raise OraLimitError(
                f"stack.xml declares more than {self.limits.max_xml_nodes} nodes"
            )
        self.attributes += len(element.attrib)
        if self.attributes > self.limits.max_entries:
            raise OraLimitError(
                f"stack.xml declares more than {self.limits.max_entries} "
                "cumulative attributes"
            )

    def child(self, element: ElementTree.Element, depth: int) -> OraChild:
        self.count_element(element)
        if depth > self.limits.max_nesting_depth:
            raise OraLimitError(
                f"stack.xml nests deeper than the limit of "
                f"{self.limits.max_nesting_depth}"
            )

        if element.tag == "stack":
            return self.stack(element, depth)
        if element.tag == "layer":
            return OraLayer(
                src=validate_src(_require(element, "src"), element="layer"),
                **_common(element),  # type: ignore[arg-type]
            )
        if element.tag == "text":
            source = element.get("src")
            return OraText(
                src=validate_src(source, element="text") if source else None,
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
            **_common(element, extra_tracked=("isolation",)),  # type: ignore[arg-type]
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


def parse_stack(
    payload: bytes,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
    mode: ReadMode = ReadMode.STRICT,
) -> OraDocument:
    """Parse `stack.xml` bytes into an `OraDocument`. `mode` controls exactly
    one thing: whether a root `<image>` missing the required `version`
    attribute is refused (STRICT, unchanged default) or recovered with
    `UNSPECIFIED_VERSION` and a `recovery_actions` entry (TOLERANT). Every
    other requirement in this function -- `w`/`h`, well-formedness, the
    doctype refusal, resource limits -- is unconditional in both modes."""
    if len(payload) > limits.max_header_bytes:
        raise OraLimitError(
            f"stack.xml is {len(payload)} bytes, over the limit of "
            f"{limits.max_header_bytes}"
        )

    reject_unsafe_xml(payload, error_class=OraValidationError)
    _require_utf8(payload)

    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise OraValidationError(f"stack.xml is not well-formed XML: {exc}") from exc

    if root.tag != ROOT_ELEMENT:
        raise OraValidationError(
            f"stack.xml root element must be <{ROOT_ELEMENT}>, got <{root.tag}>"
        )

    walker = _Walker(limits)
    walker.count_element(root)

    width = _positive_integer(_require(root, "w"), label="image w")
    height = _positive_integer(_require(root, "h"), label="image h")
    recovery: list[str] = []
    declared_version = root.get("version")
    if declared_version is None:
        if mode is ReadMode.STRICT:
            raise OraValidationError("<image> is missing the required 'version' attribute")
        version = UNSPECIFIED_VERSION
        recovery.append(
            "root <image> had no 'version' attribute; treated as an unspecified "
            "profile version rather than assuming a specific one (ReadMode.TOLERANT)"
        )
    else:
        version = declared_version
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

    walker.count_element(stacks[0])
    return OraDocument(
        width=width,
        height=height,
        version=version,
        xres=xres,
        yres=yres,
        root=walker.stack(stacks[0], 0),
        recovery_actions=tuple(recovery),
    )


__all__ = ["ROOT_ELEMENT", "UNSPECIFIED_VERSION", "parse_stack"]

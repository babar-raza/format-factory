"""ORA-PRESERVE-001 -- report what a save would lose, before it loses it.

"Report every construct that cannot be preserved before saving, through a
loss report API, rather than failing silently."

`lifecycle.dumps`/`dump` already implement the other half of the baseline
(`PreservationMode.LOSSLESS` re-emits the original archive members verbatim,
so nothing is lost; `CANONICAL` regenerates stack.xml from the model). What
neither of them does is tell a caller, before choosing CANONICAL, which
constructs that regeneration would actually drop.

The model (`OraNode` and its subclasses) captures exactly the attributes the
specification defines: name, x, y, opacity, visibility, composite-op,
isolation, src. Anything else present as an XML attribute on <image>,
<stack>, <layer> or <text> -- a vendor extension, a future-profile attribute
this library does not yet model -- is silently ignored by the parser and
never re-emitted by `_canonical_stack_xml`. It survives a LOSSLESS round
trip (the original bytes are kept verbatim) but would not survive a
CANONICAL one. That gap is real and checkable without inventing anything:
this module re-reads the same original stack.xml bytes the image was loaded
from and diffs their actual attributes against the known, modeled set.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree

from .codec.container import STACK_MEMBER
from .lifecycle import OraImage, PreservationMode

#: Attributes `_canonical_stack_xml` (lifecycle.py) and the parser's
#: `_common()` (codec/stack_xml.py) both recognize, per element tag. Anything
#: else present in the original XML is read by neither and would not survive
#: CANONICAL regeneration.
_KNOWN_ATTRIBUTES: dict[str, frozenset[str]] = {
    "image": frozenset({"w", "h", "version", "xres", "yres"}),
    "stack": frozenset(
        {"name", "x", "y", "opacity", "visibility", "composite-op", "isolation"}
    ),
    "layer": frozenset({"name", "x", "y", "opacity", "visibility", "composite-op", "src"}),
    "text": frozenset({"name", "x", "y", "opacity", "visibility", "composite-op", "src"}),
}


@dataclass(frozen=True, slots=True)
class LossItem:
    """One construct that CANONICAL regeneration would not preserve."""

    path: tuple[str, ...]
    element: str
    attribute: str
    value: str

    @property
    def message(self) -> str:
        """Human-readable description of this one dropped construct."""
        return (
            f"<{self.element}> attribute {self.attribute!r}={self.value!r} at "
            f"{'/'.join(self.path)} is not modeled and would be dropped by "
            "CANONICAL regeneration"
        )


@dataclass(frozen=True, slots=True)
class LossReport:
    """What a save in a given `PreservationMode` would lose, if anything."""

    items: tuple[LossItem, ...]

    @property
    def is_lossless(self) -> bool:
        """True if CANONICAL regeneration would drop nothing (no LossItems)."""
        return not self.items


def _walk(element: ElementTree.Element, path: tuple[str, ...], items: list[LossItem]) -> None:
    known = _KNOWN_ATTRIBUTES.get(element.tag)
    if known is not None:
        for name, value in element.attrib.items():
            if name not in known:
                items.append(
                    LossItem(path=path, element=element.tag, attribute=name, value=value)
                )
    sibling_counts: dict[str, int] = {}
    for child in element:
        index = sibling_counts.get(child.tag, 0)
        sibling_counts[child.tag] = index + 1
        _walk(child, path + (f"{child.tag}[{index}]",), items)


def check_preservation(image: OraImage, *, target: PreservationMode) -> LossReport:
    """Report what saving `image` in `target` mode would lose.

    LOSSLESS never loses anything -- the original archive members, including
    the original stack.xml bytes, are re-emitted verbatim -- so this returns
    an empty report without inspecting the document. CANONICAL regenerates
    stack.xml from the model, so this re-parses the *original* stack.xml
    bytes the image was loaded from (already validated safe once, at load
    time) and reports every attribute present in the original that the
    model does not carry and `_canonical_stack_xml` would therefore not
    re-emit.
    """
    if target is PreservationMode.LOSSLESS:
        return LossReport(items=())

    root = ElementTree.fromstring(image.members[STACK_MEMBER])
    items: list[LossItem] = []
    _walk(root, (f"{root.tag}[0]",), items)
    return LossReport(items=tuple(items))


__all__ = ["LossItem", "LossReport", "check_preservation"]

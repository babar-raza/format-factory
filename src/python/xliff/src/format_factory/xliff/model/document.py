"""Typed XLIFF 2.x core model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .inline import InlineElement, InlineNode, flatten_inline_content

_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _copy_inline_nodes(nodes: list[InlineNode]) -> list[InlineNode]:
    """Deep-copy inline content so source and target never share mutable codes."""

    result: list[InlineNode] = []
    for node in nodes:
        if isinstance(node, str):
            result.append(node)
        else:
            result.append(
                InlineElement(
                    tag=node.tag,
                    attributes=dict(node.attributes),
                    content=_copy_inline_nodes(node.content),
                    tail=node.tail,
                )
            )
    return result


@dataclass(slots=True)
class ExtensionNode:
    """An unknown or not-yet-typed namespaced XML subtree."""

    tag: str
    xml: bytes


@dataclass(slots=True)
class DataElement:
    """`<data>` -- storage for the original (native) code data of one inline
    code, referenced by `id` from an inline element's `dataRef`,
    `dataRefStart`, or `dataRefEnd` attribute (XLIFF Core 4.2.2.11 data).

    Content is modeled the same way as source/target inline content
    (`list[InlineNode]`) since `<data>`'s own content model -- non-
    translatable text plus zero-or-more `<cp>` elements -- is structurally
    the same shape; a literal `<cp>` child simply round-trips as a generic
    `InlineElement(tag="cp", ...)`, matching this package's existing
    "unknown tags round-trip generically" precedent rather than requiring
    dedicated `<cp>` modeling.
    """

    id: str
    content: list[InlineNode] = field(default_factory=list)
    dir: str = ""
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Note:
    text: str
    id: str = ""
    applies_to: str = ""
    category: str = ""
    priority: int | None = None
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Segment:
    """A segment or ignorable item with structured inline content."""

    id: str
    source: list[InlineNode]
    target: list[InlineNode] | None = None
    kind: str = "segment"
    state: str = ""
    sub_state: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    source_attributes: dict[str, str] = field(default_factory=dict)
    target_attributes: dict[str, str] = field(default_factory=dict)
    extensions: list[ExtensionNode] = field(default_factory=list)

    def create_target_from_source(self, *, code_policy: str = "copy") -> None:
        """Create a target using an explicit safe inline-code policy.

        ``copy`` deep-copies all source text and inline codes, ``strip`` copies
        only rendered text, and ``empty`` creates a deliberately empty target.
        Existing targets are never overwritten implicitly.
        """

        if self.target is not None:
            raise ValueError("target already exists; edit or replace it explicitly")
        if code_policy == "copy":
            self.target = _copy_inline_nodes(self.source)
        elif code_policy == "strip":
            self.target = [flatten_inline_content(self.source)]
        elif code_policy == "empty":
            self.target = []
        else:
            raise ValueError("code_policy must be 'copy', 'strip', or 'empty'")


@dataclass(slots=True)
class Unit:
    id: str
    children: list[Segment | ExtensionNode] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    original_data: list[DataElement] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def segments(self) -> list[Segment]:
        return [value for value in self.children if isinstance(value, Segment)]


@dataclass(slots=True)
class Group:
    id: str
    children: list[Group | Unit | ExtensionNode] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def iter_units(self) -> Iterator[Unit]:
        for child in self.children:
            if isinstance(child, Unit):
                yield child
            elif isinstance(child, Group):
                yield from child.iter_units()


@dataclass(slots=True)
class XliffFile:
    id: str
    children: list[Group | Unit | ExtensionNode] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def iter_units(self) -> Iterator[Unit]:
        for child in self.children:
            if isinstance(child, Unit):
                yield child
            elif isinstance(child, Group):
                yield from child.iter_units()


@dataclass(slots=True)
class XliffDocument:
    """XLIFF 2.0/2.1 document; external references stay passive strings."""

    version: str
    source_language: str
    target_language: str | None
    children: list[XliffFile | ExtensionNode]
    attributes: dict[str, str] = field(default_factory=dict)
    namespace: str = "urn:oasis:names:tc:xliff:document:2.0"
    #: The version this document's file actually declared, set once by the
    #: reader at parse time (XLIFF-LIFECYCLE-001). `version` is the mutable,
    #: currently-declared value dumps()/dump() will write; editing it (a
    #: plain field assignment, since this model is not frozen) does not
    #: touch `detected_version` -- there is no reconstruction step to
    #: accidentally reset it through, unlike a frozen/tree-based model
    #: would need. None on a document built directly in memory, since
    #: nothing was detected.
    detected_version: str | None = None

    @property
    def xml_space(self) -> str:
        """"The xml:space attribute specifies how white spaces... are to
        be treated. Value description: default or preserve... Default
        value: ...When used in <xliff>: The value default."

        Distinct from per-element xml:space inheritance (file/group/unit/
        source/target/data each default to their PARENT's effective
        value, not a document-wide constant) -- that broader chain is not
        modeled here; this property answers only the one thing this
        obligation's own rule_text names: the root's own default.
        """
        return self.attributes.get(_XML_SPACE, "default")

    @property
    def files(self) -> list[XliffFile]:
        return [value for value in self.children if isinstance(value, XliffFile)]

    def iter_units(self) -> Iterator[Unit]:
        for file in self.files:
            yield from file.iter_units()

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def unit_count(self) -> int:
        return sum(1 for _ in self.iter_units())

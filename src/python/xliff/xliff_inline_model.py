"""XLIFF inline markup domain model — the `InlineElement` structural node.

OASIS XLIFF 2.1 Specification, Chapter 5 "Inline Markup", defines five core
inline elements that may appear inside ``<source>``/``<target>`` segment
content: ``<pc>`` (paired code), ``<sc>``/``<ec>`` (isolated start/end code),
``<ph>`` (inline standalone marker), and ``<mrk>`` (annotation marker).

This module holds only the domain model for that structure. Parsing XML into
this shape and serializing it back is a separate concern — see
``xliff_inline.py``'s ``parse_inline_content``/``serialize_inline_content``.

Spec ref: FACT-XLIFF-101.
"""

from __future__ import annotations

from typing import Any, Union

InlineNode = Union[str, "InlineElement"]

#: Attribute names that carry a reference into the <originalData> table,
#: checked in spec-preferred order. The first one present on an element is
#: exposed as its `.data_ref` convenience value; the full raw attribute set
#: remains available via `.attributes` regardless.
_DATA_REF_ATTRS = ("dataRef", "dataRefStart", "dataRefEnd", "startRef")


class InlineElement:
    """Structured representation of one XLIFF inline markup element.

    Preserves the element's tag (pc/sc/ec/ph/mrk), every raw XML attribute
    it carried (so ``id``, ``dataRef``, ``dataRefStart``, ``dataRefEnd``,
    ``type``, ``subType``, etc. all survive untouched), its nested content
    (recursively, for pc/mrk which may contain text and further inline
    elements), and its ``tail`` text (the plain text immediately following
    this element's closing tag, before the next sibling — mirrors
    ``xml.etree.ElementTree`` tail semantics so serialization can reproduce
    the exact original text flow).

    Spec ref: FACT-XLIFF-101 (OASIS XLIFF 2.1, Chapter 5 Inline Markup).
    """

    __slots__ = ("tag", "attributes", "content", "tail")

    def __init__(
        self,
        tag: str,
        attributes: dict[str, str] | None = None,
        content: list[InlineNode] | None = None,
        tail: str = "",
    ) -> None:
        self.tag = tag
        self.attributes: dict[str, str] = dict(attributes) if attributes else {}
        self.content: list[InlineNode] = list(content) if content is not None else []
        self.tail = tail or ""

    @property
    def id(self) -> str:
        """Return this element's ``id`` attribute (empty string if absent)."""
        return self.attributes.get("id", "")

    @property
    def data_ref(self) -> str | None:
        """Return the first data-reference attribute present, or None.

        Checks ``dataRef`` (ph/pc), ``dataRefStart``/``dataRefEnd`` (pc),
        and ``startRef`` (ec) in that order.
        """
        for key in _DATA_REF_ATTRS:
            if key in self.attributes:
                return self.attributes[key]
        return None

    def plain_text(self) -> str:
        """Return this element's nested content flattened to plain text.

        Does not include this element's own `.tail` — tail text belongs to
        the parent's content flow, not to the element itself.
        """
        return flatten_inline_content(self.content)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable structural dict for this element."""
        return {
            "kind": "element",
            "tag": self.tag,
            "attributes": dict(self.attributes),
            "content": [
                node if isinstance(node, str) else node.to_dict()
                for node in self.content
            ],
            "tail": self.tail,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InlineElement":
        """Reconstruct an `InlineElement` from `to_dict()` output."""
        content: list[InlineNode] = []
        for node in data.get("content", []):
            if isinstance(node, str):
                content.append(node)
            else:
                content.append(cls.from_dict(node))
        return cls(
            tag=data["tag"],
            attributes=data.get("attributes", {}),
            content=content,
            tail=data.get("tail", ""),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InlineElement):
            return NotImplemented
        return (
            self.tag == other.tag
            and self.attributes == other.attributes
            and self.content == other.content
            and self.tail == other.tail
        )

    def __repr__(self) -> str:
        return f"InlineElement(tag={self.tag!r}, id={self.id!r}, tail={self.tail!r})"


def flatten_inline_content(content: list[InlineNode]) -> str:
    """Flatten a structured content list to a plain-text string.

    Used both by `InlineElement.plain_text` and by the codec to derive the
    convenience `source`/`target` plain-text segment fields from the
    structured `source_content`/`target_content` fields.
    """
    parts: list[str] = []
    for node in content:
        if isinstance(node, str):
            parts.append(node)
        else:
            parts.append(node.plain_text())
            parts.append(node.tail)
    return "".join(parts)

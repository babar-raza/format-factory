"""XLIFF inline markup parser/serializer — pc/sc/ec/ph/mrk structural preservation.

Prior to this module, the codec flattened all inline markup to a single
plain Python string (see the historical ``_text_content`` helper), discarding
every child element, its ``id``, and its ``dataRef``/``dataRefStart``/
``dataRefEnd`` attributes. Any real CAT-tool/TM-exported XLIFF with inline
codes — the norm, since they represent variables or formatting that MUST
survive round-trip — had its inline structure silently destroyed on every
load -> edit -> save cycle.

This module provides the load (`parse_inline_content`) and write
(`serialize_inline_content`) halves of the fix — the domain model those two
functions convert to/from, ``InlineElement``, lives in ``xliff_inline_model.py``
and is re-exported here for backward-compatible imports.

Spec ref: FACT-XLIFF-101 (OASIS XLIFF 2.1, Chapter 5 Inline Markup).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from .xliff_inline_model import InlineElement, InlineNode, flatten_inline_content

__all__ = [
    "InlineElement",
    "InlineNode",
    "flatten_inline_content",
    "parse_inline_content",
    "serialize_inline_content",
    "INLINE_TAGS",
]

#: The core XLIFF 2.1 inline elements this module understands (Chapter 5).
INLINE_TAGS = frozenset({"pc", "sc", "ec", "ph", "mrk"})


def _strip_ns(tag: str) -> str:
    """Remove a Clark-notation namespace prefix from an XML tag name."""
    if tag.startswith("{"):
        return tag[tag.index("}") + 1:]
    return tag


def parse_inline_content(elem: ET.Element) -> list[InlineNode]:
    """Parse `elem`'s text/children into a structured inline-content list.

    Inverse of `serialize_inline_content`. Every pc/sc/ec/ph/mrk child (and,
    generously, any other child element type present) becomes an
    `InlineElement` carrying its full attribute set, recursively-parsed
    content, and tail text — nothing is discarded. Plain text (`elem.text`)
    becomes a bare string as the first content entry when present.
    """
    content: list[InlineNode] = []
    if elem.text:
        content.append(elem.text)
    for child in elem:
        tag = _strip_ns(child.tag)
        content.append(
            InlineElement(
                tag=tag,
                attributes=dict(child.attrib),
                content=parse_inline_content(child),
                tail=child.tail or "",
            )
        )
    return content


def serialize_inline_content(parent: ET.Element, content: list[InlineNode], ns: str) -> None:
    """Populate `parent`'s `.text` and child elements from `content`.

    Inverse of `parse_inline_content`. Reconstructs `parent.text`, each
    child element (namespaced under `ns`) with its original attributes,
    recursively-serialized nested content, and `.tail`, so a full
    parse -> serialize round trip reproduces the original XML shape
    element-for-element.
    """
    parent.text = None
    last_child: ET.Element | None = None
    for node in content:
        if isinstance(node, str):
            if not node:
                continue
            if last_child is None:
                parent.text = (parent.text or "") + node
            else:
                last_child.tail = (last_child.tail or "") + node
        else:
            child = ET.SubElement(parent, f"{{{ns}}}{node.tag}")
            for key, value in node.attributes.items():
                child.set(key, value)
            serialize_inline_content(child, node.content, ns)
            child.tail = node.tail if node.tail else None
            last_child = child

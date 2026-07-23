"""Structured mixed content for XLIFF inline codes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


@dataclass(slots=True)
class InlineElement:
    """One inline code or namespace extension with mixed child content."""

    tag: str
    attributes: dict[str, str] = field(default_factory=dict)
    content: list[InlineNode] = field(default_factory=list)
    tail: str = ""

    @property
    def id(self) -> str:
        return self.attributes.get("id", "")

    @property
    def data_ref(self) -> str | None:
        for key in ("dataRef", "dataRefStart", "dataRefEnd", "startRef"):
            if key in self.attributes:
                return self.attributes[key]
        return None

    def plain_text(self) -> str:
        return flatten_inline_content(self.content)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "element",
            "tag": self.tag,
            "attributes": dict(self.attributes),
            "content": [
                value if isinstance(value, str) else value.to_dict()
                for value in self.content
            ],
            "tail": self.tail,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> InlineElement:
        children: list[InlineNode] = []
        for child in value.get("content", []):
            children.append(
                child if isinstance(child, str) else cls.from_dict(child)
            )
        return cls(
            tag=str(value["tag"]),
            attributes={
                str(key): str(item)
                for key, item in dict(value.get("attributes", {})).items()
            },
            content=children,
            tail=str(value.get("tail", "")),
        )


InlineNode: TypeAlias = str | InlineElement


def flatten_inline_content(content: list[InlineNode]) -> str:
    parts: list[str] = []
    for node in content:
        if isinstance(node, str):
            parts.append(node)
        else:
            parts.append(node.plain_text())
            parts.append(node.tail)
    return "".join(parts)

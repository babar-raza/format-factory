"""Typed XLIFF 2.x core model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .inline import InlineNode


@dataclass(slots=True)
class ExtensionNode:
    """An unknown or not-yet-typed namespaced XML subtree."""

    tag: str
    xml: bytes


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


@dataclass(slots=True)
class Unit:
    id: str
    children: list[Segment | ExtensionNode] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
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

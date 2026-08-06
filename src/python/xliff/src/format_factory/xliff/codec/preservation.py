"""Preservation-mode serialization and loss disclosure for XLIFF documents.

XLIFF-PRESERVE-001 requires (a) an explicit LOSSLESS-vs-CANONICAL caller
choice on ``dumps()``/``dump()``, and (b) a first-class ``LossReport``/
``check_preservation`` API describing what CANONICAL mode would drop.

Scope chosen, documented honestly rather than silently narrowed: this
model already distinguishes modeled from unmodeled content in exactly one
place -- :class:`~format_factory.xliff.model.ExtensionNode` (unrecognized
or not-yet-typed namespaced XML subtrees attached at file/group/unit/
segment level). CANONICAL mode drops every ``ExtensionNode`` in the tree;
everything else -- every typed field, and every entry in the generic
``attributes`` dict on ``Group``/``Unit``/``Segment``/``XliffFile`` --
is unconditionally preserved in both modes, because this model does not
separately distinguish a "standard" XLIFF attribute from a caller-supplied
custom one within that dict. There is nothing else in this model's
current shape for a canonical regeneration to legitimately elect to drop.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from ..model import ExtensionNode, Group, Segment, Unit, XliffDocument, XliffFile


class PreservationMode(StrEnum):
    """Caller-selectable output fidelity for ``dumps()``/``dump()``."""

    LOSSLESS = "lossless"
    CANONICAL = "canonical"


@dataclass(frozen=True, slots=True)
class LossReport:
    """Machine-readable disclosure of what CANONICAL mode would drop."""

    is_lossless: bool
    dropped_count: int
    dropped_tags: tuple[str, ...]
    detail: str


def _canonicalize_segment(segment: Segment) -> tuple[Segment, list[str]]:
    if not segment.extensions:
        return segment, []
    dropped = [node.tag for node in segment.extensions]
    return replace(segment, extensions=[]), dropped


def _canonicalize_unit(unit: Unit) -> tuple[Unit, list[str]]:
    dropped: list[str] = []
    kept: list[Segment | ExtensionNode] = []
    for child in unit.children:
        if isinstance(child, ExtensionNode):
            dropped.append(child.tag)
        else:
            new_segment, segment_dropped = _canonicalize_segment(child)
            kept.append(new_segment)
            dropped.extend(segment_dropped)
    return replace(unit, children=kept), dropped


def _canonicalize_group(group: Group) -> tuple[Group, list[str]]:
    dropped: list[str] = []
    kept: list[Group | Unit | ExtensionNode] = []
    for child in group.children:
        if isinstance(child, ExtensionNode):
            dropped.append(child.tag)
        elif isinstance(child, Unit):
            new_unit, unit_dropped = _canonicalize_unit(child)
            kept.append(new_unit)
            dropped.extend(unit_dropped)
        else:
            new_group, group_dropped = _canonicalize_group(child)
            kept.append(new_group)
            dropped.extend(group_dropped)
    return replace(group, children=kept), dropped


def _canonicalize_file(value: XliffFile) -> tuple[XliffFile, list[str]]:
    dropped: list[str] = []
    kept: list[Group | Unit | ExtensionNode] = []
    for child in value.children:
        if isinstance(child, ExtensionNode):
            dropped.append(child.tag)
        elif isinstance(child, Unit):
            new_unit, unit_dropped = _canonicalize_unit(child)
            kept.append(new_unit)
            dropped.extend(unit_dropped)
        else:
            new_group, group_dropped = _canonicalize_group(child)
            kept.append(new_group)
            dropped.extend(group_dropped)
    return replace(value, children=kept), dropped


def canonicalize(document: XliffDocument) -> tuple[XliffDocument, tuple[str, ...]]:
    """Return a copy of ``document`` with every ``ExtensionNode`` dropped.

    Returns the regenerated document plus the tags of every dropped node
    (in document order, duplicates included).
    """

    dropped: list[str] = []
    kept: list[XliffFile | ExtensionNode] = []
    for child in document.children:
        if isinstance(child, ExtensionNode):
            dropped.append(child.tag)
        else:
            new_file, file_dropped = _canonicalize_file(child)
            kept.append(new_file)
            dropped.extend(file_dropped)
    return replace(document, children=kept), tuple(dropped)


def check_preservation(document: XliffDocument) -> LossReport:
    """Report what CANONICAL mode would drop from ``document``.

    Does not serialize -- this walks the in-memory tree only, so it is
    cheap to call before choosing a preservation mode for ``dumps()``.
    """

    _canonical, dropped = canonicalize(document)
    if not dropped:
        return LossReport(
            is_lossless=True,
            dropped_count=0,
            dropped_tags=(),
            detail=(
                "document has no ExtensionNode content; LOSSLESS and "
                "CANONICAL output are identical"
            ),
        )
    unique_tags = tuple(sorted(set(dropped)))
    return LossReport(
        is_lossless=False,
        dropped_count=len(dropped),
        dropped_tags=unique_tags,
        detail=(
            f"CANONICAL mode drops {len(dropped)} extension element(s) "
            f"({', '.join(unique_tags)}) not present in the typed model"
        ),
    )

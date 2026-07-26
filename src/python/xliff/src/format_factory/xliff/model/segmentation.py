"""Safe, model-only XLIFF segment restructuring operations.

The core model deliberately represents inline XML as token sequences.  These
operations therefore split only between top-level tokens: no inline element is
silently cut in half, and spanning ``sc``/``ec`` pairs cannot be orphaned by a
new segment boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ..errors import XliffValidationError
from .document import Segment, Unit
from .inline import InlineElement, InlineNode


@dataclass(frozen=True, slots=True)
class SegmentMapping:
    """Machine-readable identity mapping emitted after a structural edit."""

    operation: str
    unit_id: str
    replacements: Mapping[str, tuple[str, ...]]

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "unit_id": self.unit_id,
            "replacements": {
                source: list(targets)
                for source, targets in sorted(self.replacements.items())
            },
        }


def _segment_position(unit: Unit, segment_id: str) -> tuple[int, Segment]:
    matches = [
        (index, child)
        for index, child in enumerate(unit.children)
        if isinstance(child, Segment) and child.id == segment_id
    ]
    if len(matches) != 1:
        raise XliffValidationError(
            f"unit {unit.id!r} must contain exactly one segment {segment_id!r}"
        )
    return matches[0]


def _require_fresh_ids(unit: Unit, ids: tuple[str, ...], replacing: set[str]) -> None:
    if any(not value for value in ids) or len(set(ids)) != len(ids):
        raise XliffValidationError("replacement segment ids must be non-empty and distinct")
    existing = {
        child.id
        for child in unit.children
        if isinstance(child, Segment) and child.id not in replacing
    }
    conflict = sorted(existing.intersection(ids))
    if conflict:
        raise XliffValidationError(
            "replacement segment id already exists in unit: " + ", ".join(conflict)
        )


def _split_content(
    content: list[InlineNode], index: int, *, label: str
) -> tuple[list[InlineNode], list[InlineNode]]:
    if not 0 < index < len(content):
        raise XliffValidationError(
            f"{label} split index must fall between top-level inline tokens"
        )
    first, second = list(content[:index]), list(content[index:])
    _require_closed_spanning_codes(first, label=label)
    _require_closed_spanning_codes(second, label=label)
    return first, second


def _require_closed_spanning_codes(content: list[InlineNode], *, label: str) -> None:
    """Reject a boundary that leaves a direct spanning pair on either side.

    Nested inline content is indivisible at this API boundary, so inspecting
    direct ``sc`` and ``ec`` tokens is sufficient.  This is intentionally
    conservative: rejecting an ambiguous edit is safer than duplicating or
    dropping an original-data reference.
    """

    open_codes: set[str] = set()
    for node in content:
        if not isinstance(node, InlineElement):
            continue
        if node.tag == "sc" and node.id:
            open_codes.add(node.id)
        elif node.tag == "ec":
            start_ref = node.attributes.get("startRef", "")
            if not start_ref or start_ref not in open_codes:
                raise XliffValidationError(
                    f"{label} boundary would orphan a paired inline code"
                )
            open_codes.remove(start_ref)
    if open_codes:
        raise XliffValidationError(
            f"{label} boundary would orphan a paired inline code"
        )


def _copy_segment(
    source: Segment,
    *,
    identifier: str,
    content: list[InlineNode],
    target: list[InlineNode] | None,
) -> Segment:
    return Segment(
        id=identifier,
        source=content,
        target=target,
        kind=source.kind,
        state=source.state,
        sub_state=source.sub_state,
        attributes=dict(source.attributes),
        extensions=list(source.extensions),
    )


def split_segment(
    unit: Unit,
    segment_id: str,
    *,
    source_index: int,
    first_id: str,
    second_id: str,
    target_index: int | None = None,
) -> SegmentMapping:
    """Split one segment at token boundaries and return its identity mapping.

    A translated segment requires an explicit target boundary.  Silently
    inferring a target split from a source offset is unsafe because translated
    text is not positionally equivalent to source text.
    """

    position, original = _segment_position(unit, segment_id)
    if original.kind != "segment":
        raise XliffValidationError("only XLIFF segment elements can be split")
    if original.extensions:
        raise XliffValidationError(
            "segments with extension children require a format-specific segmentation adapter"
        )
    _require_fresh_ids(unit, (first_id, second_id), {segment_id})
    first_source, second_source = _split_content(
        original.source, source_index, label="source"
    )
    if original.target is None:
        if target_index is not None:
            raise XliffValidationError("an untranslated segment has no target boundary")
        first_target = second_target = None
    else:
        if target_index is None:
            raise XliffValidationError(
                "splitting a translated segment requires target_index"
            )
        first_target, second_target = _split_content(
            original.target, target_index, label="target"
        )
    first = _copy_segment(
        original, identifier=first_id, content=first_source, target=first_target
    )
    second = _copy_segment(
        original, identifier=second_id, content=second_source, target=second_target
    )
    unit.children[position : position + 1] = [first, second]
    return SegmentMapping("split", unit.id, {segment_id: (first_id, second_id)})


def join_segments(
    unit: Unit, first_id: str, second_id: str, *, new_id: str
) -> SegmentMapping:
    """Join two adjacent, semantically compatible segments."""

    first_position, first = _segment_position(unit, first_id)
    second_position, second = _segment_position(unit, second_id)
    if second_position != first_position + 1:
        raise XliffValidationError("only adjacent segments can be joined")
    if first.kind != "segment" or second.kind != "segment":
        raise XliffValidationError("only XLIFF segment elements can be joined")
    if first.extensions or second.extensions:
        raise XliffValidationError(
            "segments with extension children require a format-specific segmentation adapter"
        )
    if (
        first.state != second.state
        or first.sub_state != second.sub_state
        or first.attributes != second.attributes
    ):
        raise XliffValidationError(
            "segments must have identical state, substate, and attributes to join"
        )
    if (first.target is None) != (second.target is None):
        raise XliffValidationError(
            "cannot join translated and untranslated segments without an explicit adapter"
        )
    _require_fresh_ids(unit, (new_id,), {first_id, second_id})
    source = [*first.source, *second.source]
    _require_closed_spanning_codes(source, label="joined source")
    if first.target is None:
        target = None
    else:
        target = [*(first.target or []), *(second.target or [])]
        _require_closed_spanning_codes(target, label="joined target")
    joined = _copy_segment(first, identifier=new_id, content=source, target=target)
    unit.children[first_position : second_position + 1] = [joined]
    return SegmentMapping(
        "join", unit.id, {first_id: (new_id,), second_id: (new_id,)}
    )


__all__ = ["SegmentMapping", "join_segments", "split_segment"]

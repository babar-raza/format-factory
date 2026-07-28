"""Pure XLIFF inspection helpers."""

from __future__ import annotations

from ..model import XliffDocument, flatten_inline_content


def translated_segment_count(document: XliffDocument) -> int:
    return sum(
        1
        for unit in document.iter_units()
        for segment in unit.segments
        if segment.target is not None and flatten_inline_content(segment.target)
    )


def untranslated_segment_count(document: XliffDocument) -> int:
    return sum(
        1
        for unit in document.iter_units()
        for segment in unit.segments
        if segment.target is None or not flatten_inline_content(segment.target)
    )


def average_source_length(document: XliffDocument) -> float:
    values = [
        len(flatten_inline_content(segment.source))
        for unit in document.iter_units()
        for segment in unit.segments
    ]
    return sum(values) / len(values) if values else 0.0


__all__ = [
    "average_source_length",
    "translated_segment_count",
    "untranslated_segment_count",
]

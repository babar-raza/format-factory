"""XLIFF analytics — translation-segment statistics derived from parsed documents.

Every function accepts a raw source (file path or bytes) and re-parses it via
``load_xliff`` internally; none require a pre-built domain model object. This
mirrors the codec's own I/O contract so analytics stay usable standalone.

Spec ref: FACT-XLIFF-002 — translation units contain <segment> elements with
required <source> and optional <target> children (OASIS XLIFF 2.1
Specification, section 2.3 Translation Units).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Union

from xliff.xliff_codec import load_xliff

spec_qname = "xliff:segment"
spec_fact_ref = "FACT-XLIFF-002"

SourceType = Union[str, Path, bytes]

__all__ = [
    "xliff_translated_segment_count",
    "xliff_untranslated_segment_count",
    "xliff_average_source_length",
]


def _iter_segments(source: SourceType) -> Iterator[dict[str, Any]]:
    """Yield every segment dict across all files/units in the parsed document."""
    model = load_xliff(source)
    for file_data in model.get("files", []):
        for unit_data in file_data.get("units", []):
            for segment in unit_data.get("segments", []):
                yield segment


def xliff_translated_segment_count(source: SourceType) -> int:
    """Return the count of segments whose target text is non-empty.

    Spec: XLIFF <segment> elements carry an optional <target> child holding
    the translated text (FACT-XLIFF-002). A segment is counted as translated
    when its target is present and contains non-whitespace text.
    """
    return sum(1 for seg in _iter_segments(source) if str(seg.get("target", "")).strip())


def xliff_untranslated_segment_count(source: SourceType) -> int:
    """Return the count of segments whose target text is empty or missing.

    Spec: XLIFF <segment> elements carry an optional <target> child holding
    the translated text (FACT-XLIFF-002). A segment with no target, or a
    target containing only whitespace, is counted as untranslated.
    """
    return sum(1 for seg in _iter_segments(source) if not str(seg.get("target", "")).strip())


def xliff_average_source_length(source: SourceType) -> float:
    """Return the average character length of segment source text.

    Spec: XLIFF <segment> elements carry a required <source> child holding
    the source-language text (FACT-XLIFF-002). Returns 0.0 when the document
    has no segments.
    """
    lengths = [len(str(seg.get("source", ""))) for seg in _iter_segments(source)]
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)

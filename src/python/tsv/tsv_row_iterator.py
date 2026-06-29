"""
tsv_row_iterator.py — Spec-shaped row iteration for TSV documents.

Authority: IANA text/tab-separated-values media type.
Spec QName: tsv:record (urn:iana:media-type:text:tab-separated-values)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .tsv_parser import parse_tsv_strict
from .spec.record.record import Record


def tsv_iter_records(source: "str | Path") -> Iterator[Record]:
    """Yield spec-shaped Record objects for every data row in a TSV file.

    Header row (if present) is excluded; only data rows are yielded.

    Args:
        source: Path to a .tsv tab-separated values file.

    Yields:
        Record instances (spec class: tsv:record, FACT-TSV-001).

    Raises:
        TsvError subclasses on parse failure.
    """
    doc = parse_tsv_strict(str(Path(source).resolve()))
    for row in doc.get("rows", []):
        yield Record(list(row))

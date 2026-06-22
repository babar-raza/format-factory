"""TsvRecord — production facade for tsv:record.

Spec authority: tsv:record
Fact ref: FACT-TSV-001
Canonical spec class: src/python/tsv/spec/record/record.py::Record
"""
from __future__ import annotations

from ..spec.record.record import Record as _SpecRecord


class TsvRecord(_SpecRecord):
    """Production facade for tsv:record."""

    spec_qname = "tsv:record"
    spec_fact_ref = "FACT-TSV-001"
    namespace_uri = "urn:iana:media-type:text:tab-separated-values"

"""CsvRecord — production facade for csv:record.

Spec authority: csv:record
Fact ref: FACT-CSV-001
Canonical spec class: src/python/csv/spec/record/record.py::Record
"""
from __future__ import annotations

from ..spec.record.record import Record as _SpecRecord


class CsvRecord(_SpecRecord):
    """Production facade for csv:record (RFC 4180 row)."""

    spec_qname = "csv:record"
    spec_fact_ref = "FACT-CSV-001"
    namespace_uri = "urn:ietf:rfc:4180:csv"

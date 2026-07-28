"""CsvRecord — production facade for csv:record.

Spec authority: csv:record
Fact ref: SAL-CSV-00001
Canonical spec class: src/python/ff_csv/spec/record/record.py::Record
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.record.record import Record as _SpecRecord


class CsvRecord(_SpecRecord):
    """Production facade for csv:record (RFC 4180 row)."""

    spec_qname: ClassVar[str] = "csv:record"
    spec_fact_ref: ClassVar[str] = "SAL-CSV-00001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:4180:csv"

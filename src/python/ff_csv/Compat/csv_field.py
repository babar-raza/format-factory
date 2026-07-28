"""CsvField — production facade for csv:field.

Spec authority: csv:field
Fact ref: SAL-CSV-00002
Canonical spec class: src/python/ff_csv/spec/record/field.py::Field
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.record.field import Field as _SpecField


class CsvField(_SpecField):
    """Production facade for csv:field (RFC 4180 field value)."""

    spec_qname: ClassVar[str] = "csv:field"
    spec_fact_ref: ClassVar[str] = "SAL-CSV-00002"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:4180:csv"

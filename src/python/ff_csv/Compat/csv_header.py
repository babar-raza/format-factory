"""CsvHeader — production facade for csv:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.record.header import Header as _SpecHeader


class CsvHeader(_SpecHeader):
    """Production facade for csv:header."""
    spec_qname: ClassVar[str] = "csv:header"
    spec_fact_ref: ClassVar[str] = "SAL-CSV-00001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:4180:csv"

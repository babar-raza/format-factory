"""CsvHeader — production facade for csv:header."""
from __future__ import annotations
from ..spec.record.header import Header as _SpecHeader


class CsvHeader(_SpecHeader):
    """Production facade for csv:header."""
    spec_qname = "csv:header"
    spec_fact_ref = "FACT-CSV-001"
    namespace_uri = "urn:ietf:rfc:4180:csv"

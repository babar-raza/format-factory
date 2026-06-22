"""DifHeader — production facade for dif:header."""
from __future__ import annotations
from ..spec.table.header import Header as _SpecHeader


class DifHeader(_SpecHeader):
    """Production facade for dif:header."""
    spec_qname = "dif:header"
    spec_fact_ref = "FACT-DIF-001"
    namespace_uri = "urn:format:dif:1.0"

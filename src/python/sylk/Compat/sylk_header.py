"""SylkHeader — production facade for sylk:header."""
from __future__ import annotations
from ..spec.row.header import Header as _SpecHeader


class SylkHeader(_SpecHeader):
    """Production facade for sylk:header."""
    spec_qname = "sylk:header"
    spec_fact_ref = "FACT-SYLK-001"
    namespace_uri = "urn:format:sylk:1.0"

"""SylkRow — production facade for sylk:row."""
from __future__ import annotations
from ..spec.row.row import Row as _SpecRow


class SylkRow(_SpecRow):
    """Production facade for sylk:row."""
    spec_qname = "sylk:row"
    spec_fact_ref = "FACT-SYLK-002"
    namespace_uri = "urn:format:sylk:1.0"

"""SylkCell — production facade for sylk:cell."""
from __future__ import annotations
from ..spec.row.cell import Cell as _SpecCell


class SylkCell(_SpecCell):
    """Production facade for sylk:cell."""
    spec_qname = "sylk:cell"
    spec_fact_ref = "FACT-SYLK-003"
    namespace_uri = "urn:format:sylk:1.0"

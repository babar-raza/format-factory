"""DifVector — production facade for dif:vector."""
from __future__ import annotations
from ..spec.table.vector import Vector as _SpecVector


class DifVector(_SpecVector):
    """Production facade for dif:vector."""
    spec_qname = "dif:vector"
    spec_fact_ref = "FACT-DIF-002"
    namespace_uri = "urn:format:dif:1.0"

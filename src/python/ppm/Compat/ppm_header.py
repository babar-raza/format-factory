"""PpmHeader — production facade for ppm:header."""
from __future__ import annotations
from ..spec.pixmap.header import Header as _SpecHeader


class PpmHeader(_SpecHeader):
    """Production facade for ppm:header."""
    spec_qname = "ppm:header"
    spec_fact_ref = "FACT-PPM-001"
    namespace_uri = "urn:format:netpbm:ppm:1.0"

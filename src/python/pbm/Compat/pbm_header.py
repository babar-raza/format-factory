"""PbmHeader — production facade for pbm:header."""
from __future__ import annotations
from ..spec.bitmap.header import Header as _SpecHeader


class PbmHeader(_SpecHeader):
    """Production facade for pbm:header."""
    spec_qname = "pbm:header"
    spec_fact_ref = "FACT-PBM-001"
    namespace_uri = "urn:format:netpbm:pbm:1.0"

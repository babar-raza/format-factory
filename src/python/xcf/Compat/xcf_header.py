"""XcfHeader — production facade for xcf:header."""
from __future__ import annotations
from ..spec.layer.header import Header as _SpecHeader


class XcfHeader(_SpecHeader):
    """Production facade for xcf:header."""
    spec_qname = "xcf:header"
    spec_fact_ref = "FACT-XCF-001"
    namespace_uri = "urn:format:gimp:xcf:1.0"

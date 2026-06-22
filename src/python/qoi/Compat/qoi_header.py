"""QoiHeader — production facade for qoi:header."""
from __future__ import annotations
from ..spec.chunk.header import Header as _SpecHeader


class QoiHeader(_SpecHeader):
    """Production facade for qoi:header."""
    spec_qname = "qoi:header"
    spec_fact_ref = "FACT-QOI-001"
    namespace_uri = "urn:format:qoi:1.0"

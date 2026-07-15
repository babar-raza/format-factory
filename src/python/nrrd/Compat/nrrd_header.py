"""NrrdHeader — production facade for nrrd:header."""
from __future__ import annotations
from ..spec.header.header import Header as _SpecHeader


class NrrdHeader(_SpecHeader):
    """Production facade for nrrd:header."""
    spec_qname = "nrrd:header"
    spec_fact_ref = "FACT-NRRD-002"
    namespace_uri = "urn:format:nrrd:5.0"

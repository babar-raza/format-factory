"""NrrdHeader — production facade for nrrd:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.header.header import Header as _SpecHeader


class NrrdHeader(_SpecHeader):
    """Production facade for nrrd:header."""
    spec_qname: ClassVar[str] = "nrrd:header"
    spec_fact_ref: ClassVar[str] = "FACT-NRRD-002"
    namespace_uri: ClassVar[str] = "urn:format:nrrd:5.0"

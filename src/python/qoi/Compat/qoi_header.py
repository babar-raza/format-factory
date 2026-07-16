"""QoiHeader — production facade for qoi:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.chunk.header import Header as _SpecHeader


class QoiHeader(_SpecHeader):
    """Production facade for qoi:header."""
    spec_qname: ClassVar[str] = "qoi:header"
    spec_fact_ref: ClassVar[str] = "SAL-QOI-00001"
    namespace_uri: ClassVar[str] = "urn:format:qoi:1.0"

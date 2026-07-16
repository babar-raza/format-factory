"""PbmHeader — production facade for pbm:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.bitmap.header import Header as _SpecHeader


class PbmHeader(_SpecHeader):
    """Production facade for pbm:header."""
    spec_qname: ClassVar[str] = "pbm:header"
    spec_fact_ref: ClassVar[str] = "SAL-PBM-00001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pbm:1.0"

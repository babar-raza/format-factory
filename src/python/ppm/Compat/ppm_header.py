"""PpmHeader — production facade for ppm:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.pixmap.header import Header as _SpecHeader


class PpmHeader(_SpecHeader):
    """Production facade for ppm:header."""
    spec_qname: ClassVar[str] = "ppm:header"
    spec_fact_ref: ClassVar[str] = "SAL-PPM-00001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:ppm:1.0"

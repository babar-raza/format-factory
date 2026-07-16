"""XcfHeader — production facade for xcf:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.layer.header import Header as _SpecHeader


class XcfHeader(_SpecHeader):
    """Production facade for xcf:header."""
    spec_qname: ClassVar[str] = "xcf:header"
    spec_fact_ref: ClassVar[str] = "SAL-XCF-00001"
    namespace_uri: ClassVar[str] = "urn:format:gimp:xcf:1.0"

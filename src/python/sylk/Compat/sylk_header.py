"""SylkHeader — production facade for sylk:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.row.header import Header as _SpecHeader


class SylkHeader(_SpecHeader):
    """Production facade for sylk:header."""
    spec_qname: ClassVar[str] = "sylk:header"
    spec_fact_ref: ClassVar[str] = "SAL-SYLK-00001"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"

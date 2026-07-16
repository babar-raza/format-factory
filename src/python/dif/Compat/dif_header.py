"""DifHeader — production facade for dif:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.table.header import Header as _SpecHeader


class DifHeader(_SpecHeader):
    """Production facade for dif:header."""
    spec_qname: ClassVar[str] = "dif:header"
    spec_fact_ref: ClassVar[str] = "SAL-DIF-00001"
    namespace_uri: ClassVar[str] = "urn:format:dif:1.0"

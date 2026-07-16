"""SylkRow — production facade for sylk:row."""
from __future__ import annotations
from typing import ClassVar
from ..spec.row.row import Row as _SpecRow


class SylkRow(_SpecRow):
    """Production facade for sylk:row."""
    spec_qname: ClassVar[str] = "sylk:row"
    spec_fact_ref: ClassVar[str] = "SAL-SYLK-00002"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"

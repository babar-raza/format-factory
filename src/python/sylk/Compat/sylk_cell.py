"""SylkCell — production facade for sylk:cell."""
from __future__ import annotations
from typing import ClassVar
from ..spec.row.cell import Cell as _SpecCell


class SylkCell(_SpecCell):
    """Production facade for sylk:cell."""
    spec_qname: ClassVar[str] = "sylk:cell"
    spec_fact_ref: ClassVar[str] = "SAL-SYLK-00003"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"

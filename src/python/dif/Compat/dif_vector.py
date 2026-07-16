"""DifVector — production facade for dif:vector."""
from __future__ import annotations
from typing import ClassVar
from ..spec.table.vector import Vector as _SpecVector


class DifVector(_SpecVector):
    """Production facade for dif:vector."""
    spec_qname: ClassVar[str] = "dif:vector"
    spec_fact_ref: ClassVar[str] = "SAL-DIF-00002"
    namespace_uri: ClassVar[str] = "urn:format:dif:1.0"

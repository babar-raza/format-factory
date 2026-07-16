"""MtlxTypeDef — production facade for materialx:typedef."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.typedef import TypeDef as _SpecTypeDef


class MtlxTypeDef(_SpecTypeDef):
    """Production facade for materialx:typedef."""
    spec_qname: ClassVar[str] = "materialx:typedef"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

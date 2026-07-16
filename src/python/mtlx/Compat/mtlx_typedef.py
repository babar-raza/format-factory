"""MtlxTypeDef — production facade for materialx:typedef."""
from __future__ import annotations
from ..spec.element.typedef import TypeDef as _SpecTypeDef


class MtlxTypeDef(_SpecTypeDef):
    """Production facade for materialx:typedef."""
    spec_qname = "materialx:typedef"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"

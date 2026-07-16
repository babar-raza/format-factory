"""MtlxNodeDef — production facade for materialx:nodedef."""
from __future__ import annotations
from ..spec.element.nodedef import NodeDef as _SpecNodeDef


class MtlxNodeDef(_SpecNodeDef):
    """Production facade for materialx:nodedef."""
    spec_qname = "materialx:nodedef"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"

"""MtlxNodeDef — production facade for materialx:nodedef."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.nodedef import NodeDef as _SpecNodeDef


class MtlxNodeDef(_SpecNodeDef):
    """Production facade for materialx:nodedef."""
    spec_qname: ClassVar[str] = "materialx:nodedef"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

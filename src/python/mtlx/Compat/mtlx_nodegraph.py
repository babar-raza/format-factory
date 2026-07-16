"""MtlxNodeGraph — production facade for materialx:nodegraph."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.nodegraph import NodeGraph as _SpecNodeGraph


class MtlxNodeGraph(_SpecNodeGraph):
    """Production facade for materialx:nodegraph."""
    spec_qname: ClassVar[str] = "materialx:nodegraph"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-002"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

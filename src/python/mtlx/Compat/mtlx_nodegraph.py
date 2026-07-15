"""MtlxNodeGraph — production facade for materialx:nodegraph."""
from __future__ import annotations
from ..spec.element.nodegraph import NodeGraph as _SpecNodeGraph


class MtlxNodeGraph(_SpecNodeGraph):
    """Production facade for materialx:nodegraph."""
    spec_qname = "materialx:nodegraph"
    spec_fact_ref = "FACT-MTLX-002"
    namespace_uri = "urn:format:materialx:1.39"

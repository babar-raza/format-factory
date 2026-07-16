"""MtlxLook — production facade for materialx:look."""
from __future__ import annotations
from ..spec.element.look import Look as _SpecLook


class MtlxLook(_SpecLook):
    """Production facade for materialx:look."""
    spec_qname = "materialx:look"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"

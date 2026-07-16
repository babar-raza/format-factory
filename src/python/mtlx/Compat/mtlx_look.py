"""MtlxLook — production facade for materialx:look."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.look import Look as _SpecLook


class MtlxLook(_SpecLook):
    """Production facade for materialx:look."""
    spec_qname: ClassVar[str] = "materialx:look"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

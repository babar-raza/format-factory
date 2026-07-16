"""MtlxPropertySet — production facade for materialx:propertyset."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.propertyset import PropertySet as _SpecPropertySet


class MtlxPropertySet(_SpecPropertySet):
    """Production facade for materialx:propertyset."""
    spec_qname: ClassVar[str] = "materialx:propertyset"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

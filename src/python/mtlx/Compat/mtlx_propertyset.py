"""MtlxPropertySet — production facade for materialx:propertyset."""
from __future__ import annotations
from ..spec.element.propertyset import PropertySet as _SpecPropertySet


class MtlxPropertySet(_SpecPropertySet):
    """Production facade for materialx:propertyset."""
    spec_qname = "materialx:propertyset"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"

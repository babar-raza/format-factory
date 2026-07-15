"""MtlxMaterial — production facade for materialx:material."""
from __future__ import annotations
from ..spec.element.material import Material as _SpecMaterial


class MtlxMaterial(_SpecMaterial):
    """Production facade for materialx:material."""
    spec_qname = "materialx:material"
    spec_fact_ref = "FACT-MTLX-003"
    namespace_uri = "urn:format:materialx:1.39"

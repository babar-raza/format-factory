"""MtlxMaterial — production facade for materialx:material."""
from __future__ import annotations
from typing import ClassVar
from ..spec.element.material import Material as _SpecMaterial


class MtlxMaterial(_SpecMaterial):
    """Production facade for materialx:material."""
    spec_qname: ClassVar[str] = "materialx:material"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-003"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"

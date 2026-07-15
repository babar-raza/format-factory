"""ZstBlock — production facade for zst:block."""
from __future__ import annotations
from typing import ClassVar
from ..spec.frame.block import Block as _SpecBlock


class ZstBlock(_SpecBlock):
    """Production facade for zst:block."""
    spec_qname: ClassVar[str] = "zst:block"
    spec_fact_ref: ClassVar[str] = "FACT-ZST-002"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstd"

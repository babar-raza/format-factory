"""ZstBlock — production facade for zst:block."""
from __future__ import annotations
from ..spec.frame.block import Block as _SpecBlock


class ZstBlock(_SpecBlock):
    """Production facade for zst:block."""
    spec_qname = "zst:block"
    spec_fact_ref = "FACT-ZST-002"
    namespace_uri = "urn:ietf:rfc:8878:zstd"

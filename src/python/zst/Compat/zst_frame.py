"""ZstFrame — production facade for zst:frame."""
from __future__ import annotations
from ..spec.frame.frame import Frame as _SpecFrame


class ZstFrame(_SpecFrame):
    """Production facade for zst:frame."""
    spec_qname = "zst:frame"
    spec_fact_ref = "FACT-ZST-001"
    namespace_uri = "urn:ietf:rfc:8878:zstd"

"""ZstFrame — production facade for zst:frame."""
from __future__ import annotations
from typing import ClassVar
from ..spec.frame.frame import Frame as _SpecFrame


class ZstFrame(_SpecFrame):
    """Production facade for zst:frame."""
    spec_qname: ClassVar[str] = "zst:frame"
    spec_fact_ref: ClassVar[str] = "SAL-ZST-00001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstd"

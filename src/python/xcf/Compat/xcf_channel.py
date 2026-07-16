"""XcfChannel — production facade for xcf:channel."""
from __future__ import annotations
from typing import ClassVar
from ..spec.layer.channel import Channel as _SpecChannel


class XcfChannel(_SpecChannel):
    """Production facade for xcf:channel."""
    spec_qname: ClassVar[str] = "xcf:channel"
    spec_fact_ref: ClassVar[str] = "SAL-XCF-00003"
    namespace_uri: ClassVar[str] = "urn:format:gimp:xcf:1.0"

"""XcfChannel — production facade for xcf:channel."""
from __future__ import annotations
from ..spec.layer.channel import Channel as _SpecChannel


class XcfChannel(_SpecChannel):
    """Production facade for xcf:channel."""
    spec_qname = "xcf:channel"
    spec_fact_ref = "FACT-XCF-003"
    namespace_uri = "urn:format:gimp:xcf:1.0"

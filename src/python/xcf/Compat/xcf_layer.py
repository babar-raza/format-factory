"""XcfLayer — production facade for xcf:layer."""
from __future__ import annotations
from ..spec.layer.layer import Layer as _SpecLayer


class XcfLayer(_SpecLayer):
    """Production facade for xcf:layer."""
    spec_qname = "xcf:layer"
    spec_fact_ref = "FACT-XCF-002"
    namespace_uri = "urn:format:gimp:xcf:1.0"

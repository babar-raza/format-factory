"""XcfLayer — production facade for xcf:layer."""
from __future__ import annotations
from typing import ClassVar
from ..spec.layer.layer import Layer as _SpecLayer


class XcfLayer(_SpecLayer):
    """Production facade for xcf:layer."""
    spec_qname: ClassVar[str] = "xcf:layer"
    spec_fact_ref: ClassVar[str] = "SAL-XCF-00002"
    namespace_uri: ClassVar[str] = "urn:format:gimp:xcf:1.0"

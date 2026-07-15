"""SafetensorsHeader — production facade for safetensors:header."""
from __future__ import annotations
from ..spec.header.header import Header as _SpecHeader


class SafetensorsHeader(_SpecHeader):
    """Production facade for safetensors:header."""
    spec_qname = "safetensors:header"
    spec_fact_ref = "FACT-SAFETENSORS-001"
    namespace_uri = "urn:format:safetensors:0.4"

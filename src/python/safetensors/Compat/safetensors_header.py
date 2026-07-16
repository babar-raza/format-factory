"""SafetensorsHeader — production facade for safetensors:header."""
from __future__ import annotations
from typing import ClassVar
from ..spec.header.header import Header as _SpecHeader


class SafetensorsHeader(_SpecHeader):
    """Production facade for safetensors:header."""
    spec_qname: ClassVar[str] = "safetensors:header"
    spec_fact_ref: ClassVar[str] = "FACT-SAFETENSORS-001"
    namespace_uri: ClassVar[str] = "urn:format:safetensors:0.4"

"""SafetensorsTensor — production facade for safetensors:tensor."""
from __future__ import annotations
from typing import ClassVar
from ..spec.header.tensor import Tensor as _SpecTensor


class SafetensorsTensor(_SpecTensor):
    """Production facade for safetensors:tensor."""
    spec_qname: ClassVar[str] = "safetensors:tensor"
    spec_fact_ref: ClassVar[str] = "FACT-SAFETENSORS-002"
    namespace_uri: ClassVar[str] = "urn:format:safetensors:0.4"

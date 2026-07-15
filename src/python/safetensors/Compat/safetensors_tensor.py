"""SafetensorsTensor — production facade for safetensors:tensor."""
from __future__ import annotations
from ..spec.header.tensor import Tensor as _SpecTensor


class SafetensorsTensor(_SpecTensor):
    """Production facade for safetensors:tensor."""
    spec_qname = "safetensors:tensor"
    spec_fact_ref = "FACT-SAFETENSORS-002"
    namespace_uri = "urn:format:safetensors:0.4"

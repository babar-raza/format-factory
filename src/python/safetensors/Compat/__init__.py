"""safetensors.Compat — production facade layer for SafeTensors.

Exports:
    SafetensorsHeader — facade for safetensors:header (FACT-SAFETENSORS-001)
    SafetensorsTensor — facade for safetensors:tensor (FACT-SAFETENSORS-002)
"""
from .safetensors_header import SafetensorsHeader
from .safetensors_tensor import SafetensorsTensor

__all__ = ["SafetensorsHeader", "SafetensorsTensor"]

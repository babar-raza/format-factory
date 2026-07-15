"""safetensors.spec — canonical spec authority classes for SafeTensors."""
from .header.header import Header
from .header.tensor import Tensor

__all__ = ["Header", "Tensor"]

"""Optional framework adapters."""

from .numpy import to_numpy
from .torch import to_torch

__all__ = ["to_numpy", "to_torch"]

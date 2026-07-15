"""nrrd.spec — canonical spec authority classes for NRRD."""
from .header.header import Header
from .header.data import Data

__all__ = ["Header", "Data"]

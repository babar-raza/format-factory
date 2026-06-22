"""dif.spec — canonical spec authority classes for DIF."""
from .table.header import Header
from .table.vector import Vector
from .table.datum import Datum

__all__ = ["Header", "Vector", "Datum"]

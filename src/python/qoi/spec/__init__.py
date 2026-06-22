"""qoi.spec — canonical spec authority classes for QOI."""
from .chunk.header import Header
from .chunk.chunk import Chunk

__all__ = ["Header", "Chunk"]

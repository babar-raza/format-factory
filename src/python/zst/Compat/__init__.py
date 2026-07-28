"""zst.Compat — production facade layer for ZST.

Exports:
    ZstFrame — facade for zst:frame (SAL-ZST-00001)
    ZstBlock — facade for zst:block (SAL-ZST-00002)
"""
from .zst_frame import ZstFrame
from .zst_block import ZstBlock

__all__ = ["ZstFrame", "ZstBlock"]

"""ppm.Compat — production facade layer for PPM.

Exports:
    PpmHeader — facade for ppm:header (FACT-PPM-001)
    PpmPixmap — facade for ppm:pixmap (FACT-PPM-002)
"""
from .ppm_header import PpmHeader
from .ppm_pixmap import PpmPixmap

__all__ = ["PpmHeader", "PpmPixmap"]

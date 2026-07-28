"""ppm.Compat — production facade layer for PPM.

Exports:
    PpmHeader — facade for ppm:header (SAL-PPM-00001)
    PpmPixmap — facade for ppm:pixmap (SAL-PPM-00002)
"""
from .ppm_header import PpmHeader
from .ppm_pixmap import PpmPixmap

__all__ = ["PpmHeader", "PpmPixmap"]

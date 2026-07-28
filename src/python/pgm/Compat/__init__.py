"""pgm.Compat — production facade layer for PGM.

Exports:
    PgmHeader  — facade for pgm:header  (SAL-PGM-00001)
    PgmGraymap — facade for pgm:graymap (SAL-PGM-00002)
"""
from .pgm_header import PgmHeader
from .pgm_graymap import PgmGraymap

__all__ = ["PgmHeader", "PgmGraymap"]

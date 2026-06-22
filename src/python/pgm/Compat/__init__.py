"""pgm.Compat — production facade layer for PGM.

Exports:
    PgmHeader  — facade for pgm:header  (FACT-PGM-001)
    PgmGraymap — facade for pgm:graymap (FACT-PGM-002)
"""
from .pgm_header import PgmHeader
from .pgm_graymap import PgmGraymap

__all__ = ["PgmHeader", "PgmGraymap"]

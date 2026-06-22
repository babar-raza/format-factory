"""tsv.Compat — production facade layer for TSV.

Exports:
    TsvRecord — facade for tsv:record (FACT-TSV-001)
    TsvField  — facade for tsv:field  (FACT-TSV-002)
"""
from .tsv_record import TsvRecord
from .tsv_field import TsvField

__all__ = ["TsvRecord", "TsvField"]

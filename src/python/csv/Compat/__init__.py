"""csv.Compat — production facade layer for CSV.

Exports:
    CsvRecord — facade for csv:record (FACT-CSV-001)
    CsvField  — facade for csv:field  (FACT-CSV-002)
"""
from .csv_record import CsvRecord
from .csv_field import CsvField

__all__ = ["CsvRecord", "CsvField"]

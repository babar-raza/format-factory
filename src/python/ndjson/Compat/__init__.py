"""ndjson.Compat — production facade layer for NDJSON.

Exports:
    NdjsonRecord — facade for ndjson:record (FACT-NDJSON-001)
    NdjsonField  — facade for ndjson:field  (FACT-NDJSON-002)
"""
from .ndjson_record import NdjsonRecord
from .ndjson_field import NdjsonField

__all__ = ["NdjsonRecord", "NdjsonField"]

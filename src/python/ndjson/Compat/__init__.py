"""ndjson.Compat — production facade layer for NDJSON.

Exports:
    NdjsonRecord — facade for ndjson:record (SAL-NDJSON-00001)
    NdjsonField  — facade for ndjson:field  (SAL-NDJSON-00002)
"""
from .ndjson_record import NdjsonRecord
from .ndjson_field import NdjsonField

__all__ = ["NdjsonRecord", "NdjsonField"]

"""
NDJSON field analytics — field-level analytics for NDJSON record streams.

Extends ndjson_record_stats.py with additional field-level analytics.
Uses load_ndjson from ndjson_codec.
"""
from __future__ import annotations

from pathlib import Path

from .ndjson_codec import load_ndjson

spec_qname = "ndjson:record"
spec_fact_ref = "FACT-NDJSON-001"


def ndjson_first_record_keys(source: "str | bytes | Path") -> list:
    """Return list of keys from the first dict record. Empty list if no records.

    Spec: NDJSON record field names (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    for rec in records:
        if isinstance(rec, dict):
            return list(rec.keys())
    return []


def ndjson_first_record_field_count(source: "str | bytes | Path") -> int:
    """Return the field count of the first dict record. 0 if no records.

    Spec: NDJSON record field count (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    for rec in records:
        if isinstance(rec, dict):
            return len(rec)
    return 0


def ndjson_has_consistent_keys(source: "str | bytes | Path") -> bool:
    """Return True if all dict records have identical sets of keys.

    True vacuously when there are no dict records.

    Spec: NDJSON record schema consistency (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    dict_records = [r for r in records if isinstance(r, dict)]
    if not dict_records:
        return True
    first_keys = frozenset(dict_records[0].keys())
    return all(frozenset(r.keys()) == first_keys for r in dict_records)


def ndjson_bool_value_count(source: "str | bytes | Path") -> int:
    """Return count of True boolean values across all fields in all records.

    Spec: NDJSON record boolean values (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    count = 0
    for rec in records:
        if isinstance(rec, dict):
            for v in rec.values():
                if v is True:
                    count += 1
    return count


def ndjson_null_field_count(source: "str | bytes | Path") -> int:
    """Return count of None (null) values across all fields in all records.

    Spec: NDJSON record null values (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    count = 0
    for rec in records:
        if isinstance(rec, dict):
            for v in rec.values():
                if v is None:
                    count += 1
    return count


def ndjson_sorted_key_names(source: "str | bytes | Path") -> list:
    """Return sorted list of all unique key names across all dict records.

    Spec: NDJSON record field names (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    keys: set = set()
    for rec in records:
        if isinstance(rec, dict):
            keys.update(rec.keys())
    return sorted(keys)

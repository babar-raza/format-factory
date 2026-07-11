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


def ndjson_all_key_names(source: "str | bytes | Path") -> list:
    """Return list of all unique key names across all dict records (insertion order).

    Spec: NDJSON record field names (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    seen: dict = {}
    for rec in records:
        if isinstance(rec, dict):
            for k in rec.keys():
                seen[k] = None
    return list(seen.keys())


def ndjson_last_record_keys(source: "str | bytes | Path") -> list:
    """Return list of keys from the last dict record. Empty list if no dict records.

    Spec: NDJSON record field names (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    last = None
    for rec in records:
        if isinstance(rec, dict):
            last = rec
    return list(last.keys()) if last is not None else []


def ndjson_numeric_field_count(source: "str | bytes | Path") -> int:
    """Return count of numeric (int or float) values across all fields in all records.

    Spec: NDJSON record numeric values (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    count = 0
    for rec in records:
        if isinstance(rec, dict):
            for v in rec.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    count += 1
    return count


def ndjson_string_field_count(source: "str | bytes | Path") -> int:
    """Return count of string values across all fields in all records.

    Spec: NDJSON record string values (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    count = 0
    for rec in records:
        if isinstance(rec, dict):
            for v in rec.values():
                if isinstance(v, str):
                    count += 1
    return count


def ndjson_has_nested_records(source: "str | bytes | Path") -> bool:
    """Return True if any field value is itself a dict (nested object).

    Spec: NDJSON record nested values (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    for rec in records:
        if isinstance(rec, dict):
            for v in rec.values():
                if isinstance(v, dict):
                    return True
    return False


def ndjson_max_field_count(source: "str | bytes | Path") -> int:
    """Return maximum field count across all dict records. 0 if no dict records.

    Spec: NDJSON record field count (FACT-NDJSON-001)
    """
    records = load_ndjson(source)
    counts = [len(r) for r in records if isinstance(r, dict)]
    return max(counts) if counts else 0


def ndjson_record_count(source: "str | bytes | Path") -> int:
    """Return total count of records (lines) in the NDJSON stream.

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        int — total record count.
    """
    return len(load_ndjson(source))


def ndjson_dict_record_count(source: "str | bytes | Path") -> int:
    """Return count of records that are JSON objects (dicts).

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        int — dict record count.
    """
    return sum(1 for r in load_ndjson(source) if isinstance(r, dict))


def ndjson_unique_key_count(source: "str | bytes | Path") -> int:
    """Return count of distinct field names across all dict records.

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        int — number of unique keys.
    """
    records = load_ndjson(source)
    keys: set = set()
    for rec in records:
        if isinstance(rec, dict):
            keys.update(rec.keys())
    return len(keys)


def ndjson_min_field_count(source: "str | bytes | Path") -> int:
    """Return minimum field count across all dict records. 0 if no dict records.

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        int — minimum field count.
    """
    records = load_ndjson(source)
    counts = [len(r) for r in records if isinstance(r, dict)]
    return min(counts) if counts else 0


def ndjson_has_arrays(source: "str | bytes | Path") -> bool:
    """Return True if any field value across all dict records is a list.

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        bool — True if any value is a list.
    """
    for rec in load_ndjson(source):
        if isinstance(rec, dict):
            for v in rec.values():
                if isinstance(v, list):
                    return True
    return False


def ndjson_total_field_count(source: "str | bytes | Path") -> int:
    """Return total field count across all dict records.

    Sums the number of keys in each dict record.

    Args:
        source: Path to an .ndjson file, or raw NDJSON bytes.

    Returns:
        int — total fields. 0 if no dict records.
    """
    return sum(len(r) for r in load_ndjson(source) if isinstance(r, dict))

"""NDJSON record statistics and aggregation functions.

Derived analytics, aggregation, and manipulation operations on
NDJSON record lists. These functions operate on already-parsed records.

spec_concept: Newline-delimited JSON record stream statistics
"""
from __future__ import annotations

from typing import Any

from .ndjson_codec import load_ndjson



def group_by(source, key: str) -> dict[Any, list[Any]]:
    """Group NDJSON records by the value of a field.

    Only dict records are eligible; non-dict records are collected
    under the special key ``None``.  Records where the key is missing
    are also grouped under ``None``.

    Args:
        source: Path, bytes, or string of NDJSON content.
        key:    Field name to group by.

    Returns:
        Dict mapping field values to lists of matching records.
        Order within each group preserves input order.

    Raises:
        NdjsonParseError: If any non-empty line is not valid JSON.
        NdjsonError: For size/read errors.
    """
    records = load_ndjson(source)
    groups: dict[Any, list[Any]] = {}
    for record in records:
        if isinstance(record, dict) and key in record:
            group_key = record[key]
        else:
            group_key = None
        groups.setdefault(group_key, []).append(record)
    return groups




def deduplicate(source, key: str) -> list[Any]:
    """Remove duplicate NDJSON records by a field key; keep first occurrence.

    Non-dict records or records missing the key are always kept (treated
    as unique).

    Args:
        source: Path to a file, bytes, string, or list of records.
        key:    Field name to use for deduplication.

    Returns:
        List of records with duplicates removed.

    Raises:
        NdjsonParseError: If source cannot be parsed.
        NdjsonError:      For other load errors.
    """
    records = load_ndjson(source)
    seen: set = set()
    result: list[Any] = []
    for record in records:
        if isinstance(record, dict) and key in record:
            val = record[key]
            try:
                hashable = val if not isinstance(val, (list, dict)) else str(val)
                if hashable in seen:
                    continue
                seen.add(hashable)
            except TypeError:
                pass
        result.append(record)
    return result




def min_value(source, field: str) -> Any:
    """Return the minimum value for a field across all NDJSON records.

    Records missing the field are skipped. Returns None if no values found.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to find the min of.

    Returns:
        Minimum field value, or None if field has no values.
    """
    records = load_ndjson(source)
    values = [rec[field] for rec in records if isinstance(rec, dict) and field in rec]
    return min(values) if values else None




def zip_records(list1: list, list2: list) -> list[Any]:
    """Zip two record lists by position into merged dicts.

    Stops at the shorter list. For each pair, merges the two dicts.
    list2 values overwrite list1 values on key collision.

    Args:
        list1: First list of dicts.
        list2: Second list of dicts.

    Returns:
        List of merged dicts.
    """
    result = []
    for a, b in zip(list1, list2):
        if isinstance(a, dict) and isinstance(b, dict):
            result.append({**a, **b})
        else:
            result.append(b)
    return result




def count_by(source, field: str) -> dict:
    """Count occurrences of each unique value for a field.

    Records missing the field are skipped.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to count by.

    Returns:
        Dict mapping each unique value to its occurrence count.
    """
    records = load_ndjson(source)
    result: dict = {}
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            val = rec[field]
            try:
                key = val
                result[key] = result.get(key, 0) + 1
            except TypeError:
                key = str(val)
                result[key] = result.get(key, 0) + 1
    return result




def max_value(source, field: str) -> Any:
    """Return the maximum value for a field across all NDJSON records.

    Records missing the field are skipped. Returns None if no values found.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to find the max of.

    Returns:
        Maximum field value, or None if field has no values.
    """
    records = load_ndjson(source)
    values = [rec[field] for rec in records if isinstance(rec, dict) and field in rec]
    return max(values) if values else None




def pick(source, fields: list[str]) -> list[Any]:
    """Project only specified fields from each NDJSON record.

    Fields not present in a record are omitted from that record's output dict.

    Args:
        source: NDJSON source (bytes, str, or Path).
        fields: List of field names to keep.

    Returns:
        List of dicts containing only the requested fields.
    """
    records = load_ndjson(source)
    result = []
    for rec in records:
        if isinstance(rec, dict):
            result.append({k: v for k, v in rec.items() if k in fields})
        else:
            result.append(rec)
    return result




def distinct_values(source, field: str) -> list[Any]:
    """Return a list of unique values for a field across all NDJSON records.

    Records that don't contain the field are skipped. Order is preserved
    (first occurrence wins).

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to extract distinct values from.

    Returns:
        List of unique field values in order of first appearance.
    """
    records = load_ndjson(source)
    seen: list[Any] = []
    seen_set: set = set()
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            val = rec[field]
            try:
                hashable = val
                hash(hashable)
                if hashable not in seen_set:
                    seen_set.add(hashable)
                    seen.append(val)
            except TypeError:
                # unhashable (e.g. list/dict) — use linear scan
                if val not in seen:
                    seen.append(val)
    return seen




def sort_by(source, field: str, reverse: bool = False) -> list[Any]:
    """Sort NDJSON records by a field value; return sorted list.

    Records that are not dicts or lack the field are placed at the end.

    Args:
        source:  Path to a file, bytes, or string of NDJSON content.
        field:   Key name to sort by.
        reverse: If True, sort in descending order.

    Returns:
        List of records sorted by field value.
    """
    records = load_ndjson(source)
    _MISSING = object()

    def _key(r: Any) -> tuple:
        if isinstance(r, dict) and field in r:
            val = r[field]
            try:
                return (0, val)
            except TypeError:
                return (0, str(val))
        return (1, None)

    return sorted(records, key=_key, reverse=reverse)




def aggregate(source, field: str, func: str) -> Any:
    """Aggregate NDJSON field values: sum, count, min, or max.

    Records that lack the field or have non-numeric values are skipped
    for sum/min/max. count includes all records.

    Args:
        source: Path to a file, bytes, or string of NDJSON content.
        field:  Key name to aggregate.
        func:   One of "sum", "count", "min", "max".

    Returns:
        Aggregated value (int, float, or None if no applicable records).

    Raises:
        ValueError: If func is not one of the allowed values.
    """
    allowed = {"sum", "count", "min", "max"}
    if func not in allowed:
        raise ValueError(f"func must be one of {sorted(allowed)}, got '{func}'")
    records = load_ndjson(source)
    if func == "count":
        return len(records)
    values = [r[field] for r in records if isinstance(r, dict) and field in r
              and isinstance(r[field], (int, float))]
    if not values:
        return None
    if func == "sum":
        return sum(values)
    if func == "min":
        return min(values)
    return max(values)




def tail(source, n: int) -> list[Any]:
    """Return the last N records from an NDJSON source.

    Args:
        source: Path to a file, bytes, or string of NDJSON content.
        n:      Number of records to return from the end.

    Returns:
        List of the last n records (fewer if source has < n records).

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    records = load_ndjson(source)
    return records[-n:] if n > 0 else []




def pluck(source, field: str) -> list[Any]:
    """Extract single field values from NDJSON records as a flat list.

    Records that are not dicts or do not contain the field are skipped.

    Args:
        source: Path to a file, bytes, or string of NDJSON content.
        field:  Key name to extract from each record dict.

    Returns:
        Flat list of values for the given field across all records.
    """
    records = load_ndjson(source)
    return [r[field] for r in records if isinstance(r, dict) and field in r]




def head(source, n: int = 10) -> list:
    """Return the first N records from an NDJSON source.

    Args:
        source: NDJSON source (bytes, str, or Path).
        n: Number of records to return (default 10).

    Returns:
        List of first N records; fewer if source has fewer than N.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    return load_ndjson(source)[:n]




def sum_field(source, field: str) -> float:
    """Sum numeric values for a field across all NDJSON records.

    Records without the field or with non-numeric values are skipped.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to sum.

    Returns:
        Sum as float, or 0.0 if no numeric values found.
    """
    records = load_ndjson(source)
    total = 0.0
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            try:
                total += float(rec[field])
            except (TypeError, ValueError):
                pass
    return total




def average_value(source, field: str) -> float:
    """Return the average of numeric values for a field across all NDJSON records.

    Records without the field, or with non-numeric values, are skipped.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field: Field name to average.

    Returns:
        Average as float, or 0.0 if no numeric values found.
    """
    records = load_ndjson(source)
    total = 0.0
    count = 0
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            try:
                total += float(rec[field])
                count += 1
            except (TypeError, ValueError):
                pass
    return total / count if count > 0 else 0.0




def field_stats(source, field: str) -> dict:
    """Return basic statistics about a numeric field across all NDJSON records.

    Args:
        source: NDJSON source (bytes, str, or Path).
        field:  Field name to analyse.

    Returns:
        Dict with: count, missing, min, max, sum, mean.
        Numeric fields only; non-numeric values count as missing.
    """
    records = load_ndjson(source)
    values: list[float] = []
    missing = 0
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            try:
                values.append(float(rec[field]))
            except (TypeError, ValueError):
                missing += 1
        else:
            missing += 1
    if not values:
        return {"count": 0, "missing": missing, "min": None, "max": None, "sum": None, "mean": None}
    return {
        "count": len(values),
        "missing": missing,
        "min": min(values),
        "max": max(values),
        "sum": sum(values),
        "mean": sum(values) / len(values),
    }




# FORMAT_FACTORY_EXECUTION: taskcard=SHQ-L2-001; method=QUEUE_DISPATCHED_EXECUTION; queue_item=shq-q-002; sprint_id=FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
def flatten_records(source: "Any", prefix: str = "") -> "list[dict]":
    """Flatten nested dict records one level deep.

    For each record, if a field value is a dict, its keys are expanded as
    '<outer_key>_<inner_key>' (with optional prefix prepended to outer keys).
    Non-dict values are kept as-is. Non-dict records are passed through unchanged.

    Args:
        source: NDJSON source (file path, bytes, list of records).
        prefix: Optional string to prepend to all top-level field names.

    Returns:
        List of flattened records (dicts). Non-dict records are passed through.

    Example:
        flatten_records([{"a": {"x": 1, "y": 2}, "b": 3}])
        → [{"a_x": 1, "a_y": 2, "b": 3}]
    """
    if isinstance(source, list):
        records = source
    else:
        records = load_ndjson(source)

    result = []
    for record in records:
        if not isinstance(record, dict):
            result.append(record)
            continue
        flat: dict = {}
        for key, val in record.items():
            outer = f"{prefix}{key}" if prefix else key
            if isinstance(val, dict):
                for sub_key, sub_val in val.items():
                    flat[f"{outer}_{sub_key}"] = sub_val
            else:
                flat[outer] = val
        result.append(flat)
    return result




def count_unique_values(source: "Any", field: str) -> int:
    """Count the number of unique values for a field across all records.

    Records missing the field are excluded from counting.

    Args:
        source: NDJSON bytes, path, or list of records.
        field: Field name to count unique values for.

    Returns:
        Count of distinct values for the field.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    seen: set = set()
    for rec in records:
        if isinstance(rec, dict) and field in rec:
            try:
                seen.add(rec[field])
            except TypeError:
                seen.add(str(rec[field]))
    return len(seen)




def zip_with_index(source: "Any", field_name: str = "_index") -> "list[dict]":
    """Add a sequential index field to each record.

    Args:
        source: NDJSON bytes, path, or list of records.
        field_name: Name of the index field to add (default '_index').

    Returns:
        List of records each with field_name set to 0-based index.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    result = []
    for i, rec in enumerate(records):
        if isinstance(rec, dict):
            out = dict(rec)
            out[field_name] = i
        else:
            out = {field_name: i, "_value": rec}
        result.append(out)
    return result




def omit(source: "Any", fields: list[str]) -> "list[dict]":
    """Return records with specified fields removed.

    Args:
        source: NDJSON bytes, path, or list of records.
        fields: Field names to omit from each record.

    Returns:
        List of dict records with the given fields removed.
        Non-dict records are returned unchanged.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    field_set = set(fields)
    result = []
    for rec in records:
        if isinstance(rec, dict):
            result.append({k: v for k, v in rec.items() if k not in field_set})
        else:
            result.append(rec)
    return result




def batch_update(source: "Any", field: str, value: "Any") -> "list[Any]":
    """Set a field to a given value in every dict record.

    Non-dict records are passed through unchanged.

    Args:
        source: NDJSON bytes, path, string, or list of records.
        field:  Field name to set.
        value:  Value to assign to the field.

    Returns:
        New list of records with the field updated in every dict.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    result = []
    for rec in records:
        if isinstance(rec, dict):
            out = dict(rec)
            out[field] = value
            result.append(out)
        else:
            result.append(rec)
    return result


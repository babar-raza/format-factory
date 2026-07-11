"""
TOML table analytics — recursive document traversal statistics.

Extends toml_analytics.py with analytics that traverse nested tables.
No spec_qname claim — analytics modules do not represent TOML element types.
"""
from __future__ import annotations

from pathlib import Path

from .toml_codec import (
    load_toml,
)

spec_qname = "toml:document"
spec_fact_ref = "FACT-TOML-001"
namespace_uri = "urn:toml:v1.0.0"


def _iter_values(obj: object):
    """Yield all leaf and container values recursively."""
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_values(v)
            yield v
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_values(item)
            yield item


def _count_keys(obj: object) -> int:
    """Count all keys at all nesting levels."""
    if not isinstance(obj, dict):
        return 0
    total = len(obj)
    for v in obj.values():
        total += _count_keys(v)
    return total


def toml_recursive_key_count(source: "str | bytes | Path") -> int:
    """Return total count of all keys at all nesting levels in the document."""
    doc = load_toml(source)
    return _count_keys(doc.get("data", {}))


def toml_recursive_numeric_sum(source: "str | bytes | Path") -> float:
    """Return sum of all integer and float values at all nesting levels."""
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(
        float(v) for v in _iter_values(data) if isinstance(v, (int, float)) and not isinstance(v, bool)
    )


def toml_recursive_string_count(source: "str | bytes | Path") -> int:
    """Return count of all string values at all nesting levels."""
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(1 for v in _iter_values(data) if isinstance(v, str))


def toml_nested_boolean_count(source: "str | bytes | Path") -> int:
    """Return count of all boolean values at all nesting levels."""
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(1 for v in _iter_values(data) if isinstance(v, bool))


def toml_leaf_value_count(source: "str | bytes | Path") -> int:
    """Return count of non-dict, non-list values at all nesting levels."""
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(1 for v in _iter_values(data) if not isinstance(v, (dict, list)))


def toml_has_array_of_tables(source: "str | bytes | Path") -> bool:
    """Return True if any list value contains at least one dict (array of tables)."""
    doc = load_toml(source)
    data = doc.get("data", {})
    for v in _iter_values(data):
        if isinstance(v, list) and any(isinstance(item, dict) for item in v):
            return True
    return False


def toml_max_numeric_value_recursive(source: "str | bytes | Path") -> float:
    """Return maximum numeric value (int or float) across all nesting levels. 0.0 if none."""
    doc = load_toml(source)
    data = doc.get("data", {})
    nums = [float(v) for v in _iter_values(data) if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return max(nums, default=0.0)


def toml_min_numeric_value_recursive(source: "str | bytes | Path") -> float:
    """Return minimum numeric value (int or float) across all nesting levels. 0.0 if none."""
    doc = load_toml(source)
    data = doc.get("data", {})
    nums = [float(v) for v in _iter_values(data) if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return min(nums, default=0.0)

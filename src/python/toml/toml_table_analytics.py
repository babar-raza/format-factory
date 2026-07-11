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


def toml_top_level_key_count(source: "str | bytes | Path") -> int:
    """Return the count of keys at the top (root) level of the TOML document.

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        int — number of top-level keys. 0 if the document is empty.
    """
    doc = load_toml(source)
    return len(doc.get("data", {}).keys())


def toml_has_nested_tables(source: "str | bytes | Path") -> bool:
    """Return True if any top-level value in the TOML document is a table (dict).

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        bool — True if at least one top-level value is a dict.
    """
    doc = load_toml(source)
    data = doc.get("data", {})
    return any(isinstance(v, dict) for v in data.values())


def toml_recursive_list_count(source: "str | bytes | Path") -> int:
    """Return the total count of list (array) values at all nesting levels.

    Counts every list encountered during a full recursive traversal of the
    document, including lists nested inside tables and other lists.

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        int — total list count. 0 if no arrays exist.
    """
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(1 for v in _iter_values(data) if isinstance(v, list))


def toml_is_deep(source: "str | bytes | Path") -> bool:
    """Return True if the document nesting depth is 3 or greater.

    Uses the same depth calculation as toml_depth: recursive maximum nesting
    level of dict values. A depth of 3 means at least triple-nested tables.

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        bool — True if depth >= 3.
    """
    def _depth(obj: object) -> int:
        if isinstance(obj, dict) and obj:
            return 1 + max((_depth(v) for v in obj.values()), default=0)
        return 0

    doc = load_toml(source)
    return _depth(doc.get("data", {})) >= 3


def toml_avg_string_length(source: "str | bytes | Path") -> float:
    """Return the average length of all string values at all nesting levels.

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        float — mean string value length. 0.0 if no string values exist.
    """
    doc = load_toml(source)
    data = doc.get("data", {})
    lengths = [len(v) for v in _iter_values(data) if isinstance(v, str)]
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def toml_top_level_table_count(source: "str | bytes | Path") -> int:
    """Return count of top-level dict values (inline or section tables).

    Args:
        source: Path to the .toml file, or raw TOML bytes/str.

    Returns:
        int — number of top-level keys whose value is a dict. 0 if none.
    """
    doc = load_toml(source)
    data = doc.get("data", {})
    return sum(1 for v in data.values() if isinstance(v, dict))


def toml_top_level_keys(source: "str | bytes | Path") -> list:
    """Return list of top-level key names from the TOML document.

    Returns keys in their original order.
    """
    doc = load_toml(source)
    return list(doc.get("data", {}).keys())


def toml_has_boolean_values(source: "str | bytes | Path") -> bool:
    """Return True if any top-level value is a boolean."""
    doc = load_toml(source)
    return any(isinstance(v, bool) for v in doc.get("data", {}).values())


def toml_top_level_string_count(source: "str | bytes | Path") -> int:
    """Return count of top-level string values in the document."""
    doc = load_toml(source)
    return sum(1 for v in doc.get("data", {}).values() if isinstance(v, str))


def toml_top_level_int_count(source: "str | bytes | Path") -> int:
    """Return count of top-level integer values (not float, not bool)."""
    doc = load_toml(source)
    return sum(
        1 for v in doc.get("data", {}).values()
        if isinstance(v, int) and not isinstance(v, bool)
    )


def toml_top_level_keys_sorted(source: "str | bytes | Path") -> list:
    """Return alphabetically sorted list of top-level key names."""
    doc = load_toml(source)
    return sorted(doc.get("data", {}).keys())


def toml_top_level_scalar_count(source: "str | bytes | Path") -> int:
    """Return count of top-level scalar values (str, int, float, bool).

    Excludes dicts and lists.
    """
    doc = load_toml(source)
    return sum(
        1 for v in doc.get("data", {}).values()
        if isinstance(v, (str, int, float, bool)) and not isinstance(v, dict)
    )

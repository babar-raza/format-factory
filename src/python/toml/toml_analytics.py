"""
TOML analytics functions extracted from toml_codec.py (TC-HEAL-FORMATS-BATCH2).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .toml_codec import (
    load_toml,
)


def toml_string_value_count(source: "str | bytes | Path") -> int:
    """Count the number of top-level values that are strings.

    Counts only the top-level key-value pairs where the value is a str.
    Nested values inside sections are not included.

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level string values.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, str))


def toml_list_count(source: "str | bytes | Path") -> int:
    """Count the number of top-level values that are lists (TOML arrays).

    Counts only the top-level key-value pairs where the value is a list.
    Nested values inside sections are not included.

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level list/array values.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, list))


def toml_numeric_value_count(source: "str | bytes | Path") -> int:
    """Count top-level values that are numeric (int or float, not bool).

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level numeric values.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, (int, float)) and not isinstance(v, bool))


def toml_boolean_value_count(source: "str | bytes | Path") -> int:
    """Count top-level values that are booleans.

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level boolean values.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, bool))


def toml_table_count(source: "str | bytes | Path") -> int:
    """Count top-level values that are tables (dicts).

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level table values.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, dict))


def toml_total_keys(source: "str | bytes | Path") -> int:
    """Count total top-level keys.

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        Integer count of top-level keys.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return len(data)


def toml_has_tables(source: "str | bytes | Path") -> bool:
    """Return True if the TOML document contains at least one table (dict value)."""
    return toml_table_count(source) > 0


def toml_has_lists(source: "str | bytes | Path") -> bool:
    """Return True if the TOML document contains at least one list value."""
    return toml_list_count(source) > 0


def toml_is_empty(source: "str | bytes | Path") -> bool:
    """Return True if the TOML document has no keys."""
    return toml_total_keys(source) == 0


def toml_string_density(source: "str | bytes | Path") -> float:
    """Return ratio of string values to total value count. 0.0 if no values."""
    model = load_toml(source)
    data = model.get("data", model)
    total = 0
    strings = 0
    for v in data.values():
        total += 1
        if isinstance(v, str):
            strings += 1
    if total == 0:
        return 0.0
    return strings / total


def toml_numeric_density(source: "str | bytes | Path") -> float:
    """Return ratio of numeric values to total top-level value count. 0.0 if no values."""
    model = load_toml(source)
    data = model.get("data", model)
    total = len(data)
    if total == 0:
        return 0.0
    numeric = sum(1 for v in data.values() if isinstance(v, (int, float)) and not isinstance(v, bool))
    return numeric / total


def toml_depth(source: "str | bytes | Path") -> int:
    """Return the maximum nesting depth of the TOML document. 0 for empty, 1 for flat."""
    model = load_toml(source)
    data = model.get("data", model)

    def _depth(node: dict) -> int:
        if not node:
            return 0
        max_child = 0
        for v in node.values():
            if isinstance(v, dict):
                max_child = max(max_child, _depth(v))
        return 1 + max_child

    return _depth(data)




def toml_avg_key_length(source: "str | bytes | Path") -> float:
    """Return the average length of top-level key names. 0.0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    keys = list(data.keys())
    if not keys:
        return 0.0
    return sum(len(k) for k in keys) / len(keys)


def toml_max_value_length(source: "str | bytes | Path") -> int:
    """Return the max string length of any top-level value. 0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    if not data:
        return 0
    return max(len(str(v)) for v in data.values())


def toml_nested_table_count(source: "str | bytes | Path") -> int:
    """Return the count of top-level values that are dicts (nested tables)."""
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, dict))


def toml_has_booleans(source: "str | bytes | Path") -> bool:
    """Return True if any top-level value is a boolean."""
    model = load_toml(source)
    data = model.get("data", model)
    return any(isinstance(v, bool) for v in data.values())


def toml_key_count_per_table(source: "str | bytes | Path") -> list:
    """Return list of key counts for each top-level table. Empty list if no tables."""
    model = load_toml(source)
    data = model.get("data", model)
    return [len(v) for v in data.values() if isinstance(v, dict)]


def toml_is_flat(source: "str | bytes | Path") -> bool:
    """Return True if no top-level value is a dict (no nested tables)."""
    model = load_toml(source)
    data = model.get("data", model)
    return not any(isinstance(v, dict) for v in data.values())


def toml_total_value_count(source: "str | bytes | Path") -> int:
    """Return total count of leaf values across all tables (recursive)."""
    model = load_toml(source)
    data = model.get("data", model)

    def _count(d):
        total = 0
        for v in d.values():
            if isinstance(v, dict):
                total += _count(v)
            else:
                total += 1
        return total

    return _count(data)


def toml_max_list_length(source: "str | bytes | Path") -> int:
    """Return the length of the longest top-level list value. 0 if none."""
    model = load_toml(source)
    data = model.get("data", model)
    lists = [v for v in data.values() if isinstance(v, list)]
    return max((len(lst) for lst in lists), default=0)


def toml_all_keys_lowercase(source: "str | bytes | Path") -> bool:
    """Return True if all top-level key names are lowercase (no uppercase chars)."""
    model = load_toml(source)
    data = model.get("data", model)
    return all(k == k.lower() for k in data.keys())


def toml_has_numeric_values(source: "str | bytes | Path") -> bool:
    """Return True if at least one top-level value is numeric (int or float, not bool)."""
    model = load_toml(source)
    data = model.get("data", model)
    return any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in data.values())


def toml_avg_list_length(source: "str | bytes | Path") -> float:
    """Return the average length of top-level list values. 0.0 if no lists."""
    model = load_toml(source)
    data = model.get("data", model)
    lists = [v for v in data.values() if isinstance(v, list)]
    if not lists:
        return 0.0
    return sum(len(lst) for lst in lists) / len(lists)


def toml_max_numeric_value(source: "str | bytes | Path") -> float:
    """Return the maximum numeric value at top level. 0.0 if no numeric values."""
    model = load_toml(source)
    data = model.get("data", model)
    nums = [v for v in data.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return float(max(nums)) if nums else 0.0


def toml_min_numeric_value(source: "str | bytes | Path") -> float:
    """Return the minimum numeric value at top level. 0.0 if no numeric values."""
    model = load_toml(source)
    data = model.get("data", model)
    nums = [v for v in data.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return float(min(nums)) if nums else 0.0


def toml_bool_ratio(source: "str | bytes | Path") -> float:
    """Return ratio of boolean values to total top-level value count. 0.0 if no values."""
    model = load_toml(source)
    data = model.get("data", model)
    total = len(data)
    if total == 0:
        return 0.0
    bools = sum(1 for v in data.values() if isinstance(v, bool))
    return bools / total


def toml_numeric_sum(source: "str | bytes | Path") -> float:
    """Return sum of all top-level numeric values (int and float, not bool). 0.0 if none."""
    model = load_toml(source)
    data = model.get("data", model)
    return float(sum(v for v in data.values() if isinstance(v, (int, float)) and not isinstance(v, bool)))


def toml_unique_value_count(source: "str | bytes | Path") -> int:
    """Return the count of unique scalar values at top level (excluding tables and lists)."""
    model = load_toml(source)
    data = model.get("data", model)
    scalars = [v for v in data.values() if not isinstance(v, (dict, list))]
    return len(set(str(v) for v in scalars))


def toml_file_size_bytes(source: "str | bytes | Path") -> int:
    """Return the file size in bytes. 0 if source is bytes/str (not a path)."""
    if isinstance(source, (str, Path)):
        p = Path(source)
        if p.is_file():
            return p.stat().st_size
    return 0


def toml_max_key_length(source: "str | bytes | Path") -> int:
    """Return the length of the longest top-level key name. 0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    keys = list(data.keys())
    return max((len(k) for k in keys), default=0)


def toml_avg_value_length(source: "str | bytes | Path") -> float:
    """Return the average string-representation length of top-level values. 0.0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    if not data:
        return 0.0
    return sum(len(str(v)) for v in data.values()) / len(data)


def toml_string_key_ratio(source: "str | bytes | Path") -> float:
    """Return ratio of keys whose top-level values are strings. 0.0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    total = len(data)
    if total == 0:
        return 0.0
    strings = sum(1 for v in data.values() if isinstance(v, str))
    return strings / total


def toml_min_key_length(source: "str | bytes | Path") -> int:
    """Return the length of the shortest top-level key name. 0 if no keys."""
    model = load_toml(source)
    data = model.get("data", model)
    keys = list(data.keys())
    return min((len(k) for k in keys), default=0)


def toml_list_item_count(source: "str | bytes | Path") -> int:
    """Return total number of items across all top-level list values."""
    model = load_toml(source)
    data = model.get("data", model)
    return sum(len(v) for v in data.values() if isinstance(v, list))


def toml_is_single_table(source: "str | bytes | Path") -> bool:
    """Return True if the document is a flat single table (no nested table sections)."""
    return toml_table_count(source) == 0


def toml_string_count(source: "str | bytes | Path") -> int:
    """Return count of top-level string values (alias for toml_string_value_count)."""
    return toml_string_value_count(source)


def toml_numeric_count(source: "str | bytes | Path") -> int:
    """Return count of top-level numeric values (alias for toml_numeric_value_count)."""
    return toml_numeric_value_count(source)


def toml_bool_count(source: "str | bytes | Path") -> int:
    """Return count of top-level boolean values (alias for toml_boolean_value_count)."""
    return toml_boolean_value_count(source)


def toml_has_boolean_value(source: "str | bytes | Path") -> bool:
    """Return True if any top-level value is a boolean (alias for toml_has_booleans)."""
    return toml_has_booleans(source)



def toml_has_exactly_two_keys(source: "str | bytes | Path") -> bool:
    """Return True if the document has exactly two top-level keys."""
    return toml_total_keys(source) == 2


def toml_has_only_booleans(source: "str | bytes | Path") -> bool:
    """Return True if every top-level value is a boolean."""
    model = load_toml(source)
    data = model.get("data", model)
    if not data:
        return False
    return all(isinstance(v, bool) for v in data.values())


def toml_has_mixed_value_types(source: "str | bytes | Path") -> bool:
    """Return True if top-level values include more than one distinct Python type."""
    model = load_toml(source)
    data = model.get("data", model)
    types = set(type(v) for v in data.values())
    return len(types) > 1


def toml_non_boolean_count(source: "str | bytes | Path") -> int:
    """Return count of top-level values that are NOT booleans."""
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if not isinstance(v, bool))


def toml_has_no_booleans(source: "str | bytes | Path") -> bool:
    """Return True if no top-level value is a boolean."""
    return not toml_has_booleans(source)


def toml_has_at_least_one_numeric(source: "str | bytes | Path") -> bool:
    """Return True if at least one top-level value is numeric (int or float, not bool)."""
    return toml_has_numeric_values(source)


"""ndjson_stream_metrics.py — Extracted NDJSON analytics functions.

Split out of json_stream.py (TC-PA-017 monolith healing) to keep each source module
under the 800-LOC architecture cap. Pure analytics functions over NDJSON record lists;
behavior is unchanged from the original definitions. Base loaders and sibling metrics
that remain in json_stream.py are brought in via the star-import below. Re-exported
from json_stream.py so every public name stays importable from its original path.
"""
from __future__ import annotations

from .json_stream import *  # noqa: F401,F403 - base loaders/metrics reused at call time


def ndjson_avg_numeric_value(source: "Any") -> float:
    """Return average of all numeric field values. 0.0 if none."""
    records = load_ndjson(source)
    nums = []
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    nums.append(v)
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def ndjson_total_string_length(source: "Any") -> int:
    """Return total character length of all string field values. 0 if none."""
    records = load_ndjson(source)
    total = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, str):
                    total += len(v)
    return total


def ndjson_numeric_density(source: "Any") -> float:
    """Return ratio of numeric fields to total fields. 0.0 if no fields."""
    records = load_ndjson(source)
    total_fields = 0
    numeric_fields = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                total_fields += 1
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    numeric_fields += 1
    if total_fields == 0:
        return 0.0
    return numeric_fields / total_fields


def ndjson_min_record_size(source: "Any") -> int:
    """Return the size in bytes of the smallest NDJSON record. 0 if empty."""
    import json as _json
    records = load_ndjson(source)
    if not records:
        return 0
    sizes = [len(_json.dumps(r).encode("utf-8")) for r in records]
    return min(sizes)


def ndjson_has_numeric_fields(source: "Any") -> bool:
    """Return True if any record has at least one numeric field value."""
    records = load_ndjson(source)
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    return True
    return False


def ndjson_has_lists(source: "Any") -> bool:
    """Return True if any record has at least one list field value."""
    records = load_ndjson(source)
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, list):
                    return True
    return False


def ndjson_schema_consistency(source: "Any") -> float:
    """Return ratio of records with the most common field count to total. 0.0 if empty."""
    from collections import Counter as _Counter
    records = load_ndjson(source)
    if not records:
        return 0.0
    counts = _Counter(len(r) if isinstance(r, dict) else 0 for r in records)
    most_common_count = counts.most_common(1)[0][1]
    return most_common_count / len(records)


def ndjson_total_numeric_sum(source: "Any") -> float:
    """Return sum of all numeric field values across all records. 0.0 if none."""
    records = load_ndjson(source)
    total = 0.0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    total += v
    return total


def ndjson_is_single_record(source: "Any") -> bool:
    """Return True if the source contains exactly one record."""
    records = load_ndjson(source)
    return len(records) == 1


def ndjson_boolean_density(source: "Any") -> float:
    """Return ratio of boolean fields to total fields. 0.0 if no fields."""
    records = load_ndjson(source)
    total_fields = 0
    bool_fields = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                total_fields += 1
                if isinstance(v, bool):
                    bool_fields += 1
    if total_fields == 0:
        return 0.0
    return bool_fields / total_fields


def ndjson_max_field_value_length(source: "Any") -> int:
    """Return maximum string length of any field value. 0 if no string fields."""
    records = load_ndjson(source)
    max_len = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, str) and len(v) > max_len:
                    max_len = len(v)
    return max_len


def ndjson_string_density(source: "Any") -> float:
    """Return ratio of string fields to total fields. 0.0 if no fields."""
    records = load_ndjson(source)
    total_fields = 0
    string_fields = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                total_fields += 1
                if isinstance(v, str):
                    string_fields += 1
    if total_fields == 0:
        return 0.0
    return string_fields / total_fields


def ndjson_avg_list_length(source: "Any") -> float:
    """Return average length of list-type fields. 0.0 if no list fields."""
    records = load_ndjson(source)
    lengths: list[int] = []
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, list):
                    lengths.append(len(v))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def ndjson_nested_count(source: "Any") -> int:
    """Return count of fields that are dicts (nested objects). 0 if none."""
    records = load_ndjson(source)
    count = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, dict):
                    count += 1
    return count


def ndjson_min_record_fields(source: "Any") -> int:
    """Return the minimum number of fields across all records. 0 if no records."""
    records = load_ndjson(source)
    if not records:
        return 0
    min_fields = None
    for r in records:
        if isinstance(r, dict):
            n = len(r)
            if min_fields is None or n < min_fields:
                min_fields = n
    return min_fields if min_fields is not None else 0


# ---------------------------------------------------------------------------
# Additional analytics — TC-PRODUCT-PILOT-NDJSON-001
# ---------------------------------------------------------------------------

def ndjson_has_uniform_types(source: "Any") -> bool:
    """Return True if all records share the same Python type (non-empty source)."""
    records = source if isinstance(source, list) else load_ndjson(source)
    if not records:
        return False
    first_type = type(records[0])
    return all(type(r) is first_type for r in records)


def ndjson_value_variance(source: "Any") -> float:
    """Return population variance of all numeric values across all records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    nums = []
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    nums.append(float(v))
    if not nums:
        return 0.0
    mean = sum(nums) / len(nums)
    return sum((x - mean) ** 2 for x in nums) / len(nums)


def ndjson_file_size_bytes(source: "Any") -> int:
    """Return file size in bytes for a path source. Returns 0 for bytes/list/missing."""
    if isinstance(source, (bytes, bytearray, list)):
        return 0
    try:
        return Path(str(source)).stat().st_size
    except (OSError, ValueError):
        return 0


def ndjson_avg_record_depth(source: "Any") -> float:
    """Return average nesting depth across all records. 0.0 if no records."""
    records = source if isinstance(source, list) else load_ndjson(source)

    def _depth(obj: "Any") -> int:
        if isinstance(obj, dict):
            if not obj:
                return 1
            return 1 + max(_depth(v) for v in obj.values())
        if isinstance(obj, list):
            if not obj:
                return 1
            return 1 + max(_depth(v) for v in obj)
        return 0

    if not records:
        return 0.0
    return sum(_depth(r) for r in records) / len(records)


def ndjson_nonempty_record_count(source: "Any") -> int:
    """Return count of records that are not empty."""
    records = source if isinstance(source, list) else load_ndjson(source)
    return sum(1 for r in records if r)


def ndjson_nonempty_record_ratio(source: "Any") -> float:
    """Return ratio of non-empty records to total records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    if not records:
        return 0.0
    return sum(1 for r in records if r) / len(records)


def ndjson_has_all_same_keys(source: "Any") -> bool:
    """Return True if all dict records share the same set of field keys."""
    records = source if isinstance(source, list) else load_ndjson(source)
    dict_records = [r for r in records if isinstance(r, dict)]
    if not dict_records:
        return False
    first_keys = set(dict_records[0].keys())
    return all(set(r.keys()) == first_keys for r in dict_records[1:])


def ndjson_max_list_length(source: "Any") -> int:
    """Return the maximum length of any list value in any record."""
    records = source if isinstance(source, list) else load_ndjson(source)
    max_len = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, list):
                    max_len = max(max_len, len(v))
        elif isinstance(r, list):
            max_len = max(max_len, len(r))
    return max_len


def ndjson_null_ratio(source: "Any") -> float:
    """Return ratio of null (None) values to total field values."""
    records = source if isinstance(source, list) else load_ndjson(source)
    total = 0
    null_count = 0
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                total += 1
                if v is None:
                    null_count += 1
    if total == 0:
        return 0.0
    return null_count / total


def ndjson_string_value_count(source: "Any") -> int:
    """Return count of string values across all dict records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    return sum(
        1 for r in records if isinstance(r, dict)
        for v in r.values() if isinstance(v, str)
    )


def ndjson_string_value_count_minus_record_count(source: "Any") -> int:
    """Return max(0, string_value_count - record_count)."""
    records = source if isinstance(source, list) else load_ndjson(source)
    string_count = sum(
        1 for r in records if isinstance(r, dict)
        for v in r.values() if isinstance(v, str)
    )
    return max(0, string_count - len(records))


def ndjson_string_value_count_exceeds_record_count(source: "Any") -> bool:
    """Return True if string value count exceeds total record count."""
    return ndjson_string_value_count_minus_record_count(source) > 0


def ndjson_all_records_are_dicts(source: "Any") -> bool:
    """Return True if every record in the source is a dict."""
    records = source if isinstance(source, list) else load_ndjson(source)
    if not records:
        return False
    return all(isinstance(r, dict) for r in records)


def ndjson_bool_value_count(source: "Any") -> int:
    """Return count of boolean values across all dict records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    return sum(
        1 for r in records if isinstance(r, dict)
        for v in r.values() if isinstance(v, bool)
    )


def ndjson_null_value_count(source: "Any") -> int:
    """Return count of null (None) values across all dict records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    return sum(
        1 for r in records if isinstance(r, dict)
        for v in r.values() if v is None
    )


def ndjson_numeric_range(source: "Any") -> float:
    """Return range (max - min) of all numeric values. 0.0 if fewer than 2 values."""
    records = source if isinstance(source, list) else load_ndjson(source)
    nums = []
    for r in records:
        if isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    nums.append(float(v))
    if len(nums) < 2:
        return 0.0
    return float(max(nums) - min(nums))


# ---------------------------------------------------------------------------
# Aliases for alternative / short names
# ---------------------------------------------------------------------------

ndjson_max_record_key_count = ndjson_max_field_count
ndjson_deepest_nesting = ndjson_max_nesting_depth
ndjson_max_key_count = ndjson_max_field_count
ndjson_array_field_count = ndjson_list_field_count
ndjson_avg_values_per_record = ndjson_average_field_count
ndjson_avg_field_count = ndjson_average_field_count
def ndjson_avg_key_length(source: "Any") -> float:
    """Return average length of field names across all dict records."""
    records = source if isinstance(source, list) else load_ndjson(source)
    names: set = set()
    for r in records:
        if isinstance(r, dict):
            names.update(r.keys())
    if not names:
        return 0.0
    return sum(len(n) for n in names) / len(names)
ndjson_numeric_ratio = ndjson_numeric_density
ndjson_numeric_field_ratio = ndjson_numeric_density
ndjson_bool_ratio = ndjson_boolean_density
ndjson_bool_field_count = ndjson_boolean_field_count
ndjson_unique_key_count = ndjson_unique_field_count
ndjson_distinct_key_count = ndjson_unique_field_count
ndjson_avg_key_count = ndjson_average_field_count
ndjson_string_length_sum = ndjson_total_string_length
ndjson_numeric_sum = ndjson_total_numeric_sum
ndjson_dict_field_total = ndjson_total_field_count
ndjson_total_value_count = ndjson_total_field_count
ndjson_avg_string_value_length = ndjson_avg_string_length
ndjson_key_count_variance = ndjson_field_count_variance
ndjson_object_field_variance = ndjson_field_count_variance

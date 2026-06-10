"""
format-factory: NDJSON (Newline-Delimited JSON) FOSS Python track.

Minimal FOSS implementation for .ndjson / .jsonl format support.
Spec: https://ndjson.org/ — royalty-free, public domain format.
Uses stdlib json only — no external dependencies.
Acquisition Gates 1-4 initiated.

FOSS track only — no commercial readiness implied.
"""

from .ndjson_codec import (
    NdjsonError,
    NdjsonParseError,
    probe_ndjson,
    load_ndjson,
    write_ndjson,
    append_record,
    filter_records,
    get_field_names,
    export_to_csv,
    get_record_count,
    validate_schema,
    roundtrip,
    sort_records,
    write_csv,
    field_stats,
    merge_ndjson,
    group_by,
    sum_field,
    rename_field,
    tail,
    pick,
    average_value,
    count_by,
    distinct_values,
    to_jsonl_str,
    pluck,
    min_value,
    max_value,
    deduplicate,
    count_records,
    zip_records,
    sort_by,
    aggregate,
    head,
)

__all__ = [
    "NdjsonError",
    "NdjsonParseError",
    "probe_ndjson",
    "load_ndjson",
    "write_ndjson",
    "append_record",
    "filter_records",
    "get_field_names",
    "export_to_csv",
    "get_record_count",
    "validate_schema",
    "roundtrip",
    "sort_records",
    "write_csv",
    "field_stats",
    "merge_ndjson",
    "group_by",
    "sum_field",
    "rename_field",
    "tail",
    "pick",
    "average_value",
    "count_by",
    "distinct_values",
    "to_jsonl_str",
    "pluck",
    "min_value",
    "max_value",
    "deduplicate",
    "count_records",
    "zip_records",
    "sort_by",
    "aggregate",
    "head",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

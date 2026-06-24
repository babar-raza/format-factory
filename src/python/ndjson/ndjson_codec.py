"""
ndjson_codec.py — NDJSON (Newline-Delimited JSON) codec for format-factory.

NDJSON (also known as JSON Lines, .jsonl) stores one valid JSON value per line.
Spec reference: https://ndjson.org/ (public, royalty-free).
Uses Python stdlib json module — no external dependencies.

Acquisition gates 1-4 initiated.
commercial_product_ready: false
track: python-foss
spec_concept: Newline-delimited JSON record stream
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_LINES = 1_000_000


class NdjsonError(Exception):
    """Base exception for NDJSON codec errors."""


class NdjsonParseError(NdjsonError):
    """Raised when NDJSON content cannot be parsed."""


def probe_ndjson(source) -> bool:
    """Probe whether source looks like a valid NDJSON file.

    Checks that the first non-empty line is a valid JSON value.
    Does not raise on malformed input — returns False instead.

    Args:
        source: Path to a file, bytes, or string to probe.

    Returns:
        True if source appears to be NDJSON, False otherwise.
    """
    try:
        raw = _read_source(source)
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines():
            line = line.strip()
            if line:
                json.loads(line)
                return True
        return False  # All lines empty
    except Exception:
        return False


def load_ndjson(source) -> list[Any]:
    """Parse an NDJSON source and return a list of decoded values.

    Empty lines are skipped.  Returns a list of Python objects (dicts,
    lists, strings, numbers, booleans, or null).

    Args:
        source: Path to a file, bytes, or string to parse.

    Returns:
        List of decoded JSON values, one per non-empty line.

    Raises:
        NdjsonParseError: If any non-empty line is not valid JSON.
        NdjsonError: For size/read errors.
    """
    raw = _read_source(source)
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        raise NdjsonError(f"Line count {len(lines)} exceeds limit of {MAX_LINES}")
    records: list[Any] = []
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise NdjsonParseError(f"Line {lineno}: {exc}") from exc
    return records


def write_ndjson(records: list[Any], dest: str | Path) -> None:
    """Write a list of values to an NDJSON file.

    Each value is serialized as a single JSON line (compact, no indentation).

    Args:
        records: List of JSON-serializable values.
        dest: Destination file path.

    Raises:
        NdjsonError: If dest cannot be written or a value is not JSON-serializable.
    """
    out = Path(dest)
    lines: list[str] = []
    for i, record in enumerate(records):
        try:
            lines.append(json.dumps(record, ensure_ascii=False))
        except (TypeError, ValueError) as exc:
            raise NdjsonError(f"Record {i} is not JSON-serializable: {exc}") from exc
    content = "\n".join(lines)
    if content:
        content += "\n"
    try:
        out.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise NdjsonError(f"Cannot write {out}: {exc}") from exc


def append_record(dest: str | Path, record: Any) -> None:
    """Append a single JSON record to an NDJSON file.

    Creates the file if it does not exist.  The record is serialized as
    a single compact JSON line terminated with a newline.

    Args:
        dest:   Path to the destination NDJSON file (created if missing).
        record: JSON-serializable value to append.

    Raises:
        NdjsonError: If dest cannot be written or record is not
                     JSON-serializable.
    """
    out = Path(dest)
    try:
        line = json.dumps(record, ensure_ascii=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise NdjsonError(f"Record is not JSON-serializable: {exc}") from exc
    try:
        with out.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError as exc:
        raise NdjsonError(f"Cannot append to {out}: {exc}") from exc


def filter_records(source, key: str, value: Any) -> list[Any]:
    """Return records from an NDJSON source where a dict field matches a value.

    Only object (dict) records are eligible for matching; non-object records
    (arrays, strings, numbers, booleans, null) are always excluded.

    Args:
        source: Path to a file, bytes, or string to filter.
        key:    Dict key to match.
        value:  Value to compare against ``record[key]``.

    Returns:
        List of matching dict records where ``record.get(key) == value``.

    Raises:
        NdjsonParseError: If any non-empty line is not valid JSON.
        NdjsonError: For size/read errors.
    """
    records = load_ndjson(source)
    return [r for r in records if isinstance(r, dict) and r.get(key) == value]


def get_field_names(source) -> list[str]:
    """Return sorted unique field names across all dict records.

    Non-dict records (arrays, strings, numbers, booleans, null) are skipped.
    Returns an empty list if no dict records are found.

    Args:
        source: Path to a file, bytes, or string.

    Returns:
        Sorted list of unique key strings found in dict records.

    Raises:
        NdjsonParseError: If any non-empty line is not valid JSON.
        NdjsonError: For size/read errors.
    """
    records = load_ndjson(source)
    keys: set[str] = set()
    for r in records:
        if isinstance(r, dict):
            keys.update(r.keys())
    return sorted(keys)



def export_to_csv(source) -> str:
    """Export NDJSON dict records to a CSV string.

    Non-dict records are skipped. Field names sorted.
    Missing fields rendered as empty strings.
    Returns empty string if no dict records.
    """
    records = load_ndjson(source)
    dict_records = [r for r in records if isinstance(r, dict)]
    keys = sorted({k for r in dict_records for k in r})
    if not keys:
        return ""
    lines = [",".join(_csv_field(k) for k in keys)]
    for r in dict_records:
        lines.append(",".join(_csv_field(str(r.get(k, ""))) for k in keys))
    return '\n'.join(lines) + '\n'


def _csv_field(v: str) -> str:
    """Quote a CSV field if needed (RFC 4180)."""
    needs_quote = any(c in v for c in (",", '\n', '\r', chr(34), '\t'))
    if needs_quote:
        return chr(34) + v.replace(chr(34), chr(34) + chr(34)) + chr(34)
    return v


def get_record_count(source) -> int:
    """Return the number of non-empty records in an NDJSON source."""
    return len(load_ndjson(source))


def count_records(source) -> int:
    """Return the number of non-empty records in an NDJSON source.

    Equivalent to ``get_record_count()`` but named for ergonomic consistency
    with other Format Factory codec APIs.

    Args:
        source: NDJSON file path, bytes, or string content.

    Returns:
        Count of non-empty (non-blank-line) records.

    Raises:
        NdjsonParseError: If any non-empty line is not valid JSON.
        NdjsonError: For size/read errors.
    """
    return len(load_ndjson(source))


def validate_schema(source, schema: dict[str, Any]) -> dict[str, Any]:
    """Validate each record in an NDJSON source against a simple schema dict.

    The schema is a dict mapping field names to expected types (as Python types
    or type name strings). Records missing required fields or having wrong types
    are reported as validation errors.

    Args:
        source: NDJSON file path, bytes, or string content.
        schema: Dict mapping field_name -> expected_type.
                Values can be Python types (str, int, float, bool, list, dict)
                or type-name strings ('str', 'int', 'float', 'bool', 'list', 'dict').

    Returns:
        Dict with keys:
            valid (bool): True if all records are valid.
            total_records (int): Number of records checked.
            valid_records (int): Number of valid records.
            errors (list[dict]): One entry per invalid record with record_index and details.

    Example:
        validate_schema(path, {"name": str, "age": int})
    """
    _type_map = {
        "str": str, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict,
    }
    resolved: dict[str, type] = {}
    for field, t in schema.items():
        if isinstance(t, type):
            resolved[field] = t
        elif isinstance(t, str) and t in _type_map:
            resolved[field] = _type_map[t]
        else:
            resolved[field] = object  # any type accepted

    records = load_ndjson(source)
    errors: list[dict[str, Any]] = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append({"record_index": i, "error": "not_a_dict", "value": repr(record)[:80]})
            continue
        for field, expected_type in resolved.items():
            if field not in record:
                errors.append({"record_index": i, "error": "missing_field", "field": field})
            elif expected_type is not object and not isinstance(record[field], expected_type):
                errors.append({
                    "record_index": i,
                    "error": "wrong_type",
                    "field": field,
                    "expected": expected_type.__name__,
                    "actual": type(record[field]).__name__,
                })

    valid_count = len(records) - len({e["record_index"] for e in errors})
    return {
        "valid": len(errors) == 0,
        "total_records": len(records),
        "valid_records": valid_count,
        "errors": errors,
    }


def sort_records(source, key: str, *, reverse: bool = False) -> list[Any]:
    """Sort NDJSON records by a field value.

    Records missing the key field are sorted to the end (None is treated as
    the minimum sort value, i.e., sorted last when reverse=False).

    Args:
        source: Path, bytes, or string of NDJSON content.
        key:    Field name to sort by.
        reverse: If True, sort in descending order.

    Returns:
        New list of records sorted by the given key.

    Raises:
        NdjsonError: If source cannot be loaded.
    """
    records = load_ndjson(source)
    return sorted(
        records,
        key=lambda r: (r.get(key) is None, r.get(key)),
        reverse=reverse,
    )


def merge_ndjson(source_a, source_b) -> list[Any]:
    """Merge records from two NDJSON sources into a single list.

    Loads both sources and returns a new list with all records from
    source_a followed by all records from source_b.

    Args:
        source_a: First source (path, bytes, or string).
        source_b: Second source (path, bytes, or string).

    Returns:
        Combined list of all records from both sources.

    Raises:
        NdjsonParseError: If either source contains invalid JSON lines.
        NdjsonError: For size/read errors.
    """
    return load_ndjson(source_a) + load_ndjson(source_b)


def to_jsonl_str(records: list[Any]) -> str:
    """Serialize a list of records to a NDJSON/JSONL string.

    Each record is serialized to a single JSON line, separated by newlines.

    Args:
        records: List of JSON-serializable values.

    Returns:
        NDJSON string (newline-delimited JSON).
    """
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)


def roundtrip(source, dest: str | Path) -> list[Any]:
    """Write NDJSON records to dest then reload from dest, proving round-trip fidelity.

    Loads source, writes all records to dest using write_ndjson(), then reloads
    from dest and returns the reloaded records list.

    Args:
        source: Original source (path, bytes, or string).
        dest:   Destination file path to write and reload.

    Returns:
        Reloaded list of records from dest.

    Raises:
        NdjsonError: If write or reload fails.
    """
    records = load_ndjson(source)
    write_ndjson(records, dest)
    return load_ndjson(dest)


def rename_field(source, old_name: str, new_name: str) -> list:
    """Rename a field in every NDJSON record.

    Records that don't contain old_name are returned unchanged.

    Args:
        source: NDJSON source (bytes, str, or Path).
        old_name: Field name to rename.
        new_name: Replacement field name.

    Returns:
        List of records with old_name replaced by new_name.
    """
    records = load_ndjson(source)
    result = []
    for rec in records:
        if isinstance(rec, dict) and old_name in rec:
            new_rec = {(new_name if k == old_name else k): v for k, v in rec.items()}
            result.append(new_rec)
        else:
            result.append(rec)
    return result


def write_csv(source, dest: str | Path) -> None:
    """Write NDJSON records to a CSV file.

    This is the file-writing counterpart of export_to_csv().
    All records must be dicts. Headers are taken from the union of all keys
    in the first record, or from all records if the first is missing fields.

    Args:
        source: NDJSON source (bytes, str, or Path).
        dest:   Destination CSV file path.

    Raises:
        NdjsonError: If records are not dicts or dest cannot be written.
    """
    csv_str = export_to_csv(source)
    try:
        Path(dest).write_text(csv_str, encoding="utf-8")
    except OSError as exc:
        raise NdjsonError(f"Cannot write CSV to {dest}: {exc}") from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_source(source) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str):
        path = Path(source)
        if path.exists():
            _check_size(path)
            return path.read_bytes()
        return source.encode("utf-8")
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise NdjsonError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    raise NdjsonError(f"Unsupported source type: {type(source)}")


# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-003

def to_tsv(source: "Any", include_header: bool = True) -> str:
    """Export NDJSON records to a TSV (tab-separated values) string.

    Args:
        source: File path, bytes, or list of records.
        include_header: If True, include a header row with field names.

    Returns:
        TSV string with tab-separated columns and newline-separated rows.
        Fields not present in a row are rendered as empty string.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    if not records:
        return ""

    # Collect all unique field names in order of first appearance
    field_names: list[str] = []
    seen: set[str] = set()
    for rec in records:
        if isinstance(rec, dict):
            for k in rec:
                if k not in seen:
                    field_names.append(k)
                    seen.add(k)

    if not field_names:
        # Non-dict records: just convert each to string
        rows = [str(r) for r in records]
        return "\n".join(rows)

    lines: list[str] = []
    if include_header:
        lines.append("\t".join(field_names))

    for rec in records:
        if isinstance(rec, dict):
            row = "\t".join(str(rec.get(f, "")) for f in field_names)
        else:
            row = str(rec)
        lines.append(row)

    return "\n".join(lines)


def to_markdown_table(source: "Any") -> str:
    """Export NDJSON records to a GitHub-flavored Markdown table.

    Args:
        source: File path, bytes, or list of dict records.

    Returns:
        Markdown table string. Returns empty string for empty input.
        Non-dict records are serialized as strings in a single column.
    """
    records = source if isinstance(source, list) else load_ndjson(source)
    if not records:
        return ""

    # Collect field names
    field_names: list[str] = []
    seen: set[str] = set()
    for rec in records:
        if isinstance(rec, dict):
            for k in rec:
                if k not in seen:
                    field_names.append(k)
                    seen.add(k)

    if not field_names:
        lines = ["| value |", "| --- |"]
        for rec in records:
            lines.append(f"| {str(rec)} |")
        return "\n".join(lines)

    header = "| " + " | ".join(str(f) for f in field_names) + " |"
    separator = "| " + " | ".join("---" for _ in field_names) + " |"
    lines = [header, separator]
    for rec in records:
        if isinstance(rec, dict):
            cells = " | ".join(str(rec.get(f, "")) for f in field_names)
        else:
            cells = " | ".join(str(rec) if i == 0 else "" for i in range(len(field_names)))
        lines.append(f"| {cells} |")
    return "\n".join(lines)


def _check_size(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise NdjsonError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")


# ---------------------------------------------------------------------------
# Analytics functions moved to ndjson_analytics.py (TC-HEAL-FORMATS-BATCH1)
# ---------------------------------------------------------------------------
try:
    from .ndjson_record_stats import *  # noqa: F401, F403
except ImportError:
    pass
try:
    from .json_stream import *  # noqa: F401, F403
except ImportError:
    pass

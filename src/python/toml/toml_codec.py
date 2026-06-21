"""
toml_codec.py — TOML format codec for format-factory-toml.

FOSS track. Uses stdlib tomllib (Python 3.11+) for read and a minimal
hand-built serializer for write (no external dependencies).

Acquisition Gates 1-4 initiated.

License: Apache-2.0
"""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MiB


class TomlError(Exception):
    """Base exception for TOML codec errors."""


class TomlInputError(TomlError):
    """Raised when the file cannot be read."""


class TomlParseError(TomlError):
    """Raised when the TOML content is malformed."""


class TomlWriteError(TomlError):
    """Raised when writing TOML fails."""


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _serialize_value(value: Any, indent: int = 0) -> str:
    """Serialize a single TOML value to a string representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        return f'"{escaped}"'
    if isinstance(value, list):
        if not value:
            return "[]"
        items = [_serialize_value(v) for v in value]
        return "[" + ", ".join(items) + "]"
    if isinstance(value, dict):
        # Inline table for simple values; caller handles section tables
        pairs = ", ".join(f'{k} = {_serialize_value(v)}' for k, v in value.items())
        return "{" + pairs + "}"
    # Fallback
    return f'"{value}"'


def _write_section(lines: list[str], data: dict, prefix: str = "") -> None:
    """Recursively serialize a TOML dict to lines."""
    simple = {k: v for k, v in data.items() if not isinstance(v, dict) and not (isinstance(v, list) and v and isinstance(v[0], dict))}
    tables = {k: v for k, v in data.items() if isinstance(v, dict)}
    array_tables = {k: v for k, v in data.items() if isinstance(v, list) and v and isinstance(v[0], dict)}

    for k, v in simple.items():
        lines.append(f"{k} = {_serialize_value(v)}")

    for k, v in tables.items():
        section_key = f"{prefix}.{k}" if prefix else k
        lines.append(f"\n[{section_key}]")
        _write_section(lines, v, section_key)

    for k, v in array_tables.items():
        section_key = f"{prefix}.{k}" if prefix else k
        for item in v:
            lines.append(f"\n[[{section_key}]]")
            _write_section(lines, item, section_key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def probe_toml(source: str | bytes | Path) -> dict[str, Any]:
    """Probe a TOML source for metadata without full parse.

    Args:
        source: File path (str/Path) or raw bytes.

    Returns:
        Dict with: exists, size_bytes, top_level_keys, section_count, error (if any).
    """
    result: dict[str, Any] = {"format": "toml"}
    try:
        if isinstance(source, (bytes, bytearray)):
            data = tomllib.loads(source.decode("utf-8", errors="replace"))
            result["size_bytes"] = len(source)
        else:
            path = Path(source)
            result["path"] = str(path)
            result["exists"] = path.exists()
            if not path.exists():
                return result
            raw = path.read_bytes()
            result["size_bytes"] = len(raw)
            data = tomllib.loads(raw.decode("utf-8-sig", errors="replace"))
        result["top_level_keys"] = list(data.keys())
        result["section_count"] = sum(1 for v in data.values() if isinstance(v, dict))
        result["key_count"] = len(data)
    except Exception as exc:
        result["probe_error"] = str(exc)
    return result


def load_toml(source: str | bytes | Path) -> dict[str, Any]:
    """Load a TOML document from a file path or raw bytes.

    Args:
        source: File path (str/Path) or raw UTF-8 bytes.

    Returns:
        Neutral model dict with keys: format, path, data, top_level_keys, key_count.

    Raises:
        TomlInputError: File not found or not readable.
        TomlParseError: Malformed TOML content.
    """
    if isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise TomlInputError(f"Content size {len(source)} exceeds limit of {MAX_FILE_SIZE}")
        try:
            data = tomllib.loads(source.decode("utf-8-sig", errors="replace"))
        except tomllib.TOMLDecodeError as exc:
            raise TomlParseError(f"TOML parse error: {exc}") from exc
        return {
            "format": "toml",
            "path": "<bytes>",
            "data": data,
            "top_level_keys": list(data.keys()),
            "key_count": len(data),
        }

    path = Path(source)
    if not path.exists():
        raise TomlInputError(f"File not found: {path}")
    if not path.is_file():
        raise TomlInputError(f"Path is not a regular file: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise TomlInputError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")
    try:
        raw = path.read_bytes()
        data = tomllib.loads(raw.decode("utf-8-sig", errors="replace"))
    except tomllib.TOMLDecodeError as exc:
        raise TomlParseError(f"TOML parse error in {path}: {exc}") from exc
    except OSError as exc:
        raise TomlInputError(f"Cannot read file {path}: {exc}") from exc
    return {
        "format": "toml",
        "path": str(path),
        "data": data,
        "top_level_keys": list(data.keys()),
        "key_count": len(data),
    }


def write_toml(data: dict[str, Any], dest: str | Path) -> None:
    """Write a Python dict as TOML to dest.

    Uses a minimal hand-built serializer (no external deps).
    Supports: str, int, float, bool, list (of scalars), nested dicts (as sections),
    list-of-dicts (as array tables). Does NOT support datetime or mixed-type arrays.

    Args:
        data: Python dict to serialize.
        dest: Destination file path.

    Raises:
        TomlWriteError: If dest cannot be written.
    """
    lines: list[str] = []
    _write_section(lines, data)
    content = "\n".join(lines) + "\n"
    try:
        Path(dest).write_text(content, encoding="utf-8")
    except OSError as exc:
        raise TomlWriteError(f"Cannot write {dest}: {exc}") from exc


def get_keys(source: str | bytes | Path) -> list[str]:
    """Return the top-level keys of a TOML document.

    Args:
        source: File path (str/Path) or raw bytes.

    Returns:
        List of top-level key names.
    """
    model = load_toml(source)
    return model["top_level_keys"]


def roundtrip(source: str | bytes | Path, dest: str | Path) -> dict[str, Any]:
    """Load TOML, write to dest, reload and return the model.

    Args:
        source: Original source — file path or raw bytes.
        dest:   Destination file path to write and reload.

    Returns:
        Reloaded TOML model dict.
    """
    model = load_toml(source)
    write_toml(model["data"], dest)
    return load_toml(dest)


def get_value(source: str | bytes | Path, key_path: str) -> Any:
    """Get a value from a TOML document by dotted key path.

    Args:
        source:   File path (str/Path) or raw bytes.
        key_path: Dotted key path, e.g. "server.host" or "port".

    Returns:
        The value at the given path.

    Raises:
        KeyError: If the key path does not exist.
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)
    data = model["data"]
    parts = key_path.split(".")
    node: Any = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Key path {key_path!r} not found in TOML document")
        node = node[part]
    return node


def merge_toml(source_a: str | bytes | Path, source_b: str | bytes | Path) -> dict[str, Any]:
    """Merge two TOML documents, with source_b winning on key conflicts.

    Top-level dict keys from source_b override source_a.
    Sub-dicts are merged recursively; scalar conflicts are won by source_b.

    Args:
        source_a: Base TOML — file path or raw bytes.
        source_b: Override TOML — file path or raw bytes.

    Returns:
        Merged Python dict (not a TOML model, just the data).
    """
    def _deep_merge(base: dict, override: dict) -> dict:
        result = dict(base)
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = _deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    model_a = load_toml(source_a)
    model_b = load_toml(source_b)
    return _deep_merge(model_a["data"], model_b["data"])


def to_json_str(source: str | bytes | Path) -> str:
    """Export a TOML document as a JSON string.

    Useful for converting TOML config to JSON for downstream consumption.

    Args:
        source: File path (str/Path) or raw bytes.

    Returns:
        JSON string representation of the TOML data (pretty-printed, sorted keys).
    """
    import json as _json
    model = load_toml(source)
    return _json.dumps(model["data"], indent=2, sort_keys=True, default=str)


def set_value(data: dict[str, Any], key_path: str, value: Any) -> dict[str, Any]:
    """Return a new dict with the value at dotted key_path set to value.

    Creates intermediate dicts as needed. Does not mutate the input.

    Args:
        data:     Python dict (e.g. from model["data"] or merge_toml()).
        key_path: Dotted key path, e.g. "server.host" or "port".
        value:    New value to set.

    Returns:
        New dict with the updated value at key_path.

    Raises:
        TypeError: If an intermediate key exists but is not a dict.
    """
    import copy as _copy
    result = _copy.deepcopy(data)
    parts = key_path.split(".")
    node = result
    for part in parts[:-1]:
        if part not in node:
            node[part] = {}
        elif not isinstance(node[part], dict):
            raise TypeError(f"Key '{part}' in path '{key_path}' is not a dict; cannot traverse")
        node = node[part]
    node[parts[-1]] = value
    return result


def delete_key(data: dict[str, Any], key_path: str) -> dict[str, Any]:
    """Return a new dict with the key at dotted key_path removed.

    Does not mutate the input. Raises KeyError if any segment of the path
    does not exist or if an intermediate node is not a dict.

    Args:
        data:     Python dict (e.g. from model["data"] or merge_toml()).
        key_path: Dotted key path, e.g. "server.host" or "port".

    Returns:
        New dict with the key removed.

    Raises:
        KeyError: If the key path does not exist.
        TypeError: If an intermediate key is not a dict.
    """
    import copy as _copy
    result = _copy.deepcopy(data)
    parts = key_path.split(".")
    node = result
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Key path {key_path!r} not found in TOML document")
        if not isinstance(node[part], dict):
            raise TypeError(f"Key '{part}' in path '{key_path}' is not a dict; cannot traverse")
        node = node[part]
    last = parts[-1]
    if not isinstance(node, dict) or last not in node:
        raise KeyError(f"Key path {key_path!r} not found in TOML document")
    del node[last]
    return result


def list_sections(source: str | bytes | Path) -> list[str]:
    """Return dotted paths of all dict-valued (section) keys in a TOML document.

    Scalar keys are not included. Nested sections are listed with dotted paths.

    Args:
        source: File path (str/Path) or raw bytes.

    Returns:
        Sorted list of dotted section paths, e.g. ["app", "app.db", "server"].

    Raises:
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)

    def _collect(node: dict, prefix: str, result: list[str]) -> None:
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                result.append(path)
                _collect(v, path, result)

    sections: list[str] = []
    _collect(model["data"], "", sections)
    return sorted(sections)


def get_section_keys(source: str | bytes | Path, section: str) -> list[str]:
    """Return the keys within a specific section (sub-table) of a TOML document.

    Args:
        source:  File path (str/Path) or raw bytes.
        section: Dotted section path, e.g. "server" or "database.primary".

    Returns:
        Sorted list of key names within the section.

    Raises:
        KeyError: If the section does not exist or is not a dict.
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)
    data = model["data"]
    parts = section.split(".")
    node: Any = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Section {section!r} not found in TOML document")
        node = node[part]
    if not isinstance(node, dict):
        raise KeyError(f"Section {section!r} is not a table (dict)")
    return sorted(node.keys())


def has_key(source: str | bytes | Path, key_path: str) -> bool:
    """Check whether a dotted key path exists in a TOML document.

    Args:
        source:   File path (str/Path) or raw bytes.
        key_path: Dotted key path, e.g. "server.host" or "port".

    Returns:
        True if the key path exists, False otherwise.

    Raises:
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)
    data = model["data"]
    parts = key_path.split(".")
    node: Any = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def count_keys(source: str | bytes | Path, *, recursive: bool = False) -> int:
    """Count the number of keys in a TOML document.

    Args:
        source:    File path (str/Path) or raw bytes.
        recursive: If True, count all keys recursively (including nested).
                   If False (default), count only top-level keys.

    Returns:
        Integer count of keys.

    Raises:
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)
    data = model["data"]
    if not recursive:
        return len(data)

    def _count(node: dict) -> int:
        total = 0
        for v in node.values():
            total += 1
            if isinstance(v, dict):
                total += _count(v)
        return total

    return _count(data)


def flatten(source: str | bytes | Path, separator: str = ".") -> dict[str, Any]:
    """Flatten a TOML document into a single-level dict with dotted keys.

    Nested tables are collapsed. Array-of-tables remain as lists.

    Args:
        source:    File path (str/Path) or raw bytes.
        separator: Key separator (default ".").

    Returns:
        Flat dict mapping dotted key paths to leaf values.

    Raises:
        TomlParseError / TomlInputError: On load failure.
    """
    model = load_toml(source)

    def _flatten(node: dict, prefix: str, out: dict) -> None:
        for k, v in node.items():
            key = f"{prefix}{separator}{k}" if prefix else k
            if isinstance(v, dict):
                _flatten(v, key, out)
            else:
                out[key] = v

    result: dict[str, Any] = {}
    _flatten(model["data"], "", result)
    return result


def to_env(source: str | bytes | Path, *, prefix: str = "", uppercase: bool = True) -> str:
    """Export a TOML document as environment variable assignments.

    Nested keys are joined with underscore. Only scalar values
    (str, int, float, bool) are exported; dicts and lists are skipped.

    Args:
        source:    File path (str/Path) or raw bytes.
        prefix:    Optional prefix for all variable names.
        uppercase: If True (default), convert names to UPPER_CASE.

    Returns:
        Multi-line string of KEY=VALUE pairs.

    Raises:
        TomlParseError / TomlInputError: On load failure.
    """
    flat = flatten(source, separator="_")
    lines: list[str] = []
    for k, v in sorted(flat.items()):
        if isinstance(v, (dict, list)):
            continue
        name = k
        if prefix:
            name = f"{prefix}_{name}"
        if uppercase:
            name = name.upper()
        if isinstance(v, bool):
            val = "true" if v else "false"
        elif isinstance(v, str):
            val = v
        else:
            val = str(v)
        lines.append(f"{name}={val}")
    return "\n".join(lines)


def diff_keys(source_a: str | bytes | Path, source_b: str | bytes | Path) -> list[str]:
    """Return top-level keys present in source_a but not in source_b.

    Args:
        source_a: First TOML source (file path or bytes).
        source_b: Second TOML source (file path or bytes).

    Returns:
        Sorted list of keys in A but not in B.
    """
    result_a = load_toml(source_a)
    result_b = load_toml(source_b)
    data_a = result_a.get("data", {})
    data_b = result_b.get("data", {})
    return sorted(set(data_a.keys()) - set(data_b.keys()))


def rename_key(data: dict[str, Any], old_key: str, new_key: str) -> dict[str, Any]:
    """Rename a top-level key in a TOML data dict.

    Args:
        data: Parsed TOML dict.
        old_key: Existing key name.
        new_key: New key name.

    Returns:
        New dict with the key renamed. Raises KeyError if old_key not found.
        Raises ValueError if new_key already exists.
    """
    if old_key not in data:
        raise KeyError(f"Key not found: {old_key!r}")
    if new_key in data:
        raise ValueError(f"Key already exists: {new_key!r}")
    result = {}
    for k, v in data.items():
        if k == old_key:
            result[new_key] = v
        else:
            result[k] = v
    return result


# FORMAT_FACTORY_EXECUTION: taskcard=PD-Q-001; method=QUEUE_DISPATCHED_EXECUTION; queue_item=pdrnext-q-001
def has_section(source: str | bytes | Path, section: str) -> bool:
    """Return True if the TOML source has a top-level section with the given name.

    Args:
        source: TOML string, bytes, or file path.
        section: Section name to check.

    Returns:
        True if the section exists and its value is a dict, False otherwise.
    """
    model = load_toml(source)
    raw_data = model.get("data", {})
    return isinstance(raw_data.get(section), dict)


def update_section(data: dict[str, Any], section: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Merge key/value pairs into a specific section of a TOML data dict in-memory.

    Args:
        data: Parsed TOML dict (from load_toml or similar).
        section: Top-level key identifying the section dict to update.
        updates: Key/value pairs to merge into the section.

    Returns:
        New dict with the section updated. Other sections are unchanged.
        If section does not exist, it is created.
        Raises TypeError if the existing section value is not a dict.
    """
    result = dict(data)
    existing = result.get(section, {})
    if not isinstance(existing, dict):
        raise TypeError(
            f"Section {section!r} is not a dict (got {type(existing).__name__})"
        )
    result[section] = {**existing, **updates}
    return result


def get_all_keys(source: "str | bytes | Path", separator: str = ".") -> "list[str]":
    """Return all keys in a TOML source, recursively, as dot-separated paths.

    Top-level scalar keys are returned as-is. Nested dict keys are returned
    as parent.child paths using the given separator.

    Args:
        source: TOML file path, bytes, or string content.
        separator: String to join key path segments. Default '.'.

    Returns:
        Sorted list of all key paths (strings) in the document.
    """
    model = load_toml(source)
    data = model.get("data", {}) if isinstance(model, dict) and "data" in model else model

    result: list[str] = []

    def _collect(obj: Any, prefix: str) -> None:
        if not isinstance(obj, dict):
            return
        for key, val in obj.items():
            path = f"{prefix}{separator}{key}" if prefix else key
            result.append(path)
            if isinstance(val, dict):
                _collect(val, path)

    _collect(data, "")
    return sorted(result)


def get_section_as_dict(
    source: "str | bytes | Path",
    section: str,
) -> dict:
    """Return the value of a top-level section key as a dict.

    Args:
        source: TOML string, bytes, or file path.
        section: Top-level key name to retrieve.

    Returns:
        The section value if it is a dict, or {} if not found / not a dict.
    """
    model = load_toml(source)
    data = model.get("data", model)
    value = data.get(section, {})
    if isinstance(value, dict):
        return value
    return {}


def has_any_section(source: "str | bytes | Path") -> bool:
    """Return True if the TOML document has at least one top-level section (dict value).

    Args:
        source: TOML string, bytes, or file path.

    Returns:
        True if any top-level key has a dict value, False otherwise.
    """
    model = load_toml(source)
    data = model.get("data", model)
    return any(isinstance(v, dict) for v in data.values())


def count_values_in_section(source: "str | bytes | Path", section: str) -> int:
    """Count the number of key-value pairs in a top-level TOML section.

    Args:
        source: TOML string, bytes, or file path.
        section: Top-level section name.

    Returns:
        Number of keys in the section, or 0 if section not found or not a dict.
    """
    model = load_toml(source)
    data = model.get("data", model)
    value = data.get(section, {})
    if isinstance(value, dict):
        return len(value)
    return 0


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


def count_sections_with_key(source: "str | bytes | Path", key: str) -> int:
    """Count how many top-level TOML sections contain a specific key.

    Iterates over all top-level values that are dicts (i.e., TOML sections/tables)
    and counts how many of them contain the given key as a direct child.

    Args:
        source: TOML string, bytes, or file path.
        key: The key name to search for within each section.

    Returns:
        Integer count of top-level sections that contain ``key``.
        Returns 0 if no sections exist or none contain the key.
    """
    model = load_toml(source)
    data = model.get("data", model)
    count = 0
    for v in data.values():
        if isinstance(v, dict) and key in v:
            count += 1
    return count


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


def toml_list_count(source: "str | bytes | Path") -> int:
    """Return the count of top-level keys whose values are lists."""
    model = load_toml(source)
    data = model.get("data", model)
    return sum(1 for v in data.values() if isinstance(v, list))


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


# ---------------------------------------------------------------------------
# Additional semantic analytics (r285–r315 gap closures)
# ---------------------------------------------------------------------------

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


def toml_key_count_squared(source: "str | bytes | Path") -> int:
    """Return the square of the total top-level key count."""
    n = toml_total_keys(source)
    return n * n


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

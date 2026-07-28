"""
toml_writer.py — TOML writer for format-factory-toml.

Public API:
  write_toml(data, path) — writes TOML to file
  write_toml_str(data)   — returns TOML string

Supported value types: str, int, float, bool, list (of supported types),
dict (nested tables). Raises TomlWriteError for unsupported types.

Does NOT import tomli-w or any external library.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from .exceptions import TomlError, TomlParseError, TomlWriteError


def _toml_value(val: Any, context: str = "") -> str:
    """Serialize a single TOML value to string."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return repr(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        return f'"{escaped}"'
    if isinstance(val, list):
        items = [_toml_value(v, context) for v in val]
        return "[" + ", ".join(items) + "]"
    if isinstance(val, dict):
        raise TomlWriteError(
            f"Nested dict must be written as a TOML table, not inline at {context!r}. "
            "Use a top-level key."
        )
    raise TomlWriteError(
        f"Unsupported TOML value type {type(val).__name__!r} at key {context!r}. "
        "Supported: str, int, float, bool, list, dict (top-level only)."
    )


def _write_table(data: dict, prefix: str = "") -> list[str]:
    """Recursively serialize a TOML table, returning lines."""
    lines: list[str] = []
    deferred_tables: list[tuple[str, dict]] = []

    for key, val in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict):
            deferred_tables.append((full_key, val))
        else:
            lines.append(f"{key} = {_toml_value(val, context=full_key)}")

    for table_key, table_val in deferred_tables:
        lines.append("")
        lines.append(f"[{table_key}]")
        lines.extend(_write_table(table_val, prefix=table_key))

    return lines


def write_toml_str(data: dict) -> str:
    """Serialize a dict to TOML string.

    Supports: str, int, float, bool, list (of scalar types), nested dict (tables).
    Raises TomlWriteError for unsupported types (sets, tuples, custom objects).
    """
    if not isinstance(data, dict):
        raise TomlWriteError("Top-level TOML value must be a dict")

    lines = _write_table(data)
    content = "\n".join(lines)
    if content and not content.endswith("\n"):
        content += "\n"
    return content


def write_toml(data: dict, path: str | Path) -> None:
    """Write a dict to a TOML file. Creates parent dirs as needed. UTF-8, no BOM."""
    if not path:
        raise TomlWriteError("path must not be empty")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = write_toml_str(data)
    p.write_text(content, encoding="utf-8")

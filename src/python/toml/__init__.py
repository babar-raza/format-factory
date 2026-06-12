"""
format-factory: TOML FOSS Python track.

Minimal FOSS implementation for .toml format support.
Uses stdlib tomllib (Python 3.11+) for parsing — no external dependencies.
Acquisition Gates 1-4 initiated.

FOSS track only — no commercial readiness implied.
"""

from .toml_codec import (
    TomlError,
    TomlInputError,
    TomlParseError,
    TomlWriteError,
    probe_toml,
    load_toml,
    write_toml,
    get_keys,
    roundtrip,
    get_value,
    merge_toml,
    to_json_str,
    set_value,
    list_sections,
    delete_key,
    get_section_keys,
    has_key,
    count_keys,
    flatten,
    to_env,
    diff_keys,
    rename_key,
    update_section,
    has_section,
    get_all_keys,
    get_section_as_dict,
    has_any_section,
    count_values_in_section,
    toml_string_value_count,
    toml_list_count,
    count_sections_with_key,
)

__all__ = [
    "TomlError",
    "TomlInputError",
    "TomlParseError",
    "TomlWriteError",
    "probe_toml",
    "load_toml",
    "write_toml",
    "get_keys",
    "roundtrip",
    "get_value",
    "merge_toml",
    "to_json_str",
    "set_value",
    "list_sections",
    "delete_key",
    "get_section_keys",
    "has_key",
    "count_keys",
    "flatten",
    "to_env",
    "diff_keys",
    "rename_key",
    "update_section",
    "has_section",
    "get_all_keys",
    "get_section_as_dict",
    "has_any_section",
    "count_values_in_section",
    "toml_string_value_count",
    "toml_list_count",
    "count_sections_with_key",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

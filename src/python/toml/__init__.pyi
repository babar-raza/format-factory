"""Type stubs for format-factory-toml (PQ-020)."""
from typing import Any

from toml.toml_codec import load_toml as load_toml
from toml.toml_codec import write_toml as write_toml
from toml.toml_codec import probe_toml as probe_toml
from toml.toml_codec import list_sections as list_sections
from toml.toml_codec import get_value as get_value
from toml.toml_codec import has_key as has_key
from toml.toml_codec import has_section as has_section
from toml.toml_codec import count_keys as count_keys
from toml.toml_codec import to_json_str as to_json_str
from toml.toml_codec import get_all_keys as get_all_keys
from toml.toml_codec import get_keys as get_keys
from toml.models import TomlDocument as TomlDocument

__all__: list[str]

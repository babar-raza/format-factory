"""toml.Compat — production facade layer for TOML.

Exports:
    TomlTable — facade for toml:table (SAL-TOML-00001)
    TomlKey   — facade for toml:key   (SAL-TOML-00002)
"""
from .toml_table import TomlTable
from .toml_key import TomlKey

__all__ = ["TomlTable", "TomlKey"]

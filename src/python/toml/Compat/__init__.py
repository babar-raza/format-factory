"""toml.Compat — production facade layer for TOML.

Exports:
    TomlTable — facade for toml:table (FACT-TOML-001)
    TomlKey   — facade for toml:key   (FACT-TOML-002)
"""
from .toml_table import TomlTable
from .toml_key import TomlKey

__all__ = ["TomlTable", "TomlKey"]

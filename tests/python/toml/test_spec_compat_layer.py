"""Behavioral tests for TOML spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.toml.Compat import TomlTable, TomlKey
from src.python.toml.spec.table.table import Table as SpecTable
from src.python.toml.spec.table.key import Key as SpecKey


_SAMPLE_TABLE = {"title": "Example", "owner": "Alice", "count": 42}


class TestTomlTableMetadata:
    def test_spec_qname(self):
        assert TomlTable.spec_qname == "toml:table"

    def test_spec_fact_ref(self):
        assert TomlTable.spec_fact_ref == "FACT-TOML-001"

    def test_namespace_uri_present(self):
        assert TomlTable.namespace_uri


class TestTomlTableBehavior:
    def test_instantiation(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert t is not None

    def test_keys_property(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert "title" in t.keys

    def test_key_count(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert t.key_count == 3

    def test_get_value(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert t.get("title") == "Example"

    def test_to_dict(self):
        t = TomlTable(_SAMPLE_TABLE)
        d = t.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert repr(t)

    def test_inherits_spec_class(self):
        t = TomlTable(_SAMPLE_TABLE)
        assert isinstance(t, SpecTable)


class TestTomlKeyBehavior:
    def test_instantiation(self):
        k = TomlKey("title", "Example")
        assert k is not None

    def test_spec_qname(self):
        assert TomlKey.spec_qname == "toml:key"

    def test_spec_fact_ref(self):
        assert TomlKey.spec_fact_ref == "FACT-TOML-002"

    def test_name_property(self):
        k = TomlKey("title", "Example")
        assert k.name == "title"

    def test_value_property(self):
        k = TomlKey("count", 42)
        assert k.value == 42

    def test_value_type_str(self):
        k = TomlKey("title", "Example")
        assert k.value_type == "str"

    def test_value_type_int(self):
        k = TomlKey("count", 42)
        assert k.value_type == "int"

    def test_inherits_spec_class(self):
        k = TomlKey("x", 1)
        assert isinstance(k, SpecKey)

    def test_repr_nonempty(self):
        k = TomlKey("x", 1)
        assert repr(k)

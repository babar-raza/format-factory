"""
tests/python/toml/test_r292_toml_iter_keys.py

Sprint: ff-sprint-s292-toml-key-iterator-20260626
Authority: TOML v1.0.0 specification

Tests for toml_iter_keys() in toml_key_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"


class TestTomlIterKeysImport:
    def test_importable_from_toml_key_iterator(self):
        from toml.toml_key_iterator import toml_iter_keys
        assert callable(toml_iter_keys)

    def test_importable_from_package(self):
        import toml as toml
        assert hasattr(toml, "toml_iter_keys")


class TestTomlIterKeysOutput:
    def test_returns_iterator(self):
        from toml.toml_key_iterator import toml_iter_keys
        result = toml_iter_keys(str(_SAMPLE))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_keys(self):
        from toml.toml_key_iterator import toml_iter_keys
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert len(keys) >= 1

    def test_key_type_is_spec_key(self):
        from toml.toml_key_iterator import toml_iter_keys
        from toml.spec.table.key import Key
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert all(isinstance(k, Key) for k in keys)

    def test_key_has_spec_qname(self):
        from toml.toml_key_iterator import toml_iter_keys
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert all(hasattr(k, "spec_qname") for k in keys)

    def test_key_qname_value(self):
        from toml.toml_key_iterator import toml_iter_keys
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert all(k.spec_qname == "toml:key" for k in keys)

    def test_key_name_is_string(self):
        from toml.toml_key_iterator import toml_iter_keys
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert all(isinstance(k.name, str) for k in keys)

    def test_key_value_type(self):
        from toml.toml_key_iterator import toml_iter_keys
        keys = list(toml_iter_keys(str(_SAMPLE)))
        assert all(isinstance(k.value_type, str) for k in keys)

    def test_consistent(self):
        from toml.toml_key_iterator import toml_iter_keys
        r1 = [k.name for k in toml_iter_keys(str(_SAMPLE))]
        r2 = [k.name for k in toml_iter_keys(str(_SAMPLE))]
        assert r1 == r2

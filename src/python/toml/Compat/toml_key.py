"""TomlKey — production facade for toml:key."""
from __future__ import annotations
from ..spec.table.key import Key as _SpecKey


class TomlKey(_SpecKey):
    """Production facade for toml:key."""
    spec_qname = "toml:key"
    spec_fact_ref = "FACT-TOML-002"
    namespace_uri = "urn:format:toml:1.0"

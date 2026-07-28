"""TomlKey — production facade for toml:key."""
from __future__ import annotations
from typing import ClassVar
from ..spec.table.key import Key as _SpecKey


class TomlKey(_SpecKey):
    """Production facade for toml:key."""
    spec_qname: ClassVar[str] = "toml:key"
    spec_fact_ref: ClassVar[str] = "SAL-TOML-00002"
    namespace_uri: ClassVar[str] = "urn:format:toml:1.0"

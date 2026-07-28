"""TomlTable — production facade for toml:table."""
from __future__ import annotations
from typing import ClassVar
from ..spec.table.table import Table as _SpecTable


class TomlTable(_SpecTable):
    """Production facade for toml:table."""
    spec_qname: ClassVar[str] = "toml:table"
    spec_fact_ref: ClassVar[str] = "SAL-TOML-00001"
    namespace_uri: ClassVar[str] = "urn:format:toml:1.0"

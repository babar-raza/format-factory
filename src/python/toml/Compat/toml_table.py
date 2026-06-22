"""TomlTable — production facade for toml:table."""
from __future__ import annotations
from ..spec.table.table import Table as _SpecTable


class TomlTable(_SpecTable):
    """Production facade for toml:table."""
    spec_qname = "toml:table"
    spec_fact_ref = "FACT-TOML-001"
    namespace_uri = "urn:format:toml:1.0"

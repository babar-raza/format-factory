"""NdjsonField — production facade for ndjson:field."""
from __future__ import annotations
from typing import ClassVar
from ..spec.record.field import Field as _SpecField


class NdjsonField(_SpecField):
    """Production facade for ndjson:field."""
    spec_qname: ClassVar[str] = "ndjson:field"
    spec_fact_ref: ClassVar[str] = "SAL-NDJSON-00002"
    namespace_uri: ClassVar[str] = "urn:format:ndjson:1.0"

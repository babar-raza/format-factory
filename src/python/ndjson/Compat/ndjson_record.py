"""NdjsonRecord — production facade for ndjson:record."""
from __future__ import annotations
from typing import ClassVar
from ..spec.record.record import Record as _SpecRecord


class NdjsonRecord(_SpecRecord):
    """Production facade for ndjson:record."""
    spec_qname: ClassVar[str] = "ndjson:record"
    spec_fact_ref: ClassVar[str] = "SAL-NDJSON-00001"
    namespace_uri: ClassVar[str] = "urn:format:ndjson:1.0"

"""NdjsonRecord — production facade for ndjson:record."""
from __future__ import annotations
from ..spec.record.record import Record as _SpecRecord


class NdjsonRecord(_SpecRecord):
    """Production facade for ndjson:record."""
    spec_qname = "ndjson:record"
    spec_fact_ref = "FACT-NDJSON-001"
    namespace_uri = "urn:format:ndjson:1.0"

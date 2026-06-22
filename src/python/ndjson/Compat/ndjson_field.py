"""NdjsonField — production facade for ndjson:field."""
from __future__ import annotations
from ..spec.record.field import Field as _SpecField


class NdjsonField(_SpecField):
    """Production facade for ndjson:field."""
    spec_qname = "ndjson:field"
    spec_fact_ref = "FACT-NDJSON-002"
    namespace_uri = "urn:format:ndjson:1.0"

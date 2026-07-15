"""XliffSegment — production facade for xliff:segment."""
from __future__ import annotations
from ..spec.file.segment import Segment as _SpecSegment


class XliffSegment(_SpecSegment):
    """Production facade for xliff:segment."""
    spec_qname = "xliff:segment"
    spec_fact_ref = "FACT-XLIFF-002"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"

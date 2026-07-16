"""XliffSegment — production facade for xliff:segment."""
from __future__ import annotations
from typing import ClassVar
from ..spec.file.segment import Segment as _SpecSegment


class XliffSegment(_SpecSegment):
    """Production facade for xliff:segment."""
    spec_qname: ClassVar[str] = "xliff:segment"
    spec_fact_ref: ClassVar[str] = "FACT-XLIFF-002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:xliff:document:2.0"

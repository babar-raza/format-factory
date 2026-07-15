"""XliffUnit — production facade for xliff:unit."""
from __future__ import annotations
from ..spec.file.unit import Unit as _SpecUnit


class XliffUnit(_SpecUnit):
    """Production facade for xliff:unit."""
    spec_qname = "xliff:unit"
    spec_fact_ref = "FACT-XLIFF-002"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"

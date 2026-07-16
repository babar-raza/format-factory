"""XliffUnit — production facade for xliff:unit."""
from __future__ import annotations
from typing import ClassVar
from ..spec.file.unit import Unit as _SpecUnit


class XliffUnit(_SpecUnit):
    """Production facade for xliff:unit."""
    spec_qname: ClassVar[str] = "xliff:unit"
    spec_fact_ref: ClassVar[str] = "FACT-XLIFF-002"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:xliff:document:2.0"

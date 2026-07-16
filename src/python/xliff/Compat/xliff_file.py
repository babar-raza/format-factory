"""XliffFile — production facade for xliff:file."""
from __future__ import annotations
from typing import ClassVar
from ..spec.file.file import File as _SpecFile


class XliffFile(_SpecFile):
    """Production facade for xliff:file."""
    spec_qname: ClassVar[str] = "xliff:file"
    spec_fact_ref: ClassVar[str] = "FACT-XLIFF-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:xliff:document:2.0"

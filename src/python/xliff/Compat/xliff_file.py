"""XliffFile — production facade for xliff:file."""
from __future__ import annotations
from ..spec.file.file import File as _SpecFile


class XliffFile(_SpecFile):
    """Production facade for xliff:file."""
    spec_qname = "xliff:file"
    spec_fact_ref = "FACT-XLIFF-001"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"

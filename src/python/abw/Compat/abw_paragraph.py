"""AbwParagraph — production facade for abw:p.

Spec authority: abw:p
Spec ref: AbiWord AWML 1.0 — paragraph block element
Fact ref: FACT-ABW-003
Canonical spec class: src/python/abw/spec/document/paragraph.py::Paragraph
"""
from __future__ import annotations

from ..spec.document.paragraph import Paragraph as _SpecParagraph


class AbwParagraph(_SpecParagraph):
    """Production facade for abw:p (AbiWord paragraph element).

    Inherits all behavioral properties from the canonical spec class.
    Primary public API entry point for paragraph-level access.
    """

    spec_qname = "abiword:p"
    spec_fact_ref = "FACT-ABW-003"
    namespace_uri = "http://www.abisource.com/awml/"

    def upper(self) -> str:
        """Return paragraph text in uppercase."""
        return self._text.upper()

    def lower(self) -> str:
        """Return paragraph text in lowercase."""
        return self._text.lower()

    def contains(self, substr: str, case_sensitive: bool = True) -> bool:
        """Return True if paragraph text contains the given substring."""
        if case_sensitive:
            return substr in self._text
        return substr.lower() in self._text.lower()

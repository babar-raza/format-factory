"""odt.Compat — production facade layer for ODT (Gate 11 P-ARCH-001).

Exports:
    OdtDocument  — facade for office:document (FACT-ODT-EX-0029)
    OdtParagraph — facade for text:p          (FACT-ODT-EX-0094)
    OdtHeading   — facade for text:h          (FACT-ODT-EX-0094)
"""
from .odt_document import OdtDocument
from .odt_paragraph import OdtParagraph
from .odt_heading import OdtHeading

__all__ = ["OdtDocument", "OdtParagraph", "OdtHeading"]

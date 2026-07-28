"""odt.Compat — production facade layer for ODT (Gate 11 P-ARCH-001).

Exports:
    OdtDocument  — facade for office:document (SAL-ODT-00028)
    OdtParagraph — facade for text:p          (SAL-ODT-00091)
    OdtHeading   — facade for text:h          (SAL-ODT-00091)
"""
from .odt_document import OdtDocument
from .odt_paragraph import OdtParagraph
from .odt_heading import OdtHeading

__all__ = ["OdtDocument", "OdtParagraph", "OdtHeading"]

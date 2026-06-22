"""fodp.Compat — production facade layer for FODP (Gate 11 P-ARCH-001).

Exports:
    FodpDocument  — facade for office:document (FACT-FODP-EX-0029)
    FodpPage      — facade for draw:page       (FACT-FODP-EX-0417)
"""
from .fodp_document import FodpDocument
from .fodp_page import FodpPage

__all__ = ["FodpDocument", "FodpPage"]

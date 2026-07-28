"""fodp.Compat — production facade layer for FODP (Gate 11 P-ARCH-001).

Exports:
    FodpDocument  — facade for office:document (SAL-FODP-00031)
    FodpPage      — facade for draw:page       (SAL-FODP-00414)
"""
from .fodp_document import FodpDocument
from .fodp_page import FodpPage

__all__ = ["FodpDocument", "FodpPage"]

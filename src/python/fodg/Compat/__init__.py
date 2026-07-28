"""fodg.Compat — production facade layer for FODG (Gate 11 P-ARCH-001).

Exports:
    FodgDocument  — facade for office:document (SAL-FODG-00031)
    FodgPage      — facade for draw:page       (SAL-FODG-00414)
"""
from .fodg_document import FodgDocument
from .fodg_page import FodgPage

__all__ = ["FodgDocument", "FodgPage"]

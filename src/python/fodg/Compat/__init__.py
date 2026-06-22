"""fodg.Compat — production facade layer for FODG (Gate 11 P-ARCH-001).

Exports:
    FodgDocument  — facade for office:document (FACT-FODG-EX-0029)
    FodgPage      — facade for draw:page       (FACT-FODG-EX-0417)
"""
from .fodg_document import FodgDocument
from .fodg_page import FodgPage

__all__ = ["FodgDocument", "FodgPage"]

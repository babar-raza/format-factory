"""abw.Compat — production facade layer for ABW (Gate 11 P-ARCH-001).

Exports:
    AbwDocument   — facade for abw:abiword  (SAL-ABW-00001)
    AbwParagraph  — facade for abw:p        (SAL-ABW-00003)
"""
from .abw_document import AbwDocument
from .abw_paragraph import AbwParagraph

__all__ = ["AbwDocument", "AbwParagraph"]

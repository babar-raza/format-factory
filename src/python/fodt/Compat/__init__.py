"""fodt.Compat — production facade layer for FODT (Gate 11 P-ARCH-001).

Exports:
    FodtDocument    — facade for office:document (FACT-FODT-001)
    FodtParagraph   — facade for text:p          (FACT-FODT-003)
    FodtHeading     — facade for text:h          (FACT-FODT-004)
    FodtSpan        — facade for text:span       (FACT-FODT-006)
    FodtTableCell   — facade for table:table-cell (FACT-FODT-007)
"""
from .fodt_document import FodtDocument
from .fodt_paragraph import FodtParagraph
from .fodt_heading import FodtHeading
from .fodt_span import FodtSpan
from .fodt_table_cell import FodtTableCell

__all__ = [
    "FodtDocument",
    "FodtParagraph",
    "FodtHeading",
    "FodtSpan",
    "FodtTableCell",
]

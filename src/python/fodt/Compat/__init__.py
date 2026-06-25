"""fodt.Compat -- production facade layer for FODT (Gate 11 P-ARCH-001).

Exports:
    FodtDocument   -- facade for office:document  (FACT-FODT-001)
    FodtParagraph  -- facade for text:p           (FACT-FODT-003)
    FodtHeading    -- facade for text:h           (FACT-FODT-004)
    FodtSpan       -- facade for text:span        (FACT-FODT-006)
    FodtTableCell  -- facade for table:table-cell (FACT-FODT-007)
    FodtList       -- facade for text:list        (FACT-FODT-005)
    FodtListItem   -- facade for text:list-item   (FACT-FODT-005)
    FodtTable      -- facade for table:table      (FACT-FODT-007)
    FodtTableRow   -- facade for table:table-row  (FACT-FODT-007)
"""
from .fodt_document import FodtDocument
from .fodt_paragraph import FodtParagraph
from .fodt_heading import FodtHeading
from .fodt_span import FodtSpan
from .fodt_table_cell import FodtTableCell
from .fodt_list import FodtList
from .fodt_list_item import FodtListItem
from .fodt_table import FodtTable
from .fodt_table_row import FodtTableRow

__all__ = [
    "FodtDocument",
    "FodtParagraph",
    "FodtHeading",
    "FodtSpan",
    "FodtTableCell",
    "FodtList",
    "FodtListItem",
    "FodtTable",
    "FodtTableRow",
]

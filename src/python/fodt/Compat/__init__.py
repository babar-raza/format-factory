"""fodt.Compat -- production facade layer for FODT (Gate 11 P-ARCH-001).

Exports:
    FodtDocument   -- facade for office:document  (SAL-FODT-00001)
    FodtParagraph  -- facade for text:p           (SAL-FODT-00003)
    FodtHeading    -- facade for text:h           (SAL-FODT-00004)
    FodtSpan       -- facade for text:span        (SAL-FODT-00006)
    FodtTableCell  -- facade for table:table-cell (SAL-FODT-00007)
    FodtList       -- facade for text:list        (SAL-FODT-00005)
    FodtListItem   -- facade for text:list-item   (SAL-FODT-00005)
    FodtTable      -- facade for table:table      (SAL-FODT-00007)
    FodtTableRow   -- facade for table:table-row  (SAL-FODT-00007)
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

"""fods.Compat — Production facade layer for FODS spec elements (Gate 11 P-ARCH-001)."""
from .fods_document import FodsDocument
from .fods_sheet import FodsSheet
from .fods_cell import FodsCell
from .fods_body import FodsBody
from .fods_spreadsheet import FodsSpreadsheet
from .fods_table_row import FodsTableRow
from .fods_covered_cell import FodsCoveredCell
from .fods_paragraph import FodsParagraph
from .fods_span import FodsSpan
from .fods_automatic_styles import FodsAutomaticStyles
from .fods_style import FodsStyle
from .fods_date_style import FodsDateStyle


def get_spec_qname(obj) -> str | None:
    """Return the ODF QName for a FODS model object, or None if not annotated."""
    return getattr(obj, "spec_qname", None)


__all__ = [
    "FodsDocument", "FodsSheet", "FodsCell",
    "FodsBody", "FodsSpreadsheet", "FodsTableRow", "FodsCoveredCell",
    "FodsParagraph", "FodsSpan", "FodsAutomaticStyles", "FodsStyle", "FodsDateStyle",
    "get_spec_qname",
]

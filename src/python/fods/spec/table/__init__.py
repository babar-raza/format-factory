"""fods.spec.table — table:* canonical spec classes."""
from .table import Table
from .table_row import TableRow
from .table_cell import TableCell
from .table_column import TableColumn
from .table_header_rows import TableHeaderRows
from .covered_table_cell import CoveredTableCell

__all__ = ["Table", "TableRow", "TableCell", "TableColumn", "TableHeaderRows", "CoveredTableCell"]

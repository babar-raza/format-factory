"""gnumeric.spec — canonical spec authority classes for Gnumeric."""
from .workbook.workbook import Workbook
from .workbook.sheet import Sheet

__all__ = ["Workbook", "Sheet"]

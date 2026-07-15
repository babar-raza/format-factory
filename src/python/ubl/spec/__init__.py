"""ubl.spec — canonical spec authority classes for UBL."""
from .document.invoice import Invoice
from .document.order import Order
from .document.line_item import LineItem

__all__ = ["Invoice", "Order", "LineItem"]

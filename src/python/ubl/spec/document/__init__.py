"""ubl.spec.document — document domain spec classes for UBL."""
from .invoice import Invoice
from .order import Order
from .line_item import LineItem

__all__ = ["Invoice", "Order", "LineItem"]

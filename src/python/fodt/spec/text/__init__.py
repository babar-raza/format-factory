"""fodt.spec.text — text:* canonical spec classes."""
from .paragraph import Paragraph
from .heading import Heading
from .span import Span
from .list_ import List
from .list_item import ListItem

__all__ = ["Paragraph", "Heading", "Span", "List", "ListItem"]

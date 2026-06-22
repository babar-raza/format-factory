"""fodp.spec — canonical spec authority classes for FODP (ODF Presentation)."""
from .office.document import Document
from .draw.page import Page

__all__ = ["Document", "Page"]

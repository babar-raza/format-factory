"""odt.spec — canonical spec authority classes for ODT (ODF Text Document)."""
from .office.document import Document
from .text.paragraph import Paragraph
from .text.heading import Heading

__all__ = ["Document", "Paragraph", "Heading"]

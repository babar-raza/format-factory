"""abw.spec — spec authority classes for AbiWord AWML elements."""
from .document.document import Document
from .document.section import Section
from .document.paragraph import Paragraph

__all__ = ["Document", "Section", "Paragraph"]

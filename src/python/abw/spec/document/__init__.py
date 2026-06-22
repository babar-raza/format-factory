"""abw.spec.document — canonical spec classes for ABW document elements."""
from .document import Document
from .section import Section
from .paragraph import Paragraph
from .char_run import CharRun
from .field import Field

__all__ = ["Document", "Section", "Paragraph", "CharRun", "Field"]

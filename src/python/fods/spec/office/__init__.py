"""fods.spec.office — office:* canonical spec classes."""
from .document import Document
from .body import Body
from .spreadsheet import Spreadsheet
from .automatic_styles import AutomaticStyles

__all__ = ["Document", "Body", "Spreadsheet", "AutomaticStyles"]

"""xliff.spec — canonical spec authority classes for XLIFF."""
from .file.file import File
from .file.unit import Unit
from .file.segment import Segment

__all__ = ["File", "Unit", "Segment"]

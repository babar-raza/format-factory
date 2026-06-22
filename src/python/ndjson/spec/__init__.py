"""ndjson.spec — canonical spec authority classes for NDJSON."""
from .record.record import Record
from .record.field import Field

__all__ = ["Record", "Field"]

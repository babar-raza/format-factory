"""toml.spec — canonical spec authority classes for TOML."""
from .table.table import Table
from .table.key import Key

__all__ = ["Table", "Key"]

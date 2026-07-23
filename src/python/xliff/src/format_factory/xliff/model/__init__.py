"""XLIFF core and mixed-content models."""

from .document import (
    ExtensionNode,
    Group,
    Note,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
)
from .inline import InlineElement, InlineNode, flatten_inline_content

__all__ = [
    "ExtensionNode",
    "Group",
    "InlineElement",
    "InlineNode",
    "Note",
    "Segment",
    "Unit",
    "XliffDocument",
    "XliffFile",
    "flatten_inline_content",
]

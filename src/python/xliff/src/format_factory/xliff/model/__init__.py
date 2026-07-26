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
from .segmentation import SegmentMapping, join_segments, split_segment

__all__ = [
    "ExtensionNode",
    "Group",
    "InlineElement",
    "InlineNode",
    "Note",
    "SegmentMapping",
    "Segment",
    "Unit",
    "XliffDocument",
    "XliffFile",
    "flatten_inline_content",
    "join_segments",
    "split_segment",
]

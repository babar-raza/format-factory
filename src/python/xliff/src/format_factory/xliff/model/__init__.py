"""XLIFF core and mixed-content models."""

from .document import (
    DataElement,
    ExtensionNode,
    Group,
    Note,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    effective_xml_space,
)
from .inline import InlineElement, InlineNode, flatten_inline_content
from .segmentation import SegmentMapping, join_segments, split_segment
from .text_editing import copy_source_to_target, replace_text_slots, text_slots

__all__ = [
    "DataElement",
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
    "copy_source_to_target",
    "effective_xml_space",
    "flatten_inline_content",
    "join_segments",
    "replace_text_slots",
    "split_segment",
    "text_slots",
]

"""Token-aware XLIFF source and target editing."""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from ..errors import XliffValidationError
from .document import Segment
from .inline import InlineElement, InlineNode, flatten_inline_content

_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _clone_inline(content: Sequence[InlineNode]) -> list[InlineNode]:
    copied: list[InlineNode] = []
    for node in content:
        if isinstance(node, str):
            copied.append(node)
        else:
            copied.append(
                InlineElement(
                    tag=node.tag,
                    attributes=dict(node.attributes),
                    content=_clone_inline(node.content),
                    tail=node.tail,
                )
            )
    return copied


def text_slots(content: Sequence[InlineNode]) -> tuple[str, ...]:
    """Return editable text leaves in deterministic document order."""

    values: list[str] = []
    for node in content:
        if isinstance(node, str):
            values.append(node)
        else:
            values.extend(text_slots(node.content))
            if node.tail:
                values.append(node.tail)
    return tuple(values)


def _replace_slots(content: list[InlineNode], values: Iterator[str]) -> None:
    for index, node in enumerate(content):
        if isinstance(node, str):
            content[index] = next(values)
        else:
            _replace_slots(node.content, values)
            if node.tail:
                node.tail = next(values)


def replace_text_slots(
    segment: Segment, values: Sequence[str], *, target: bool = True
) -> None:
    """Replace exactly the text leaves of a source or existing target."""

    content = segment.target if target else segment.source
    if content is None:
        raise XliffValidationError("cannot edit target text before creating a target")
    expected = text_slots(content)
    if len(values) != len(expected):
        raise XliffValidationError(
            f"expected {len(expected)} text slots, received {len(values)}"
        )
    if any(not isinstance(value, str) for value in values):
        raise TypeError("text slot values must be strings")
    _replace_slots(content, iter(values))


def copy_source_to_target(
    segment: Segment,
    *,
    code_copy_policy: str = "all",
    target_language: str | None = None,
) -> None:
    """Create a target from source under an explicit inline-code policy.

    ``all`` copies the complete token tree.  ``none`` creates a single plain
    text target and explicitly discards source code structure.  XML whitespace
    behavior is retained in both cases; target language is never copied from
    source because that would be semantically incorrect.
    """

    if segment.target is not None:
        raise XliffValidationError("target already exists; edit its text slots instead")
    if code_copy_policy == "all":
        segment.target = _clone_inline(segment.source)
    elif code_copy_policy == "none":
        segment.target = [flatten_inline_content(segment.source)]
    else:
        raise XliffValidationError("code_copy_policy must be 'all' or 'none'")
    segment.target_attributes = {
        key: value
        for key, value in segment.source_attributes.items()
        if key == _XML_SPACE
    }
    if target_language:
        segment.target_attributes[_XML_LANG] = target_language


__all__ = ["copy_source_to_target", "replace_text_slots", "text_slots"]

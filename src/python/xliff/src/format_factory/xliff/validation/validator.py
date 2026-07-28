"""Semantic XLIFF core validation diagnostics."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter

from format_factory.core import Diagnostic, ResourceLimits, ValidationReport

from ..codec import SUPPORTED_VERSIONS
from ..model import (
    ExtensionNode,
    Group,
    InlineElement,
    InlineNode,
    Segment,
    Unit,
    XliffDocument,
)

_STATES = frozenset({"", "initial", "translated", "reviewed", "final"})
_TARGET_REQUIRED_STATES = frozenset({"translated", "reviewed", "final"})


def _inline_elements(content: list[InlineNode]) -> list[InlineElement]:
    result: list[InlineElement] = []
    for node in content:
        if isinstance(node, InlineElement):
            result.append(node)
            result.extend(_inline_elements(node.content))
    return result


def _validate_inline(segment: Segment, diagnostics: list[Diagnostic]) -> None:
    for label, content in (("source", segment.source), ("target", segment.target or [])):
        elements = _inline_elements(content)
        ids = [value.id for value in elements if value.id]
        duplicates = sorted(
            key for key, count in Counter(ids).items() if count > 1
        )
        for duplicate in duplicates:
            diagnostics.append(
                Diagnostic(
                    "xliff.inline.id.duplicate",
                    f"duplicate inline id {duplicate!r} in segment {segment.id!r} {label}",
                )
            )
        starts = {value.id for value in elements if value.tag == "sc" and value.id}
        for value in elements:
            if value.tag == "ec":
                start_ref = value.attributes.get("startRef")
                if not start_ref or start_ref not in starts:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.ec.unpaired",
                            f"ec in segment {segment.id!r} has no matching sc",
                        )
                    )


def _extension_well_formed(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError as exc:
        diagnostics.append(
            Diagnostic("xliff.extension.malformed", f"malformed extension: {exc}")
        )
        return
    if element.tag != extension.tag:
        diagnostics.append(
            Diagnostic(
                "xliff.extension.tag_mismatch",
                "extension tag does not match its preserved XML",
            )
        )


def _walk_group(group: Group) -> list[Unit]:
    return list(group.iter_units())


def validate(
    value: XliffDocument,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Validate core model invariants without resolving external references."""

    del limits
    diagnostics: list[Diagnostic] = []
    selected = profile or value.version
    if selected not in SUPPORTED_VERSIONS:
        diagnostics.append(
            Diagnostic(
                "xliff.profile.unsupported",
                f"stable profile does not support XLIFF {selected!r}",
            )
        )
    if not value.source_language:
        diagnostics.append(Diagnostic("xliff.srcLang.required", "srcLang is required"))
    if not value.files:
        diagnostics.append(Diagnostic("xliff.file.required", "at least one file is required"))
    file_ids = [item.id for item in value.files]
    for duplicate in sorted(
        key for key, count in Counter(file_ids).items() if key and count > 1
    ):
        diagnostics.append(
            Diagnostic("xliff.file.id.duplicate", f"duplicate file id {duplicate!r}")
        )
    for file in value.files:
        if not file.id:
            diagnostics.append(Diagnostic("xliff.file.id.required", "file id is required"))
        units = list(file.iter_units())
        unit_ids = [unit.id for unit in units]
        for duplicate in sorted(
            key for key, count in Counter(unit_ids).items() if key and count > 1
        ):
            diagnostics.append(
                Diagnostic(
                    "xliff.unit.id.duplicate",
                    f"duplicate unit id {duplicate!r} in file {file.id!r}",
                )
            )
        for unit in units:
            if not unit.id:
                diagnostics.append(
                    Diagnostic("xliff.unit.id.required", "unit id is required")
                )
            segment_ids = [segment.id for segment in unit.segments]
            for duplicate in sorted(
                key
                for key, count in Counter(segment_ids).items()
                if key and count > 1
            ):
                diagnostics.append(
                    Diagnostic(
                        "xliff.segment.id.duplicate",
                        f"duplicate segment id {duplicate!r} in unit {unit.id!r}",
                    )
                )
            for segment in unit.segments:
                if segment.kind == "segment" and not segment.id:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.segment.id.required",
                            f"segment in unit {unit.id!r} requires an id",
                        )
                    )
                if segment.state not in _STATES:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.segment.state.invalid",
                            f"invalid segment state {segment.state!r}",
                        )
                    )
                elif (
                    segment.state in _TARGET_REQUIRED_STATES
                    and segment.target is None
                ):
                    diagnostics.append(
                        Diagnostic(
                            "xliff.segment.state.target_required",
                            f"segment {segment.id!r} in state {segment.state!r} requires a target",
                        )
                    )
                _validate_inline(segment, diagnostics)
                for segment_extension in segment.extensions:
                    _extension_well_formed(segment_extension, diagnostics)
        for file_child in file.children:
            if isinstance(file_child, ExtensionNode):
                _extension_well_formed(file_child, diagnostics)
            elif isinstance(file_child, Group):
                for group_unit in _walk_group(file_child):
                    for group_child in group_unit.children:
                        if isinstance(group_child, ExtensionNode):
                            _extension_well_formed(group_child, diagnostics)
    for root_child in value.children:
        if isinstance(root_child, ExtensionNode):
            _extension_well_formed(root_child, diagnostics)
    return ValidationReport(diagnostics)

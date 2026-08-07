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
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def _language_compatible(enclosing: str, declared: str, *, exact_only: bool) -> bool:
    """Whether `declared` satisfies the enclosing srcLang/trgLang.

    XLIFF 2.0 requires exact equality; XLIFF 2.1's F4T Schematron additionally
    accepts a more-specific tag (e.g. declared "en-US" under enclosing "en").
    Comparison is case-insensitive per BCP 47.
    """
    enclosing_lower = enclosing.lower()
    declared_lower = declared.lower()
    if declared_lower == enclosing_lower:
        return True
    if exact_only:
        return False
    return declared_lower.startswith(enclosing_lower + "-")


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
        seen_starts: set[str] = set()
        for value in elements:
            if value.tag == "sc" and value.id:
                seen_starts.add(value.id)
            elif value.tag == "ec":
                start_ref = value.attributes.get("startRef")
                if not start_ref or start_ref not in starts:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.ec.unpaired",
                            f"ec in segment {segment.id!r} has no matching sc",
                        )
                    )
                elif start_ref not in seen_starts:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.ec.out_of_order",
                            f"ec in segment {segment.id!r} {label} closes "
                            f"{start_ref!r} before its sc opens",
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


def _iter_groups(children: list[Group | Unit | ExtensionNode]) -> list[Group]:
    """Every Group anywhere in `children`, at any nesting depth.

    "When used in <group> elements: The value MUST be unique among all
    <group> id attribute values within the enclosing <file> element" --
    the scope is the whole file, not just immediate siblings, so this
    flattens nested groups the same way file.iter_units() already does
    for units.
    """
    groups: list[Group] = []
    for child in children:
        if isinstance(child, Group):
            groups.append(child)
            groups.extend(_iter_groups(child.children))
    return groups


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
        group_ids = [group.id for group in _iter_groups(file.children)]
        for duplicate in sorted(
            key for key, count in Counter(group_ids).items() if key and count > 1
        ):
            diagnostics.append(
                Diagnostic(
                    "xliff.group.id.duplicate",
                    f"duplicate group id {duplicate!r} in file {file.id!r}",
                )
            )
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
            if not unit.segments:
                diagnostics.append(
                    Diagnostic(
                        "xliff.unit.segment.required",
                        f"unit {unit.id!r} must contain at least one segment or ignorable",
                    )
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
                exact_only = selected == "2.0"
                source_lang = segment.source_attributes.get(_XML_LANG)
                if (
                    source_lang
                    and value.source_language
                    and not _language_compatible(
                        value.source_language, source_lang, exact_only=exact_only
                    )
                ):
                    diagnostics.append(
                        Diagnostic(
                            "xliff.segment.source.lang.incompatible",
                            f"segment {segment.id!r} source xml:lang {source_lang!r} "
                            f"is incompatible with srcLang {value.source_language!r}",
                        )
                    )
                target_lang = segment.target_attributes.get(_XML_LANG)
                if (
                    target_lang
                    and value.target_language
                    and not _language_compatible(
                        value.target_language, target_lang, exact_only=exact_only
                    )
                ):
                    diagnostics.append(
                        Diagnostic(
                            "xliff.segment.target.lang.incompatible",
                            f"segment {segment.id!r} target xml:lang {target_lang!r} "
                            f"is incompatible with trgLang {value.target_language!r}",
                        )
                    )
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

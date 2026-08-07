"""Semantic XLIFF core validation diagnostics."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter

from format_factory.core import Diagnostic, ResourceLimits, ValidationReport

from ..codec import SUPPORTED_VERSIONS, XLIFF_NAMESPACE
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

_METADATA_NAMESPACE = "urn:oasis:names:tc:xliff:metadata:2.0"
_METADATA_QNAME = f"{{{_METADATA_NAMESPACE}}}metadata"
_METAGROUP_QNAME = f"{{{_METADATA_NAMESPACE}}}metaGroup"
_META_QNAME = f"{{{_METADATA_NAMESPACE}}}meta"

_RESOURCE_DATA_NAMESPACE = "urn:oasis:names:tc:xliff:resourcedata:2.0"
_RESOURCE_DATA_QNAME = f"{{{_RESOURCE_DATA_NAMESPACE}}}resourceData"
_RESOURCE_REFERENCE_QNAME = f"{{{_RESOURCE_DATA_NAMESPACE}}}reference"

_MATCHES_NAMESPACE = "urn:oasis:names:tc:xliff:matches:2.0"
_MATCHES_QNAME = f"{{{_MATCHES_NAMESPACE}}}matches"
_MATCH_QNAME = f"{{{_MATCHES_NAMESPACE}}}match"
_CORE_SOURCE_QNAME = f"{{{XLIFF_NAMESPACE}}}source"
_CORE_TARGET_QNAME = f"{{{XLIFF_NAMESPACE}}}target"


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


def _isolated_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF Core start-code isolation, 2.1 schematron patterns F5S/F5T
    plus the "no otherwise" direction of the same rule) An sc's isolated
    attribute must be set to yes if and only if the ec element corresponding
    to it (matched by startRef against this sc's id) is not present anywhere
    in the same unit -- checked separately for source and target content,
    since the schematron scopes each check to one content type. "no" is the
    schema default when the attribute is absent.

    This scans every segment/ignorable in the unit (not just one), matching
    the schematron's ``ancestor::xlf:unit//xlf:ec[...]`` scope. The
    pre-existing, per-segment sc/ec pairing check in ``_validate_inline``
    (``xliff.inline.ec.unpaired``) is a separate, narrower check that does
    not look across segment boundaries within a unit; a genuinely valid,
    non-isolated sc/ec pair split across two segments of the same unit --
    which the spec explicitly permits -- would still trip that older,
    unit-unaware check today. That is a distinct, pre-existing limitation,
    not something this function introduces or silently repairs.
    """

    for label in ("source", "target"):
        starts: list[InlineElement] = []
        end_refs: set[str] = set()
        for segment in unit.segments:
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                if element.tag == "sc" and element.id:
                    starts.append(element)
                elif element.tag == "ec":
                    start_ref = element.attributes.get("startRef")
                    if start_ref:
                        end_refs.add(start_ref)
        for sc in starts:
            isolated = sc.attributes.get("isolated", "no")
            has_matching_ec = sc.id in end_refs
            if isolated == "yes" and has_matching_ec:
                diagnostics.append(
                    Diagnostic(
                        "xliff.inline.isolated.unexpected_ec",
                        f"sc {sc.id!r} in unit {unit.id!r} {label} is isolated='yes' "
                        f"but a matching ec exists within the same unit",
                    )
                )
            elif isolated != "yes" and not has_matching_ec:
                diagnostics.append(
                    Diagnostic(
                        "xliff.inline.isolated.missing_ec",
                        f"sc {sc.id!r} in unit {unit.id!r} {label} is not isolated "
                        f"but no matching ec exists within the same unit",
                    )
                )


def _data_ref_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF Core original data references, 2.1 schematron patterns F15/
    F16S/F16T/F17S/F17T) Every dataRef/dataRefStart/dataRefEnd attribute on
    an inline element must reference the id of a `<data>` element within
    the same unit's `<originalData>`; a pc's dataRefStart and dataRefEnd
    must be used as a pair (one present without the other is invalid),
    matching the pinned schematron's own assertions exactly, checked
    separately per content type (source/target)."""

    data_ids = {value.id for value in unit.original_data if value.id}
    for label in ("source", "target"):
        for segment in unit.segments:
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                data_ref = element.attributes.get("dataRef")
                if data_ref is not None and data_ref not in data_ids:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.dataRef.unresolved",
                            f"{element.tag} {element.id!r} in unit {unit.id!r} {label} "
                            f"has dataRef={data_ref!r}, which does not match any data id",
                        )
                    )
                start_ref = element.attributes.get("dataRefStart")
                end_ref = element.attributes.get("dataRefEnd")
                if start_ref is not None and start_ref not in data_ids:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.dataRefStart.unresolved",
                            f"{element.tag} {element.id!r} in unit {unit.id!r} {label} "
                            f"has dataRefStart={start_ref!r}, which does not match any data id",
                        )
                    )
                if end_ref is not None and end_ref not in data_ids:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.dataRefEnd.unresolved",
                            f"{element.tag} {element.id!r} in unit {unit.id!r} {label} "
                            f"has dataRefEnd={end_ref!r}, which does not match any data id",
                        )
                    )
                if (start_ref is not None) != (end_ref is not None):
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.dataRef.unpaired",
                            f"{element.tag} {element.id!r} in unit {unit.id!r} {label} "
                            f"must use dataRefStart and dataRefEnd as a pair",
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


def _metadata_module_diagnostics(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF 2.1 Metadata module) "metadata contains one or more metaGroup
    elements, and meta elements require a type attribute" -- grounded
    directly in the pinned XLIFF 2.1 Metadata module schema (inside
    .local/format-contracts/acquired/xliff/src-xlf-002.bin,
    schemas/metadata.xsd): metadata's own sequence requires minOccurs=1
    maxOccurs=unbounded metaGroup children, and meta's type attribute is
    use="required". metaGroup can nest recursively and meta can appear at
    any nesting depth within it, so this walks the whole subtree via
    ElementTree's own recursive iter() rather than only direct children.

    Only extensions actually carrying the Metadata module's own namespace
    are checked; every other extension (including malformed XML, already
    reported by _extension_well_formed) is left untouched.
    """

    if extension.tag != _METADATA_QNAME:
        return
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError:
        return
    if not any(child.tag == _METAGROUP_QNAME for child in element):
        diagnostics.append(
            Diagnostic(
                "xliff.module.metadata.metagroup.required",
                "metadata must contain at least one metaGroup element",
            )
        )
    for meta in element.iter(_META_QNAME):
        if "type" not in meta.attrib:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.metadata.meta.type.required",
                    "meta element requires a type attribute",
                )
            )


def _resource_data_module_diagnostics(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF modules - resource data with external references) "source
    and target resource payloads may use optional href attributes, while a
    reference element requires href" -- grounded directly in the pinned
    XLIFF 2.1 Resource Data module schema (inside
    .local/format-contracts/acquired/xliff/src-xlf-002.bin,
    schemas/resource_data.xsd): res:source/res:target both declare href
    use="optional", while res:reference declares href use="required".
    res:reference can appear (0..unbounded) inside any res:resourceItem
    nested inside the module's root res:resourceData element, so this
    walks the whole subtree via ElementTree's recursive iter() rather than
    only direct children.

    Only extensions actually carrying the Resource Data module's own
    namespace are checked; source/target's own optional href is not
    separately asserted since there is nothing to enforce about an
    attribute that is genuinely optional.
    """

    if extension.tag != _RESOURCE_DATA_QNAME:
        return
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError:
        return
    for reference in element.iter(_RESOURCE_REFERENCE_QNAME):
        if "href" not in reference.attrib:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.resourcedata.reference.href.required",
                    "reference element requires an href attribute",
                )
            )


def _matches_module_diagnostics(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF 2.1 Translation Candidates module) "matches contains one or
    more match elements, and each match requires ref plus one source and
    one target" -- grounded directly in the pinned XLIFF 2.1 Translation
    Candidates module schema (inside
    .local/format-contracts/acquired/xliff/src-xlf-002.bin,
    schemas/matches.xsd): mtc:matches declares minOccurs="1"
    maxOccurs="unbounded" for its mtc:match children; mtc:match itself
    declares its own ref attribute use="required" and requires EXACTLY one
    xlf:source and EXACTLY one xlf:target direct child -- both use the
    XLIFF core namespace (imported from xliff_core_2.0.xsd), not the
    Matches module's own namespace.

    Only extensions actually carrying the Matches module's own namespace
    are checked.
    """

    if extension.tag != _MATCHES_QNAME:
        return
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError:
        return
    matches = [child for child in element if child.tag == _MATCH_QNAME]
    if not matches:
        diagnostics.append(
            Diagnostic(
                "xliff.module.matches.match.required",
                "matches must contain at least one match element",
            )
        )
    for match in matches:
        if "ref" not in match.attrib:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.matches.match.ref.required",
                    "match element requires a ref attribute",
                )
            )
        source_count = sum(1 for child in match if child.tag == _CORE_SOURCE_QNAME)
        target_count = sum(1 for child in match if child.tag == _CORE_TARGET_QNAME)
        if source_count != 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.matches.match.source.required",
                    f"match element must contain exactly one source, found {source_count}",
                )
            )
        if target_count != 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.matches.match.target.required",
                    f"match element must contain exactly one target, found {target_count}",
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


def _document_has_target_content(value: XliffDocument) -> bool:
    """Whether a `<target>` element (empty or not) exists anywhere in the
    document as a child of a `<segment>` or `<ignorable>` -- matching the
    XLIFF 2.1 schematron's F1 pattern context exactly. `segment.target is
    not None` iff the reader found a real `<target>` element in the source
    XML (reader.py only assigns a non-None value when a `<target>` child
    was actually present, even an empty one)."""

    return any(
        segment.target is not None
        for file in value.files
        for unit in file.iter_units()
        for segment in unit.segments
    )


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
    if not value.target_language and _document_has_target_content(value):
        diagnostics.append(
            Diagnostic(
                "xliff.trgLang.required",
                "trgLang is required because the document contains target elements",
            )
        )
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
                    _metadata_module_diagnostics(segment_extension, diagnostics)
                    _resource_data_module_diagnostics(segment_extension, diagnostics)
                    _matches_module_diagnostics(segment_extension, diagnostics)
            _isolated_diagnostics(unit, diagnostics)
            _data_ref_diagnostics(unit, diagnostics)
        for file_child in file.children:
            if isinstance(file_child, ExtensionNode):
                _extension_well_formed(file_child, diagnostics)
                _metadata_module_diagnostics(file_child, diagnostics)
                _resource_data_module_diagnostics(file_child, diagnostics)
                _matches_module_diagnostics(file_child, diagnostics)
            elif isinstance(file_child, Group):
                for group_unit in _walk_group(file_child):
                    for group_child in group_unit.children:
                        if isinstance(group_child, ExtensionNode):
                            _extension_well_formed(group_child, diagnostics)
                            _metadata_module_diagnostics(group_child, diagnostics)
                            _resource_data_module_diagnostics(group_child, diagnostics)
                            _matches_module_diagnostics(group_child, diagnostics)
    for root_child in value.children:
        if isinstance(root_child, ExtensionNode):
            _extension_well_formed(root_child, diagnostics)
            _metadata_module_diagnostics(root_child, diagnostics)
            _resource_data_module_diagnostics(root_child, diagnostics)
            _matches_module_diagnostics(root_child, diagnostics)
    return ValidationReport(diagnostics)

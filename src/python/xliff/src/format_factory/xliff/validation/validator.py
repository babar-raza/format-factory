"""Semantic XLIFF core validation diagnostics."""

from __future__ import annotations

import re
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

_GLOSSARY_NAMESPACE = "urn:oasis:names:tc:xliff:glossary:2.0"
_GLOSSARY_QNAME = f"{{{_GLOSSARY_NAMESPACE}}}glossary"
_GLOSSENTRY_QNAME = f"{{{_GLOSSARY_NAMESPACE}}}glossEntry"
_GLS_TERM_QNAME = f"{{{_GLOSSARY_NAMESPACE}}}term"
_GLS_TRANSLATION_QNAME = f"{{{_GLOSSARY_NAMESPACE}}}translation"
_GLS_DEFINITION_QNAME = f"{{{_GLOSSARY_NAMESPACE}}}definition"

_VALIDATION_NAMESPACE = "urn:oasis:names:tc:xliff:validation:2.0"
_VALIDATION_QNAME = f"{{{_VALIDATION_NAMESPACE}}}validation"
_VAL_RULE_QNAME = f"{{{_VALIDATION_NAMESPACE}}}rule"
#: Per the pinned XLIFF 2.1 Validation module schema (schemas/validation.xsd,
#: xlf:yesNo type, reused from the core schema): existsInSource,
#: caseSensitive, and disabled are all typed xlf:yesNo.
_VAL_YES_NO_VALUES = frozenset({"yes", "no"})
#: Per the pinned Validation module schema's own normalization_type
#: simpleType restriction.
_VAL_NORMALIZATION_VALUES = frozenset({"none", "nfc", "nfd"})
#: The four "condition" attributes the spec's own rule Constraints section
#: names as mutually exclusive alternatives (the fifth alternative, "a
#: custom rule defined by attributes from any namespace," is any attribute
#: outside this set and the core module's own value/case/normalization/
#: disabled/occurs attributes).
_VAL_CONDITION_ATTRS = ("isPresent", "isNotPresent", "startsWith", "endsWith")
_CORE_SOURCE_QNAME = f"{{{XLIFF_NAMESPACE}}}source"
_CORE_TARGET_QNAME = f"{{{XLIFF_NAMESPACE}}}target"

_SLR_NAMESPACE = "urn:oasis:names:tc:xliff:sizerestriction:2.0"
_SLR_SIZE_INFO_ATTR = f"{{{_SLR_NAMESPACE}}}sizeInfo"
_SLR_SIZE_INFO_REF_ATTR = f"{{{_SLR_NAMESPACE}}}sizeInfoRef"

_FS_NAMESPACE = "urn:oasis:names:tc:xliff:fs:2.0"
_FS_FS_ATTR = f"{{{_FS_NAMESPACE}}}fs"
#: Per the pinned XLIFF 2.1 Format Style module schema (schemas/fs.xsd,
#: fs_type simpleType): the exhaustive, fixed enumeration fs:fs is
#: restricted to. fs:subFs is an unrestricted xs:string in the same
#: schema, so it has no value constraint to check.
_FS_TYPE_VALUES = frozenset(
    {
        "a", "b", "bdo", "big", "blockquote", "body", "br", "button", "caption",
        "center", "cite", "code", "col", "colgroup", "dd", "del", "div", "dl",
        "dt", "em", "h1", "h2", "h3", "h4", "h5", "h6", "head", "hr", "html",
        "i", "img", "label", "legend", "li", "ol", "p", "pre", "q", "s", "samp",
        "select", "small", "span", "strike", "strong", "sub", "sup", "table",
        "tbody", "td", "tfoot", "th", "thead", "title", "tr", "tt", "u", "ul",
    }
)


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


#: "Standalone placeholders use ph with a required id; paired containers use
#: pc with a required id; spanning pairs use sc with a required id ... " --
#: ec is deliberately excluded: it identifies its pairing via startRef, not
#: its own id, and the spec does not require one on ec itself.
_ID_REQUIRED_TAGS = frozenset({"ph", "pc", "sc"})


def _validate_inline(segment: Segment, diagnostics: list[Diagnostic]) -> None:
    for label, content in (("source", segment.source), ("target", segment.target or [])):
        elements = _inline_elements(content)
        for value in elements:
            if value.tag in _ID_REQUIRED_TAGS and not value.id:
                diagnostics.append(
                    Diagnostic(
                        "xliff.inline.id.required",
                        f"<{value.tag}> in segment {segment.id!r} {label} is missing its required id",
                    )
                )
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


_CAN_MATCH_ATTRS = ("canCopy", "canDelete", "canOverlap")


def _can_attr_matches(sc_value: str | None, ec_value: str | None) -> bool:
    """A "no" value on either side of a paired sc/ec requires "no" on the
    other; "yes" and an absent attribute -- both meaning the same schema
    default of "yes" -- are mutually compatible with each other. Grounded
    directly in the pinned XLIFF 2.1 schematron's own F5.1S/F5.1T
    assertions (e.g. canCopy: a report fires when @canCopy='no' and no
    matching ec also has canCopy='no'; a second, separate report fires
    when (@canCopy='yes' or not(@canCopy)) and no matching ec has either
    canCopy='yes' or canCopy absent)."""

    sc_no = sc_value == "no"
    ec_no = ec_value == "no"
    if sc_no or ec_no:
        return sc_no and ec_no
    return True


def _isolated_pairing_attribute_diagnostics(
    unit: Unit, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF Core start-code isolation, 2.1 schematron patterns F5.1S/
    F5.1T, clauses b and c) When a non-isolated sc has a resolvable
    matching ec in the same unit -- the case _isolated_diagnostics already
    proves does not raise xliff.inline.isolated.missing_ec -- their
    canCopy/canDelete/canOverlap attributes must be equivalent per
    _can_attr_matches(), and canReorder additionally allows sc's own
    "firstNo" value, which requires the matching ec's canReorder to be
    exactly "no" (grounded directly in the pinned schematron's own
    canReorder='firstNo' assertion, distinct from the shared no/yes-or-
    absent equivalence the other three attributes use).

    Scoped narrowly to exactly the sub-clauses this obligation cluster's
    own missing_behavior names as unbuilt; clause (a) -- exactly-one-ec
    existence and document-order -- is not re-implemented here, since
    _isolated_diagnostics already proves ec presence and this function
    only runs when a match was found.
    """

    for label in ("source", "target"):
        starts: list[InlineElement] = []
        ec_by_start_ref: dict[str, InlineElement] = {}
        for segment in unit.segments:
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                if element.tag == "sc" and element.id:
                    starts.append(element)
                elif element.tag == "ec":
                    start_ref = element.attributes.get("startRef")
                    if start_ref:
                        ec_by_start_ref[start_ref] = element
        for sc in starts:
            if sc.attributes.get("isolated", "no") == "yes":
                continue
            ec = ec_by_start_ref.get(sc.id)
            if ec is None:
                continue
            for attr in _CAN_MATCH_ATTRS:
                sc_value = sc.attributes.get(attr)
                ec_value = ec.attributes.get(attr)
                if not _can_attr_matches(sc_value, ec_value):
                    diagnostics.append(
                        Diagnostic(
                            f"xliff.inline.isolated.{attr.lower()}.mismatch",
                            f"sc {sc.id!r} in unit {unit.id!r} {label} has "
                            f"{attr}={sc_value!r} but its matching ec has "
                            f"{attr}={ec_value!r}",
                        )
                    )
            sc_reorder = sc.attributes.get("canReorder")
            ec_reorder = ec.attributes.get("canReorder")
            if sc_reorder == "firstNo":
                if ec_reorder != "no":
                    diagnostics.append(
                        Diagnostic(
                            "xliff.inline.isolated.canreorder.firstno_mismatch",
                            f"sc {sc.id!r} in unit {unit.id!r} {label} has "
                            f"canReorder='firstNo' but its matching ec's canReorder "
                            f"is {ec_reorder!r}, not 'no'",
                        )
                    )
            elif not _can_attr_matches(sc_reorder, ec_reorder):
                diagnostics.append(
                    Diagnostic(
                        "xliff.inline.isolated.canreorder.mismatch",
                        f"sc {sc.id!r} in unit {unit.id!r} {label} has "
                        f"canReorder={sc_reorder!r} but its matching ec has "
                        f"canReorder={ec_reorder!r}",
                    )
                )


def _data_ref_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF Core original data references, 2.1 schematron patterns F15/
    F16S/F16T/F17S/F17T) Every dataRef/dataRefStart/dataRefEnd attribute on
    an inline element must reference the id of a `<data>` element within
    the same unit's `<originalData>`; a pc's dataRefStart and dataRefEnd
    must be used as a pair (one present without the other is invalid),
    matching the pinned schematron's own assertions exactly, checked
    separately per content type (source/target).

    The pinned core schema (schemas/xliff_core_2.0.xsd) declares `<data>`'s
    own `id` attribute `use="required"`; a `<data>` element missing it is
    invalid in its own right, independent of whether any inline element
    happens to reference it -- checked here rather than silently dropped
    from data_ids, which previously left a required-attribute violation
    entirely undiagnosed.
    """

    for index, value in enumerate(unit.original_data):
        if not value.id:
            diagnostics.append(
                Diagnostic(
                    "xliff.originalData.data.id.missing",
                    f"data element at index {index} in unit {unit.id!r} is "
                    "missing its required id attribute",
                )
            )
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


#: A comment annotation's ref fragment is "#n=<note id>" (the pinned spec's
#: own worked example, section 4.7.3.1.3 Comment Annotation); this extracts
#: the note id from the trailing "n=..." segment, tolerant of a longer
#: qualified path (e.g. "#f=f1/u=u1/n=n1") even though this package only
#: ever needs the same-unit short form the spec's own MUST requires.
_MRK_COMMENT_REF_NOTE_ID = re.compile(r"n=([^/]+)$")


def _mrk_comment_ref_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF Core comment annotation, section 4.7.3.1.3) "The ref
    attribute MUST be present and contain the URI of a <note> element
    within the same enclosing <unit> element that holds the comment."
    Checked only for mrk elements whose type is "comment" -- the spec's
    other documented ref usage (e.g. type="term", pointing at an arbitrary
    external URI such as a DBpedia page) has no same-document resolution
    requirement at all, and is deliberately left unchecked."""

    note_ids = {note.id for note in unit.notes if note.id}
    for label in ("source", "target"):
        for segment in unit.segments:
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                if element.tag != "mrk" or element.attributes.get("type") != "comment":
                    continue
                ref = element.attributes.get("ref")
                if ref is None:
                    continue
                match = _MRK_COMMENT_REF_NOTE_ID.search(ref)
                note_id = match.group(1) if match else None
                if note_id is None or note_id not in note_ids:
                    diagnostics.append(
                        Diagnostic(
                            "xliff.mrk.comment.ref.unresolved",
                            f"mrk {element.id!r} in unit {unit.id!r} {label} has "
                            f"type=comment and ref={ref!r}, which does not resolve to "
                            f"a note in the same unit",
                        )
                    )


def _check_fs_value(
    attributes: dict[str, str],
    *,
    host_label: str,
    unit_id: str,
    diagnostics: list[Diagnostic],
) -> None:
    fs_value = attributes.get(_FS_FS_ATTR)
    if fs_value is not None and fs_value not in _FS_TYPE_VALUES:
        diagnostics.append(
            Diagnostic(
                "xliff.module.fs.fs.invalid",
                f"{host_label} in unit {unit_id!r} has fs:fs={fs_value!r}, which "
                f"the Format Style module schema does not permit",
            )
        )


def _format_style_module_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF 2.1 Format Style module) "fs and subFs attributes; fs values
    are constrained by the module schema" -- grounded directly in the
    pinned XLIFF 2.1 Format Style module schema (inside
    .local/format-contracts/acquired/xliff/src-xlf-002.bin, schemas/
    fs.xsd): fs:fs is restricted to a fixed enumeration of HTML-tag-like
    values (_FS_TYPE_VALUES); fs:subFs is an unrestricted xs:string, so it
    has no value to check.

    fs:fs/fs:subFs "attach to existing core elements rather than
    introducing their own" (confirmed directly by this package's own
    pre-existing Format Style fixture, which attaches them to a unit) --
    the pinned XLIFF 2.1 spec's own repeated Constraints text ("attributes
    from the namespace .../fs:2.0, OPTIONAL, provided that the Constraints
    specified in the Format Style Module are met") shows this wildcard
    permission recurring across many core elements' own constraint
    sections. This checks every host this package generically preserves
    unknown attributes on: the unit itself, each segment/ignorable and its
    own source/target attribute dicts, and every inline code element
    (ph/pc/sc/ec/mrk) within source/target content.
    """

    _check_fs_value(
        unit.attributes, host_label=f"unit {unit.id!r}", unit_id=unit.id, diagnostics=diagnostics
    )
    for segment in unit.segments:
        _check_fs_value(
            segment.attributes,
            host_label=f"{segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        _check_fs_value(
            segment.source_attributes,
            host_label=f"source of {segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        _check_fs_value(
            segment.target_attributes,
            host_label=f"target of {segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        for label in ("source", "target"):
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                _check_fs_value(
                    element.attributes,
                    host_label=f"{element.tag} {element.id!r} in {segment.kind} "
                    f"{segment.id!r} {label}",
                    unit_id=unit.id,
                    diagnostics=diagnostics,
                )


def _check_slr_size_info(
    attributes: dict[str, str],
    *,
    host_label: str,
    unit_id: str,
    diagnostics: list[Diagnostic],
) -> None:
    if _SLR_SIZE_INFO_ATTR in attributes and _SLR_SIZE_INFO_REF_ATTR in attributes:
        diagnostics.append(
            Diagnostic(
                "xliff.module.slr.sizeinfo.conflict",
                f"{host_label} in unit {unit_id!r} has both slr:sizeInfo and "
                f"slr:sizeInfoRef, which the Size and Length Restriction "
                f"module's own Constraints section forbids specifying at "
                f"the same time",
            )
        )


def _size_restriction_module_diagnostics(unit: Unit, diagnostics: list[Diagnostic]) -> None:
    """(XLIFF 2.1 Size and Length Restriction module) grounded directly in
    the pinned XLIFF 2.1 spec text (inside
    .local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.7
    "Size and Length Restriction Module"): sizeInfo's own prose Constraints
    section states "This attribute MUST NOT be specified if and only if
    sizeInfoRef is used. They MUST NOT be specified at the same time" --
    restated identically, from the other side, in sizeInfoRef's own
    Constraints section. This is the one universally-true (profile-
    independent) structural constraint the module defines; sizeRestriction/
    storageRestriction's own value format ("[minsize,]maxsize") is scoped
    to specific named standard profiles (xliff:codepoints, xliff:utf8, ...)
    selected via generalProfile/storageProfile, which can be declared at
    file/group/unit level and inherited -- resolving the active profile
    for an arbitrary host would need the same whole-tree, parent-aware
    resolution this package has deliberately not built for xml:space/
    xml:lang inheritance either, so that value-format check is correctly
    left unbuilt here, not attempted.

    slr:sizeInfo/slr:sizeInfoRef "attach to existing core elements rather
    than introducing their own" (confirmed directly by the spec's own
    "Used in:" list for both attributes: file, group, unit, pc, sc, ec,
    ph) -- the same wildcard-attribute shape as the Format Style module's
    own fs:fs/fs:subFs, so this checks the identical set of hosts
    _format_style_module_diagnostics already walks: the unit itself, each
    segment/ignorable and its own source/target attribute dicts, and
    every inline code element within source/target content.
    """

    _check_slr_size_info(
        unit.attributes, host_label=f"unit {unit.id!r}", unit_id=unit.id, diagnostics=diagnostics
    )
    for segment in unit.segments:
        _check_slr_size_info(
            segment.attributes,
            host_label=f"{segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        _check_slr_size_info(
            segment.source_attributes,
            host_label=f"source of {segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        _check_slr_size_info(
            segment.target_attributes,
            host_label=f"target of {segment.kind} {segment.id!r}",
            unit_id=unit.id,
            diagnostics=diagnostics,
        )
        for label in ("source", "target"):
            content = segment.source if label == "source" else (segment.target or [])
            for element in _inline_elements(content):
                _check_slr_size_info(
                    element.attributes,
                    host_label=f"{element.tag} {element.id!r} in {segment.kind} "
                    f"{segment.id!r} {label}",
                    unit_id=unit.id,
                    diagnostics=diagnostics,
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


def _glossary_module_diagnostics(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF 2.1 Glossary module) "glossary contains one or more glossEntry
    elements; each glossEntry contains exactly one term, zero or more
    translation, and at most one definition" -- grounded directly in the
    pinned XLIFF 2.1 Glossary module spec text and schema (inside
    .local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.2
    "Glossary Module" and its bundled glossary.xsd): glossary's own
    sequence declares minOccurs="1" maxOccurs="unbounded" for glossEntry;
    glossEntry declares minOccurs="1" maxOccurs="1" for term, minOccurs="0"
    maxOccurs="unbounded" for translation, and minOccurs="0" maxOccurs="1"
    for definition. The spec's own prose Constraints section for
    glossEntry separately states: "A glossEntry element MUST contain a
    translation or a definition element to be valid." The spec's own
    prose Constraints section for the id attribute separately states:
    "The values of id attributes MUST be unique among all glossEntry and
    translation elements within the given enclosing glossary element."

    Only extensions actually carrying the Glossary module's own namespace
    are checked; every other extension (including malformed XML, already
    reported by _extension_well_formed) is left untouched.
    """

    if extension.tag != _GLOSSARY_QNAME:
        return
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError:
        return
    entries = [child for child in element if child.tag == _GLOSSENTRY_QNAME]
    if not entries:
        diagnostics.append(
            Diagnostic(
                "xliff.module.glossary.glossentry.required",
                "glossary must contain at least one glossEntry element",
            )
        )
    seen_ids: set[str] = set()
    for entry in entries:
        terms = [child for child in entry if child.tag == _GLS_TERM_QNAME]
        if len(terms) != 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.glossary.term.required",
                    f"glossEntry must contain exactly one term element, found {len(terms)}",
                )
            )
        translations = [child for child in entry if child.tag == _GLS_TRANSLATION_QNAME]
        definitions = [child for child in entry if child.tag == _GLS_DEFINITION_QNAME]
        if len(definitions) > 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.glossary.definition.multiple",
                    "glossEntry must contain at most one definition element, "
                    f"found {len(definitions)}",
                )
            )
        if not translations and not definitions:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.glossary.translation_or_definition.required",
                    "glossEntry must contain a translation or a definition element",
                )
            )
        for id_holder in (entry, *translations):
            entry_id = id_holder.attrib.get("id")
            if entry_id is None:
                continue
            if entry_id in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        "xliff.module.glossary.id.duplicate",
                        f"glossary id {entry_id!r} is not unique within its "
                        "enclosing glossary element",
                    )
                )
            seen_ids.add(entry_id)


def _validation_module_diagnostics(
    extension: ExtensionNode, diagnostics: list[Diagnostic]
) -> None:
    """(XLIFF 2.1 Validation module) grounded directly in the pinned XLIFF
    2.1 Validation module spec text and schema (inside
    .local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.8
    "Validation Module" and its bundled validation.xsd):

    - validation's own sequence declares minOccurs="1" maxOccurs="unbounded"
      for rule (a validation with no rule is grammatically invalid).
    - rule's own prose Constraints section: "Exactly one of the following
      attributes: isPresent, isNotPresent, startsWith, endsWith, [or] a
      custom rule defined by attributes from any namespace ... is REQUIRED
      in any one rule element" -- both under-specification (none of the
      four present, no custom attribute either) and over-specification
      (more than one of the four present) violate "exactly one".
    - existsInSource's own prose Constraints section: "When existsInSource
      is specified, exactly one of isPresent, startsWith, [or] endsWith is
      REQUIRED in the same rule element" -- notably excluding isNotPresent,
      so existsInSource paired with isNotPresent (or with none of the
      three) is a distinct violation from the rule-level one above.
    - existsInSource, caseSensitive, and disabled are all typed xlf:yesNo
      in the schema; normalization is typed val:normalization_type
      (enumeration: none/nfc/nfd); occurs is typed xs:positiveInteger.

    This checks attribute-level modeling and grammar only -- it does not
    evaluate any rule's condition against actual segment source/target
    text (a genuinely separate, much larger capability: cascading
    validation scope resolution across file/group/unit levels, disabled-
    attribute override semantics, and text matching under case/
    normalization options). Only extensions actually carrying the
    Validation module's own namespace are checked.
    """

    if extension.tag != _VALIDATION_QNAME:
        return
    try:
        element = ET.fromstring(extension.xml)
    except ET.ParseError:
        return
    rules = [child for child in element if child.tag == _VAL_RULE_QNAME]
    if not rules:
        diagnostics.append(
            Diagnostic(
                "xliff.module.validation.rule.required",
                "validation must contain at least one rule element",
            )
        )
    for rule in rules:
        condition_present = [name for name in _VAL_CONDITION_ATTRS if name in rule.attrib]
        core_attrs = {
            "isPresent", "isNotPresent", "startsWith", "endsWith", "occurs",
            "existsInSource", "caseSensitive", "normalization", "disabled",
        }
        has_custom_attr = any(name not in core_attrs for name in rule.attrib)
        if not condition_present and not has_custom_attr:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.validation.rule.condition.required",
                    "rule must specify exactly one of isPresent, isNotPresent, "
                    "startsWith, endsWith, or a custom attribute from another namespace",
                )
            )
        elif len(condition_present) > 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.validation.rule.condition.conflict",
                    "rule must specify exactly one of isPresent, isNotPresent, "
                    f"startsWith, endsWith, found {len(condition_present)}: "
                    f"{', '.join(condition_present)}",
                )
            )
        if "existsInSource" in rule.attrib:
            compatible = [name for name in ("isPresent", "startsWith", "endsWith") if name in rule.attrib]
            if len(compatible) != 1:
                diagnostics.append(
                    Diagnostic(
                        "xliff.module.validation.existsinsource.condition.required",
                        "existsInSource requires exactly one of isPresent, "
                        f"startsWith, endsWith in the same rule element, found {len(compatible)}",
                    )
                )
        for yes_no_attr in ("existsInSource", "caseSensitive", "disabled"):
            value = rule.attrib.get(yes_no_attr)
            if value is not None and value not in _VAL_YES_NO_VALUES:
                diagnostics.append(
                    Diagnostic(
                        "xliff.module.validation.yesno.invalid",
                        f"rule attribute {yes_no_attr}={value!r} must be 'yes' or 'no'",
                    )
                )
        normalization = rule.attrib.get("normalization")
        if normalization is not None and normalization not in _VAL_NORMALIZATION_VALUES:
            diagnostics.append(
                Diagnostic(
                    "xliff.module.validation.normalization.invalid",
                    f"rule attribute normalization={normalization!r} must be one of "
                    "'none', 'nfc', 'nfd'",
                )
            )
        occurs = rule.attrib.get("occurs")
        if occurs is not None and not (occurs.isdigit() and int(occurs) >= 1):
            diagnostics.append(
                Diagnostic(
                    "xliff.module.validation.occurs.invalid",
                    f"rule attribute occurs={occurs!r} must be a positive integer",
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
                    _glossary_module_diagnostics(segment_extension, diagnostics)
                    _validation_module_diagnostics(segment_extension, diagnostics)
            _isolated_diagnostics(unit, diagnostics)
            _isolated_pairing_attribute_diagnostics(unit, diagnostics)
            _data_ref_diagnostics(unit, diagnostics)
            _mrk_comment_ref_diagnostics(unit, diagnostics)
            _format_style_module_diagnostics(unit, diagnostics)
            _size_restriction_module_diagnostics(unit, diagnostics)
        for file_child in file.children:
            if isinstance(file_child, ExtensionNode):
                _extension_well_formed(file_child, diagnostics)
                _metadata_module_diagnostics(file_child, diagnostics)
                _resource_data_module_diagnostics(file_child, diagnostics)
                _matches_module_diagnostics(file_child, diagnostics)
                _glossary_module_diagnostics(file_child, diagnostics)
                _validation_module_diagnostics(file_child, diagnostics)
            elif isinstance(file_child, Group):
                for group_unit in _walk_group(file_child):
                    for group_child in group_unit.children:
                        if isinstance(group_child, ExtensionNode):
                            _extension_well_formed(group_child, diagnostics)
                            _metadata_module_diagnostics(group_child, diagnostics)
                            _resource_data_module_diagnostics(group_child, diagnostics)
                            _matches_module_diagnostics(group_child, diagnostics)
                            _glossary_module_diagnostics(group_child, diagnostics)
                            _validation_module_diagnostics(group_child, diagnostics)
    for root_child in value.children:
        if isinstance(root_child, ExtensionNode):
            _extension_well_formed(root_child, diagnostics)
            _metadata_module_diagnostics(root_child, diagnostics)
            _resource_data_module_diagnostics(root_child, diagnostics)
            _matches_module_diagnostics(root_child, diagnostics)
            _glossary_module_diagnostics(root_child, diagnostics)
            _validation_module_diagnostics(root_child, diagnostics)
    return ValidationReport(diagnostics)

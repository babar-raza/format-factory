"""XLIFF-QA-001 -- pluggable localization quality checks.

"Missing/unchanged targets, code mismatches, whitespace/punctuation drift,
length violations, and inconsistent translations are pluggable QA checks kept
separate from conformance errors." validation/validator.py answers "is this
document a well-formed XLIFF document"; this module answers "is this
translation any good" -- a different question, with a different severity
scale (never ERROR/FATAL, since a QA finding is a suggestion for a reviewer,
not a reason to refuse the document) and its own report, never merged into
validate()'s.

Each check is independently callable and independently selectable through
``run_qa_checks(checks=...)`` -- "pluggable" means a caller can run one check
without paying for the others, not merely that several checks exist.

Length violations (check_length_violations) close the one named category
that was NOT implemented here. A prior tick's own module docstring framed
"actual numeric restriction values from the Size and Length Restriction
module" as needing "the same whole-tree, parent-aware resolution this
package has deliberately not built for xml:space/xml:lang inheritance" --
investigated and found that resolution already existed (model/document.py
effective_xml_space()/effective_xml_lang()'s own composition pattern,
built for XLIFF-MODEL-001), just never connected to this module. See
check_length_violations' own docstring for the full grounding.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from format_factory.core import Diagnostic, Severity, ValidationReport

from .model import (
    ExtensionNode,
    Group,
    InlineElement,
    InlineNode,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    flatten_inline_content,
)

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

_TERMINAL_PUNCTUATION = frozenset({".", "!", "?", "。", "！", "？"})

_SLR_NAMESPACE = "urn:oasis:names:tc:xliff:sizerestriction:2.0"
_SLR_SIZE_RESTRICTION_ATTR = f"{{{_SLR_NAMESPACE}}}sizeRestriction"
_SLR_STORAGE_RESTRICTION_ATTR = f"{{{_SLR_NAMESPACE}}}storageRestriction"
_SLR_PROFILES_QNAME = f"{{{_SLR_NAMESPACE}}}profiles"

#: The 4 standard profiles the pinned XLIFF 2.1 spec fully defines (Section
#: 5.7.6 "Standard profiles"): xliff:codepoints counts Unicode code points
#: ("a simple string length restriction based on the number of Unicode
#: code points"); the 3 storage profiles count 8-bit bytes needed to
#: represent the text in that encoding "without any byte order marks
#: attached" ("xliff:utf8", "xliff:utf16", "xliff:utf32"). A profile name
#: not in this table (a third-party or future standard profile) has no
#: known counting rule and is silently skipped, not treated as a violation
#: or an error -- this check can only evaluate profiles it actually knows.
_STANDARD_PROFILES = {
    "xliff:codepoints": lambda text: len(text),
    "xliff:utf8": lambda text: len(text.encode("utf-8")),
    "xliff:utf16": lambda text: len(text.encode("utf-16-be")),
    "xliff:utf32": lambda text: len(text.encode("utf-32-be")),
}


def _inline_signature(content: list[InlineNode]) -> tuple[tuple[str, str], ...]:
    """The ordered sequence of (tag, id) pairs, ignoring plain text.

    Two segments whose signatures differ have gained, lost, or reordered a
    placeholder/code -- the structural half of "code mismatches". id is
    included, not just tag: two same-tagged codes (e.g. two <ph/> elements)
    that swap positions are a real reordering, and a tag-only signature would
    miss it since both orders produce the same tag sequence."""
    signature: list[tuple[str, str]] = []
    for node in content:
        if isinstance(node, InlineElement):
            signature.append((node.tag, node.id))
            signature.extend(_inline_signature(node.content))
    return tuple(signature)


def _iter_segments(document: XliffDocument) -> list[Segment]:
    return [
        segment
        for unit in document.iter_units()
        for segment in unit.segments
        if segment.kind == "segment"
    ]


def check_missing_targets(document: XliffDocument) -> list[Diagnostic]:
    """A segment with no target at all still needs translation.

    Distinct from validator.py's xliff.segment.state.target_required: that is
    a CONFORMANCE rule that only fires when state already claims translated/
    reviewed/final. This fires for every untranslated segment regardless of
    declared state, because an untranslated segment is a QA-relevant fact on
    its own."""
    return [
        Diagnostic(
            "xliff.qa.target.missing",
            f"segment {segment.id!r} has no target",
            severity=Severity.INFO,
        )
        for segment in _iter_segments(document)
        if segment.target is None
    ]


def check_unchanged_targets(document: XliffDocument) -> list[Diagnostic]:
    """Target text identical to source text usually means untranslated
    copy-through rather than a genuine translation."""
    diagnostics: list[Diagnostic] = []
    for segment in _iter_segments(document):
        if segment.target is None:
            continue
        source_text = flatten_inline_content(segment.source)
        target_text = flatten_inline_content(segment.target)
        if source_text and source_text == target_text:
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.target.unchanged",
                    f"segment {segment.id!r} target is identical to source",
                    severity=Severity.WARNING,
                )
            )
    return diagnostics


def check_placeholder_mismatch(document: XliffDocument) -> list[Diagnostic]:
    """"code mismatches": the target must reproduce every inline code the
    source declared, in the same relative structure. A dropped or duplicated
    placeholder breaks the rendered document even when the prose reads fine."""
    diagnostics: list[Diagnostic] = []
    for segment in _iter_segments(document):
        if segment.target is None:
            continue
        source_signature = _inline_signature(segment.source)
        target_signature = _inline_signature(segment.target)
        if source_signature != target_signature:
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.placeholder.mismatch",
                    f"segment {segment.id!r} target inline codes "
                    f"{list(target_signature)} do not match source "
                    f"{list(source_signature)}",
                    severity=Severity.WARNING,
                )
            )
    return diagnostics


def check_whitespace_punctuation_drift(document: XliffDocument) -> list[Diagnostic]:
    """"whitespace/punctuation drift": leading/trailing whitespace and
    terminal punctuation are part of a source's shape; losing them in
    translation is usually an oversight, not a stylistic choice."""
    diagnostics: list[Diagnostic] = []
    for segment in _iter_segments(document):
        if segment.target is None:
            continue
        source_text = flatten_inline_content(segment.source)
        target_text = flatten_inline_content(segment.target)
        if not source_text or not target_text:
            continue
        if (source_text != source_text.lstrip()) != (target_text != target_text.lstrip()):
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.whitespace.drift",
                    f"segment {segment.id!r} target leading whitespace does not match source",
                    severity=Severity.INFO,
                )
            )
        if (source_text != source_text.rstrip()) != (target_text != target_text.rstrip()):
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.whitespace.drift",
                    f"segment {segment.id!r} target trailing whitespace does not match source",
                    severity=Severity.INFO,
                )
            )
        source_terminal = source_text.rstrip()[-1:] in _TERMINAL_PUNCTUATION
        target_terminal = target_text.rstrip()[-1:] in _TERMINAL_PUNCTUATION
        if source_terminal != target_terminal:
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.punctuation.drift",
                    f"segment {segment.id!r} target terminal punctuation does not match source",
                    severity=Severity.INFO,
                )
            )
    return diagnostics


def _language_specificity_relation(target_lang: str, doc_lang: str) -> str:
    """Return 'exact', 'more_specific', 'reverse_specific', or 'incompatible'.

    BCP-47 subtag comparison: "en-US" is more specific than "en" (adds
    subtags after an exact prefix match); the reverse direction -- a target
    declaring LESS specificity than the document claims -- is its own
    reportable case, not silently treated as compatible.
    """
    target_lower = target_lang.lower()
    doc_lower = doc_lang.lower()
    if target_lower == doc_lower:
        return "exact"
    if target_lower.startswith(doc_lower + "-"):
        return "more_specific"
    if doc_lower.startswith(target_lower + "-"):
        return "reverse_specific"
    return "incompatible"


def check_target_language_compatibility(document: XliffDocument) -> list[Diagnostic]:
    """(XLIFF Core target language compatibility) "An explicit xml:lang value
    on a target child of segment or ignorable must satisfy the enclosing
    xliff trgLang. XLIFF 2.0 requires exact equality; the normative XLIFF 2.1
    F4T Schematron accepts exact and more-specific language tags and reports
    incompatible or reverse-specific values."
    """
    diagnostics: list[Diagnostic] = []
    if not document.target_language:
        return diagnostics
    for unit in document.iter_units():
        for segment in unit.children:
            if not isinstance(segment, Segment) or segment.target is None:
                continue
            explicit_lang = segment.target_attributes.get(XML_LANG)
            if not explicit_lang:
                continue
            relation = _language_specificity_relation(
                explicit_lang, document.target_language
            )
            if relation == "exact":
                continue
            if relation == "more_specific" and document.version != "2.0":
                continue
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.language.incompatible",
                    f"segment {segment.id!r} target xml:lang {explicit_lang!r} "
                    f"is {relation} relative to trgLang {document.target_language!r}",
                    severity=Severity.WARNING,
                )
            )
    return diagnostics


def check_source_language_compatibility(document: XliffDocument) -> list[Diagnostic]:
    """(XLIFF 2.1 Core source language compatibility) "An explicit xml:lang
    value on a source child of segment or ignorable must satisfy the
    enclosing xliff srcLang. XLIFF 2.1 accepts exact and more-specific
    language tags and reports incompatible values."

    The source-side sibling of check_target_language_compatibility, sharing
    the same specificity relation and QA-severity framing -- srcLang
    compatibility is exactly as much a reviewer-facing quality signal as
    trgLang compatibility, not a harder conformance error.
    """
    diagnostics: list[Diagnostic] = []
    if not document.source_language:
        return diagnostics
    for unit in document.iter_units():
        for segment in unit.children:
            if not isinstance(segment, Segment):
                continue
            explicit_lang = segment.source_attributes.get(XML_LANG)
            if not explicit_lang:
                continue
            relation = _language_specificity_relation(
                explicit_lang, document.source_language
            )
            if relation == "exact":
                continue
            if relation == "more_specific" and document.version != "2.0":
                continue
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.language.incompatible",
                    f"segment {segment.id!r} source xml:lang {explicit_lang!r} "
                    f"is {relation} relative to srcLang {document.source_language!r}",
                    severity=Severity.WARNING,
                )
            )
    return diagnostics


def check_translation_consistency(document: XliffDocument) -> list[Diagnostic]:
    """The same source text translated two different ways within one
    document is usually an inconsistency to flag for a reviewer, not an
    intentional stylistic choice -- context that would justify it belongs in
    a note, not a silently divergent target."""
    by_source: dict[str, set[str]] = {}
    for segment in _iter_segments(document):
        if segment.target is None:
            continue
        source_text = flatten_inline_content(segment.source)
        target_text = flatten_inline_content(segment.target)
        if not source_text or not target_text:
            continue
        by_source.setdefault(source_text, set()).add(target_text)

    diagnostics: list[Diagnostic] = []
    for source_text, targets in sorted(by_source.items()):
        if len(targets) > 1:
            diagnostics.append(
                Diagnostic(
                    "xliff.qa.translation.inconsistent",
                    f"source text {source_text!r} has {len(targets)} distinct "
                    f"translations: {sorted(targets)}",
                    severity=Severity.WARNING,
                )
            )
    return diagnostics


def _parse_size_restriction(value: str) -> tuple[int, int | None] | None:
    """Parse "[minsize,]maxsize" per the pinned spec's own xliff:codepoints
    profile text (Section 5.7.6.1.1, shared verbatim in spirit by the 3
    storage profiles' own Section 5.7.6.2.1): maxsize may be "*" for
    unbounded; if only a maxsize is given, minimum is implied 0. Returns
    None (not raises) for a value this package cannot parse -- an
    unparseable restriction is reported as absent rather than crashing the
    whole QA pass over one malformed attribute elsewhere in the document.
    """
    parts = value.split(",")
    try:
        if len(parts) == 1:
            minimum, maximum_raw = 0, parts[0].strip()
        elif len(parts) == 2:
            minimum, maximum_raw = int(parts[0].strip()), parts[1].strip()
        else:
            return None
        maximum = None if maximum_raw == "*" else int(maximum_raw)
    except ValueError:
        return None
    return minimum, maximum


def _file_profiles(file: XliffFile) -> tuple[str | None, str | None]:
    """(generalProfile, storageProfile) declared on this file's own
    <slr:profiles> module-extension child, or (None, None) if absent or
    declared empty -- matching the spec's own "Used in: <profiles>"
    scoping (Section 5.7.4.2/5.7.5.1/5.7.5.2): declared once per file, not
    inherited or cascaded the way sizeRestriction/storageRestriction are.
    "Empty string means that no restrictions apply", per the spec's own
    default-value text for both attributes -- handled identically to
    absence by the `or None` below.
    """
    for child in file.children:
        if isinstance(child, ExtensionNode) and child.tag == _SLR_PROFILES_QNAME:
            try:
                element = ET.fromstring(child.xml)
            except ET.ParseError:
                return None, None
            return element.get("generalProfile") or None, element.get("storageProfile") or None
    return None, None


def _effective_restrictions_by_unit(
    file: XliffFile,
) -> dict[str, tuple[str | None, str | None]]:
    """{unit_id: (effective_sizeRestriction, effective_storageRestriction)}
    for every unit in `file`, resolved via nearest-declaring-ancestor
    (file -> group* -> unit) -- the identical top-down composition pattern
    already proven for model/document.py's own effective_attributes_by_unit()
    (XLIFF-MODEL-001). Unlike xml:space, sizeRestriction/storageRestriction
    have no default at any level (the spec's own Default value: "undefined"
    for both) -- an ancestor chain with no declaration anywhere resolves to
    None (no restriction), not a fallback value.

    Scoped to file/group/unit -- the "structural" hosts the spec names
    (sizeRestriction is also "Used in": mrk, sm, pc, sc, the inline-level
    hosts; storageRestriction similarly). Inline-level restriction is a
    separate, smaller follow-up, deliberately not attempted here.
    """
    result: dict[str, tuple[str | None, str | None]] = {}

    def _walk(node: Group | Unit, parent_size: str | None, parent_storage: str | None) -> None:
        size = node.attributes.get(_SLR_SIZE_RESTRICTION_ATTR, parent_size)
        storage = node.attributes.get(_SLR_STORAGE_RESTRICTION_ATTR, parent_storage)
        if isinstance(node, Unit):
            result[node.id] = (size, storage)
            return
        for child in node.children:
            if isinstance(child, (Group, Unit)):
                _walk(child, size, storage)

    file_size = file.attributes.get(_SLR_SIZE_RESTRICTION_ATTR)
    file_storage = file.attributes.get(_SLR_STORAGE_RESTRICTION_ATTR)
    for child in file.children:
        if isinstance(child, (Group, Unit)):
            _walk(child, file_size, file_storage)

    return result


def _length_diagnostic(
    segment_id: str, kind: str, count: int, minimum: int, maximum: int | None
) -> Diagnostic | None:
    if count < minimum:
        return Diagnostic(
            f"xliff.qa.length.{kind}.under",
            f"segment {segment_id!r} target {kind} {count} is below the "
            f"minimum of {minimum}",
            severity=Severity.WARNING,
        )
    if maximum is not None and count > maximum:
        return Diagnostic(
            f"xliff.qa.length.{kind}.over",
            f"segment {segment_id!r} target {kind} {count} exceeds the "
            f"maximum of {maximum}",
            severity=Severity.WARNING,
        )
    return None


def check_length_violations(document: XliffDocument) -> list[Diagnostic]:
    """"length violations": slr:sizeRestriction/storageRestriction declare
    a "[minsize,]maxsize" bound on a unit's (or an ancestor group/file's)
    own target text size, interpreted under the file's own declared
    generalProfile/storageProfile (an <slr:profiles> module-extension
    child of <file>, Section 5.7.4.2/5.7.5.1/5.7.5.2). Implements the 4
    standard profiles the pinned spec fully defines (Section 5.7.6):
    xliff:codepoints (Unicode code point count) and the 3 storage profiles
    xliff:utf8/utf16/utf32 (byte count under that encoding, no BOM).

    A prior tick's own module docstring framed this as needing "the same
    whole-tree, parent-aware resolution this package has deliberately not
    built for xml:space/xml:lang inheritance" -- investigated and found
    that resolution already existed (effective_xml_space()/
    effective_xml_lang()'s own composition pattern, XLIFF-MODEL-001), just
    never connected to this module; _effective_restrictions_by_unit()
    reuses the identical shape.

    A file with no declared generalProfile/storageProfile, or one naming a
    profile this package does not recognize, is silently skipped for that
    dimension -- "empty string means no restrictions apply" is the spec's
    own stated default, and an unrecognized profile has no known counting
    rule to check against.

    Scoped to file/group/unit-level sizeRestriction/storageRestriction
    only (see _effective_restrictions_by_unit's own docstring); mrk/sm/
    pc/sc (inline-level hosts) are a separate, smaller follow-up.
    """
    diagnostics: list[Diagnostic] = []
    for file in document.files:
        general_profile, storage_profile = _file_profiles(file)
        general_counter = _STANDARD_PROFILES.get(general_profile) if general_profile else None
        storage_counter = _STANDARD_PROFILES.get(storage_profile) if storage_profile else None
        if general_counter is None and storage_counter is None:
            continue
        restrictions = _effective_restrictions_by_unit(file)
        for unit in file.iter_units():
            size_value, storage_value = restrictions.get(unit.id, (None, None))
            for segment in unit.segments:
                if segment.kind != "segment" or segment.target is None:
                    continue
                target_text = flatten_inline_content(segment.target)
                if size_value is not None and general_counter is not None:
                    parsed = _parse_size_restriction(size_value)
                    if parsed is not None:
                        diagnostic = _length_diagnostic(
                            segment.id, "size", general_counter(target_text), *parsed
                        )
                        if diagnostic is not None:
                            diagnostics.append(diagnostic)
                if storage_value is not None and storage_counter is not None:
                    parsed = _parse_size_restriction(storage_value)
                    if parsed is not None:
                        diagnostic = _length_diagnostic(
                            segment.id, "storage", storage_counter(target_text), *parsed
                        )
                        if diagnostic is not None:
                            diagnostics.append(diagnostic)
    return diagnostics


QA_CHECKS = {
    "missing_target": check_missing_targets,
    "unchanged_target": check_unchanged_targets,
    "placeholder_mismatch": check_placeholder_mismatch,
    "whitespace_punctuation_drift": check_whitespace_punctuation_drift,
    "source_language_compatibility": check_source_language_compatibility,
    "target_language_compatibility": check_target_language_compatibility,
    "translation_consistency": check_translation_consistency,
    "length_violations": check_length_violations,
}


def run_qa_checks(
    document: XliffDocument, *, checks: list[str] | None = None
) -> ValidationReport:
    """Run the named QA checks (default: all) and return them as one report.

    Always separate from validate()'s conformance ValidationReport -- a
    caller who wants both calls both and keeps the two results distinct,
    exactly as the obligation requires.
    """
    selected = QA_CHECKS if checks is None else {name: QA_CHECKS[name] for name in checks}
    diagnostics: list[Diagnostic] = []
    for check in selected.values():
        diagnostics.extend(check(document))
    return ValidationReport(diagnostics)


__all__ = [
    "QA_CHECKS",
    "check_length_violations",
    "check_missing_targets",
    "check_placeholder_mismatch",
    "check_source_language_compatibility",
    "check_target_language_compatibility",
    "check_translation_consistency",
    "check_unchanged_targets",
    "check_whitespace_punctuation_drift",
    "run_qa_checks",
]

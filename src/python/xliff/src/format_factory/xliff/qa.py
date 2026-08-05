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

Length violations are the one named category NOT implemented here. Checking
them meaningfully needs actual numeric restriction values from the Size and
Length Restriction module (slr:profiles' sizeRestriction/storageRestriction),
which XLIFF-MODULE-001 (modules.py) deliberately keeps PRESERVATION_ONLY: the
raw XML round-trips, but nothing parses its attributes into usable values yet.
A stub that always passes would be worse than an honest gap -- it would look
like coverage that was never built.
"""

from __future__ import annotations

from format_factory.core import Diagnostic, Severity, ValidationReport

from .model import InlineElement, InlineNode, Segment, XliffDocument, flatten_inline_content

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

_TERMINAL_PUNCTUATION = frozenset({".", "!", "?", "。", "！", "？"})


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


QA_CHECKS = {
    "missing_target": check_missing_targets,
    "unchanged_target": check_unchanged_targets,
    "placeholder_mismatch": check_placeholder_mismatch,
    "whitespace_punctuation_drift": check_whitespace_punctuation_drift,
    "target_language_compatibility": check_target_language_compatibility,
    "translation_consistency": check_translation_consistency,
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
    "check_missing_targets",
    "check_placeholder_mismatch",
    "check_target_language_compatibility",
    "check_translation_consistency",
    "check_unchanged_targets",
    "check_whitespace_punctuation_drift",
    "run_qa_checks",
]

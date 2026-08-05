"""XLIFF-QA-001 against the shipped namespace.

SAL-XLIFF-6F42212680161FF2 (SHOULD): missing/unchanged targets, code
mismatches, whitespace/punctuation drift, length violations, and
inconsistent translations are pluggable QA checks kept separate from
conformance errors.

Written directly against format_factory.xliff, not ported from the shadow
xliff.* package (GAP-018).
"""

from __future__ import annotations

from format_factory.core import Severity

from format_factory.xliff import (
    QA_CHECKS,
    check_missing_targets,
    check_placeholder_mismatch,
    check_target_language_compatibility,
    check_translation_consistency,
    check_unchanged_targets,
    check_whitespace_punctuation_drift,
    loads,
    run_qa_checks,
    validate,
)

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document(unit_body: str, *, version: str = "2.0", trg_lang: str | None = None) -> str:
    trg = f' trgLang="{trg_lang}"' if trg_lang else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{XLIFF_NS}" version="{version}" srcLang="en"{trg}>'
        f'<file id="f1">{unit_body}</file>'
        f"</xliff>"
    )


def _unit(unit_id: str, segments: str) -> str:
    return f'<unit id="{unit_id}">{segments}</unit>'


def _segment(seg_id: str, source: str, target: str | None = None, target_attrs: str = "") -> str:
    src = f'<source>{source}</source>'
    tgt = f'<target{target_attrs}>{target}</target>' if target is not None else ""
    return f'<segment id="{seg_id}">{src}{tgt}</segment>'


# ── Separation from conformance ─────────────────────────────────────────────


def test_qa_report_is_separate_from_conformance_report() -> None:
    """"kept separate from conformance errors" -- two distinct calls, two
    distinct reports, neither merged into the other."""
    xml = _document(_unit("u1", _segment("s1", "hello")))
    document = loads(xml)

    conformance = validate(document)
    quality = run_qa_checks(document)

    assert conformance is not quality
    assert all(code.startswith("xliff.qa.") for code in (d.code for d in quality.diagnostics))
    assert not any(code.startswith("xliff.qa.") for code in (d.code for d in conformance.diagnostics))


def test_qa_diagnostics_never_use_conformance_severities() -> None:
    """A QA finding is a suggestion for a reviewer, not a reason to refuse
    the document -- it must never reach ERROR or FATAL."""
    xml = _document(_unit("u1", _segment("s1", "hello")))
    document = loads(xml)

    report = run_qa_checks(document)

    assert all(
        diagnostic.severity in {Severity.INFO, Severity.WARNING}
        for diagnostic in report.diagnostics
    )


def test_qa_checks_are_pluggable_individually() -> None:
    """"pluggable QA checks" -- a caller can run exactly one."""
    xml = _document(_unit("u1", _segment("s1", "hello")))
    document = loads(xml)

    only_missing = run_qa_checks(document, checks=["missing_target"])

    assert all(d.code == "xliff.qa.target.missing" for d in only_missing.diagnostics)


def test_all_named_checks_are_registered() -> None:
    assert set(QA_CHECKS) == {
        "missing_target",
        "unchanged_target",
        "placeholder_mismatch",
        "whitespace_punctuation_drift",
        "target_language_compatibility",
        "translation_consistency",
    }


# ── Missing targets ─────────────────────────────────────────────────────────


def test_missing_target_is_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "hello")))
    document = loads(xml)

    findings = check_missing_targets(document)

    assert len(findings) == 1
    assert findings[0].code == "xliff.qa.target.missing"


def test_present_target_is_not_flagged_as_missing() -> None:
    xml = _document(_unit("u1", _segment("s1", "hello", "bonjour")))
    document = loads(xml)

    assert check_missing_targets(document) == []


# ── Unchanged targets ────────────────────────────────────────────────────────


def test_unchanged_target_is_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "hello", "hello")))
    document = loads(xml)

    findings = check_unchanged_targets(document)

    assert len(findings) == 1
    assert findings[0].code == "xliff.qa.target.unchanged"


def test_genuinely_translated_target_is_not_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "hello", "bonjour")))
    document = loads(xml)

    assert check_unchanged_targets(document) == []


def test_missing_target_is_not_double_flagged_as_unchanged() -> None:
    xml = _document(_unit("u1", _segment("s1", "hello")))
    document = loads(xml)

    assert check_unchanged_targets(document) == []


# ── Placeholder / code mismatches ───────────────────────────────────────────


def test_dropped_placeholder_is_flagged() -> None:
    source = 'Click <ph id="1"/> to continue'
    target = "Cliquez pour continuer"
    xml = _document(_unit("u1", _segment("s1", source, target)))
    document = loads(xml)

    findings = check_placeholder_mismatch(document)

    assert len(findings) == 1
    assert findings[0].code == "xliff.qa.placeholder.mismatch"


def test_preserved_placeholder_is_not_flagged() -> None:
    source = 'Click <ph id="1"/> to continue'
    target = 'Cliquez <ph id="1"/> pour continuer'
    xml = _document(_unit("u1", _segment("s1", source, target)))
    document = loads(xml)

    assert check_placeholder_mismatch(document) == []


def test_reordered_placeholders_are_flagged() -> None:
    source = '<ph id="1"/>a<ph id="2"/>'
    target = '<ph id="2"/>a<ph id="1"/>'
    xml = _document(_unit("u1", _segment("s1", source, target)))
    document = loads(xml)

    findings = check_placeholder_mismatch(document)

    assert len(findings) == 1


# ── Whitespace and punctuation drift ────────────────────────────────────────


def test_terminal_punctuation_drift_is_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "Hello.", "Bonjour")))
    document = loads(xml)

    findings = check_whitespace_punctuation_drift(document)

    assert any(f.code == "xliff.qa.punctuation.drift" for f in findings)


def test_matching_terminal_punctuation_is_not_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "Hello.", "Bonjour.")))
    document = loads(xml)

    assert not any(
        f.code == "xliff.qa.punctuation.drift"
        for f in check_whitespace_punctuation_drift(document)
    )


def test_trailing_whitespace_drift_is_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "Hello ", "Bonjour")))
    document = loads(xml)

    findings = check_whitespace_punctuation_drift(document)

    assert any(f.code == "xliff.qa.whitespace.drift" for f in findings)


# ── Target language compatibility ───────────────────────────────────────────


def test_xliff_20_requires_exact_language_match() -> None:
    """"XLIFF 2.0 requires exact equality." """
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour", target_attrs=' xml:lang="fr-CA"')),
        version="2.0",
        trg_lang="fr",
    )
    document = loads(xml)

    findings = check_target_language_compatibility(document)

    assert len(findings) == 1
    assert "reverse_specific" in findings[0].message or "more_specific" in findings[0].message


def test_xliff_20_exact_match_passes() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour", target_attrs=' xml:lang="fr"')),
        version="2.0",
        trg_lang="fr",
    )
    document = loads(xml)

    assert check_target_language_compatibility(document) == []


def test_xliff_21_accepts_more_specific_language() -> None:
    """"the normative XLIFF 2.1 F4T Schematron accepts exact and
    more-specific language tags." """
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour", target_attrs=' xml:lang="fr-CA"')),
        version="2.1",
        trg_lang="fr",
    )
    document = loads(xml)

    assert check_target_language_compatibility(document) == []


def test_xliff_21_reports_reverse_specific_language() -> None:
    """"...and reports incompatible or reverse-specific values." A target
    LESS specific than the document's own declared trgLang."""
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour", target_attrs=' xml:lang="fr"')),
        version="2.1",
        trg_lang="fr-CA",
    )
    document = loads(xml)

    findings = check_target_language_compatibility(document)

    assert len(findings) == 1
    assert "reverse_specific" in findings[0].message


def test_xliff_21_reports_incompatible_language() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "hello", "guten Tag", target_attrs=' xml:lang="de"')),
        version="2.1",
        trg_lang="fr",
    )
    document = loads(xml)

    findings = check_target_language_compatibility(document)

    assert len(findings) == 1
    assert "incompatible" in findings[0].message


def test_no_explicit_xml_lang_is_not_flagged() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour")), version="2.1", trg_lang="fr"
    )
    document = loads(xml)

    assert check_target_language_compatibility(document) == []


def test_no_document_trg_lang_means_nothing_to_check_against() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "hello", "bonjour", target_attrs=' xml:lang="de"'))
    )
    document = loads(xml)
    assert document.target_language is None

    assert check_target_language_compatibility(document) == []


# ── Translation consistency ─────────────────────────────────────────────────


def test_inconsistent_translation_of_the_same_source_is_flagged() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "Cancel", "Annuler"))
        + _unit("u2", _segment("s2", "Cancel", "Abandonner"))
    )
    document = loads(xml)

    findings = check_translation_consistency(document)

    assert len(findings) == 1
    assert findings[0].code == "xliff.qa.translation.inconsistent"


def test_consistent_translation_of_repeated_source_is_not_flagged() -> None:
    xml = _document(
        _unit("u1", _segment("s1", "Cancel", "Annuler"))
        + _unit("u2", _segment("s2", "Cancel", "Annuler"))
    )
    document = loads(xml)

    assert check_translation_consistency(document) == []


def test_single_occurrence_source_is_not_flagged() -> None:
    xml = _document(_unit("u1", _segment("s1", "Cancel", "Annuler")))
    document = loads(xml)

    assert check_translation_consistency(document) == []

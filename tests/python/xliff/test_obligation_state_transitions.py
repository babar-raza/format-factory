"""XLIFF-STATE-001 against the shipped namespace.

MUST (SAL-XLIFF-00018, verified, "XLIFF core - translation state"): "Expose
target state and substate without inventing proprietary semantics; allow
configurable workflow transition validation." "Segment elements carry an
optional state attribute defaulting to initial with values initial,
translated, reviewed, and final; translated, reviewed, or final requires a
target child."

required_tests: "Transition-policy fixtures (legal and illegal
transitions)."

Two obligations share this capability and this required_tests text:

* SAL-XLIFF-OBL-AF86B77156C7C1E2 (the core spec enum + target-required
  rule) was already fully implemented in validation/validator.py
  (_STATES, _TARGET_REQUIRED_STATES) with positive/negative proof already
  sitting in test_production_namespace.py
  (test_advanced_translation_state_requires_target,
  test_initial_state_and_advanced_state_with_target_are_valid) -- but cited
  under the WRONG obligation's evidence (generic round-trip tests instead
  of these). This file adds the one genuinely missing case (an invalid
  state VALUE, not just a missing target) to close the enum half
  completely.
* SAL-XLIFF-OBL-95E74FFC0501843B ("allow configurable workflow transition
  validation") had no mechanism at all: nothing let a caller check whether
  a state change between two document snapshots was legal under a
  workflow's own rules. Built as state_transitions.check_state_transitions,
  deliberately shipping no default transition policy of its own -- XLIFF
  does not mandate one, and inventing one would be exactly the proprietary
  semantics the obligation forbids.
"""

from __future__ import annotations

from format_factory.xliff import (
    Segment,
    TransitionReport,
    TransitionViolation,
    Unit,
    XliffDocument,
    XliffFile,
    check_state_transitions,
    validate,
)


def _document(*segments: Segment) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language="fr",
        children=[XliffFile(id="f", children=[Unit(id="u", children=list(segments))])],
    )


# ── The enum half: an invalid state value is rejected ───────────────────────


def test_an_invalid_state_value_is_rejected() -> None:
    document = _document(Segment(id="s", source=["hello"], state="bogus"))

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.segment.state.invalid" in codes


def test_every_spec_defined_state_value_is_accepted() -> None:
    for state in ("initial", "translated", "reviewed", "final"):
        target = ["bonjour"] if state != "initial" else None
        document = _document(Segment(id="s", source=["hello"], target=target, state=state))
        codes = {item.code for item in validate(document).diagnostics}
        assert "xliff.segment.state.invalid" not in codes


# ── check_state_transitions: the configurable half ──────────────────────────


def _segment(segment_id: str, state: str) -> Segment:
    target = ["t"] if state not in ("", "initial") else None
    return Segment(id=segment_id, source=["s"], target=target, state=state)


def test_a_transition_the_policy_permits_is_not_a_violation() -> None:
    before = _document(_segment("s1", "initial"))
    after = _document(_segment("s1", "translated"))
    policy = {"initial": frozenset({"translated"})}

    report = check_state_transitions(before, after, policy=policy)

    assert isinstance(report, TransitionReport)
    assert report.is_valid is True
    assert report.violations == ()


def test_a_transition_the_policy_forbids_is_a_violation() -> None:
    before = _document(_segment("s1", "final"))
    after = _document(_segment("s1", "initial"))
    policy = {"final": frozenset({"reviewed"})}  # final -> initial not listed

    report = check_state_transitions(before, after, policy=policy)

    assert report.is_valid is False
    (violation,) = report.violations
    assert isinstance(violation, TransitionViolation)
    assert violation.segment_id == "s1"
    assert violation.from_state == "final"
    assert violation.to_state == "initial"
    assert "s1" in violation.message
    assert "final" in violation.message


def test_a_from_state_absent_from_the_policy_permits_no_transition() -> None:
    """Fail-closed: a policy that never mentions "reviewed" as a from-state
    permits nothing away from it, including a same-looking but distinct
    target state."""
    before = _document(_segment("s1", "reviewed"))
    after = _document(_segment("s1", "final"))
    policy: dict[str, frozenset[str]] = {"initial": frozenset({"translated"})}

    report = check_state_transitions(before, after, policy=policy)

    assert report.is_valid is False
    assert report.violations[0].from_state == "reviewed"


def test_no_state_change_is_never_a_violation_even_under_an_empty_policy() -> None:
    before = _document(_segment("s1", "translated"))
    after = _document(_segment("s1", "translated"))

    report = check_state_transitions(before, after, policy={})

    assert report.is_valid is True


def test_the_wire_default_empty_state_is_normalized_to_initial() -> None:
    """Segment.state's wire-form default is "" (see model/document.py), not
    the literal string "initial" -- the obligation's own "defaulting to
    initial" language must apply to the empty form too."""
    before = _document(_segment("s1", ""))
    after = _document(_segment("s1", "translated"))
    policy = {"initial": frozenset({"translated"})}

    report = check_state_transitions(before, after, policy=policy)

    assert report.is_valid is True


def test_a_segment_added_or_removed_between_snapshots_is_not_a_transition() -> None:
    before = _document(_segment("s1", "initial"))
    after = _document(_segment("s1", "initial"), _segment("s2", "final"))

    report = check_state_transitions(before, after, policy={})

    assert report.is_valid is True


def test_multiple_independent_violations_are_all_reported() -> None:
    before = _document(_segment("s1", "initial"), _segment("s2", "initial"))
    after = _document(_segment("s1", "translated"), _segment("s2", "final"))
    policy: dict[str, frozenset[str]] = {}  # nothing permitted from "initial"

    report = check_state_transitions(before, after, policy=policy)

    assert len(report.violations) == 2
    ids = {violation.segment_id for violation in report.violations}
    assert ids == {"s1", "s2"}


def test_check_state_transitions_requires_xliff_documents() -> None:
    import pytest

    with pytest.raises(TypeError):
        check_state_transitions("not a document", _document(), policy={})  # type: ignore[arg-type]

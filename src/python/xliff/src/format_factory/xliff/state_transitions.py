"""XLIFF-STATE-001 -- configurable workflow transition validation.

MUST (SAL-XLIFF-00018, verified, "XLIFF core - translation state"): "Expose
target state and substate without inventing proprietary semantics; allow
configurable workflow transition validation."

`validation/validator.py` already exposes and enforces the spec-mandated
half: segment state is one of {initial, translated, reviewed, final}
(empty is the wire form of the default), and translated/reviewed/final
segments require a target. What was missing is the second half: XLIFF
itself does not mandate which state-to-state transitions a workflow may
perform (is translated -> initial legal? is final -> reviewed?) -- that is
deliberately left to the tool/workflow, which is exactly what "allow
configurable workflow transition validation" asks for. This module ships
the MECHANISM (compare two document snapshots, matched by segment id,
against a caller-supplied policy) and deliberately ships NO default policy
of its own -- inventing one (e.g. "final can never revert") would be
exactly the proprietary semantics the obligation forbids. An absent policy
for a from-state means every transition from it is permitted, not that the
mechanism silently does nothing: `check_state_transitions` always compares
every segment present in both snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .model import XliffDocument

#: A segment's default state, per SAL-XLIFF-00018 -- the wire form omits the
#: attribute entirely; the model stores that as "" (see model/document.py's
#: Segment.state default), never as the literal string "initial".
DEFAULT_STATE = "initial"

#: from_state -> the set of to_states a workflow permits from it. Caller-
#: supplied; this module ships none of its own.
TransitionPolicy = Mapping[str, frozenset[str]]


def _normalized_state(raw: str) -> str:
    return raw if raw else DEFAULT_STATE


@dataclass(frozen=True, slots=True)
class TransitionViolation:
    """One segment whose state change is not permitted by the policy."""

    segment_id: str
    from_state: str
    to_state: str

    @property
    def message(self) -> str:
        return (
            f"segment {self.segment_id!r} transitioned from "
            f"{self.from_state!r} to {self.to_state!r}, which the supplied "
            "policy does not permit"
        )


@dataclass(frozen=True, slots=True)
class TransitionReport:
    """Every state change between two snapshots that the policy rejects."""

    violations: tuple[TransitionViolation, ...]

    @property
    def is_valid(self) -> bool:
        return not self.violations


def _segment_states(document: XliffDocument) -> dict[str, str]:
    states: dict[str, str] = {}
    for unit in document.iter_units():
        for segment in unit.segments:
            if segment.id:
                states[segment.id] = _normalized_state(segment.state)
    return states


def check_state_transitions(
    before: XliffDocument,
    after: XliffDocument,
    *,
    policy: TransitionPolicy,
) -> TransitionReport:
    """Compare segment states between `before` and `after`, matched by
    segment id, against `policy`.

    A segment absent from either snapshot (added or removed) is not a
    transition and is not checked here -- structural add/remove is a
    different concern. `policy.get(from_state, frozenset())` means a
    from_state the policy does not mention permits no transition away from
    it (fail-closed for unmentioned states); a caller wanting "no
    restriction" for a state must say so explicitly by mapping it to every
    state it allows, including itself for "no change is always fine".
    """
    if not isinstance(before, XliffDocument):
        raise TypeError("before must be an XliffDocument")
    if not isinstance(after, XliffDocument):
        raise TypeError("after must be an XliffDocument")

    before_states = _segment_states(before)
    after_states = _segment_states(after)

    violations: list[TransitionViolation] = []
    for segment_id in sorted(set(before_states) & set(after_states)):
        from_state = before_states[segment_id]
        to_state = after_states[segment_id]
        if from_state == to_state:
            continue
        permitted = policy.get(from_state, frozenset())
        if to_state not in permitted:
            violations.append(
                TransitionViolation(
                    segment_id=segment_id, from_state=from_state, to_state=to_state
                )
            )
    return TransitionReport(violations=tuple(violations))


__all__ = [
    "DEFAULT_STATE",
    "TransitionPolicy",
    "TransitionReport",
    "TransitionViolation",
    "check_state_transitions",
]

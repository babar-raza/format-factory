"""ORA-EDIT-001 -- transactional multi-step structural edits (partial scope).

MUST: "Provide transactional add, replace, move, rename, and remove
operations for groups, layers, assets, and metadata; maintain references
and invalidate stale derived views."

required_tests: "Transaction rollback, reference repair, stale-view
invalidation, and independent application reopen tests."

Scope of this module: the "transaction rollback" half only, stated
explicitly rather than silently assumed. A single structural edit
(`dataclasses.replace()` on `OraDocument`/`OraStack`/`OraLayer`/`OraText`)
is already atomic -- ORA-LAYER-001/ORA-GROUP-001 (model/stack.py's
`__post_init__` validators) established that a rejected edit raises before
returning, so it never touches the caller's existing object. What was
missing is atomicity across a SEQUENCE of edits applied as one logical
unit: add a layer, then add its asset member, then update metadata -- if
the third step fails, the first two must not silently persist as a
half-applied document. `apply_transaction` runs a sequence of caller-
supplied `OraImage -> OraImage` steps against a working copy and only
returns a committed result if every step succeeds; any failure returns the
ORIGINAL, unmodified image plus the failure for diagnosis.

Deliberately NOT attempted here, and not claimed: "reference repair" (no
cross-element reference type exists in this package yet beyond a layer's
own `src` archive-member path -- ORA-MASK-001 and other reference-bearing
capabilities remain unbuilt, so there is nothing to repair against),
"invalidate stale derived views" (mergedimage.png/thumbnail.png have no
regeneration path at all -- this package has no rendering engine
(ORA-RENDER-001/ORA-COMPOSITE-001 are `missing`) -- inventing a "staleness"
flag with no way to ever clear it would be a hollow gesture, not a real
capability), and "independent application reopen" (covered, to the extent
this package can cover it, by the existing round-trip tests in
test_obligation_lifecycle_and_write.py; not re-proven here).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .lifecycle import OraImage

EditStep = Callable[[OraImage], OraImage]


@dataclass(frozen=True, slots=True)
class TransactionResult:
    """The outcome of applying a sequence of edit steps as one unit.

    `image` is always a valid `OraImage`: the fully-edited result when
    `committed` is True, or the untouched original when it is False --
    never a partially-applied document either way.
    """

    image: OraImage
    committed: bool
    steps_applied: int
    failure: Exception | None = None


def apply_transaction(image: OraImage, steps: Sequence[EditStep]) -> TransactionResult:
    """Apply `steps` in order against `image`, atomically.

    Each step receives the image produced by the previous step (or the
    original, for the first) and must return a new `OraImage`. If any step
    raises, or returns something that is not an `OraImage`, the whole
    sequence rolls back: the returned result carries the ORIGINAL `image`
    unchanged, `committed=False`, how many steps succeeded before the
    failure (for diagnosis), and the failure itself.
    """
    if not isinstance(image, OraImage):
        raise TypeError("image must be an OraImage")

    current = image
    applied = 0
    try:
        for step in steps:
            candidate = step(current)
            if not isinstance(candidate, OraImage):
                raise TypeError(
                    f"transaction step {applied} returned "
                    f"{type(candidate).__name__}, not an OraImage"
                )
            current = candidate
            applied += 1
    except Exception as exc:  # noqa: BLE001 -- any step failure rolls back, not just OraError
        return TransactionResult(
            image=image, committed=False, steps_applied=applied, failure=exc
        )

    return TransactionResult(image=current, committed=True, steps_applied=applied, failure=None)


__all__ = ["EditStep", "TransactionResult", "apply_transaction"]

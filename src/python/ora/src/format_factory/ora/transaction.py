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
capabilities remain unbuilt, so there is nothing to repair against), and
"independent application reopen" (covered, to the extent this package can
cover it, by the existing round-trip tests in
test_obligation_lifecycle_and_write.py; not re-proven here).

"Invalidate stale derived views" no longer has the blocker this docstring
used to name: `render.py` (FF6-ORA-RENDER-ENGINE-001) now provides a real
regeneration path -- `generate_baseline_assets(document, members)` re-
renders the current layer stack into a fresh, conforming merged image and
thumbnail, proven to reflect a committed edit rather than the pre-edit view
(`tests/python/ora/test_obligation_render_and_compositing.py::
test_regenerated_baseline_assets_reflect_a_committed_transaction_edit`).

FF6-ORA-AUTO-INVALIDATION-001: that regeneration is now also automatic.
`apply_transaction_and_refresh_baseline_assets` runs `apply_transaction`
and, only on a successful commit, regenerates and replaces the thumbnail
and merged-image members from the committed result -- a caller no longer
has to remember to call `generate_baseline_assets` themselves. Plain
`apply_transaction` is unchanged and still does not refresh anything
(cheaper, and correct for a caller who does not use the baseline assets
at all, e.g. an intermediate step in a larger pipeline); the two are
separate functions, not a flag, matching this package's own established
"separate function per distinct guarantee" style (`render`/
`render_document`, `generate_baseline_assets`/`replace_baseline_asset`).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Sequence

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

from .lifecycle import OraImage, replace_baseline_asset
from .render import generate_baseline_assets

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


def apply_transaction_and_refresh_baseline_assets(
    image: OraImage,
    steps: Sequence[EditStep],
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> TransactionResult:
    """Like `apply_transaction`, but on a successful commit also
    regenerates and replaces the thumbnail and merged-image baseline
    assets from the committed result (`render.generate_baseline_assets`
    + `lifecycle.replace_baseline_asset`), so the derived views a stale
    edit would otherwise leave behind are refreshed automatically.

    On rollback (`committed=False`), behaves identically to
    `apply_transaction`: the original `image` is returned untouched, and
    nothing is rendered -- there is nothing new to reflect.
    """
    result = apply_transaction(image, steps)
    if not result.committed:
        return result

    thumbnail, merged_image = generate_baseline_assets(
        result.image.document, result.image.members, limits=limits
    )
    refreshed = replace_baseline_asset(result.image, thumbnail=thumbnail, merged_image=merged_image)
    return replace(result, image=refreshed)


__all__ = [
    "EditStep",
    "TransactionResult",
    "apply_transaction",
    "apply_transaction_and_refresh_baseline_assets",
]

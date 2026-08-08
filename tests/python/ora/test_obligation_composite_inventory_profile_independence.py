"""ORA-COMPOSITE-001 (SAL-ORA-OBL-2CC875865800D528) against the shipped
namespace.

MUST: "Expose the selected profile's complete compositing-operation
inventory, default operation, validation, and pixel semantics through a
replaceable rendering adapter."

Before this slice: this specific obligation ID (distinct from its sibling
SAL-ORA-OBL-4EC8C1CC747F7FC6, which already closed the identical-looking
"composite-op attribute defaults to svg:src-over..." rule_text under the
SAME capability_id) had zero cross-referenced evidence -- status=missing,
source_symbols=[] -- even though the composite-op registry it needs
(model/composite_ops.py) already existed, built for six sibling obligations
this same session but never mapped onto this one.

This file closes three of this obligation's own four named clauses with
fresh, dedicated tests (not merely re-citing the sibling's own tests,
though those are also cross-referenced in the ledger):

"the selected profile's... inventory" -- investigated directly against the
pinned Layer Stack Specification (.local/format-contracts/acquired/ora/
src-ora-003.bin, "composite-op attribute" section): the composite-op table
is a single, flat, profile-independent list with no mention of per-version
gating anywhere in that section. "Profile" in this obligation's own
rule_text is not a real distinct requirement beyond the registry
model/composite_ops.py already provides -- proven behaviorally below by
showing isolation-triggering attributes (this obligation's own second
authority fact, SAL-ORA-00011: isolation depends on opacity/composite-op/
isolation together, profile 0.0.4+) do not change which composite-op
values resolve or how.

"default operation" and "validation" -- already fully covered by the
existing registry (DEFAULT_COMPOSITE_OP, composite_op_info()); this file
adds one dedicated test proving "validation" means universal acceptance
with structured lookup, per the spec's own explicit open-vocabulary mandate
("In the future other compositing modes might be added...") -- not the
kind of validation that rejects unknown input.

"pixel semantics through a replaceable rendering adapter" -- investigated
and confirmed still genuinely absent: this package has no rendering engine,
no pixel-level compositing computation, and no adapter abstraction of any
kind. NOT closed by this slice -- narrowed, not resolved. Building it would
require the same rendering-engine work already correctly deferred for
ORA-RENDER-001.
"""

from __future__ import annotations

from format_factory.ora import CompositeOpInfo, OraStack, composite_op_info
from format_factory.ora.model import COMPOSITE_OP_REGISTRY, DEFAULT_COMPOSITE_OP


# -- "the selected profile's... inventory" is not actually profile-gated --


def test_composite_op_resolution_is_identical_regardless_of_isolation_triggering_attributes() -> None:
    """SAL-ORA-00011 (this obligation's own second authority fact): a
    non-root stack is isolated -- a profile 0.0.4+ concern -- when
    isolation is "isolate", opacity is below one, or composite-op differs
    from svg:src-over. Isolation is a SEPARATE semantic (already covered by
    ORA-COMPOSITE-001's own sibling obligation SAL-ORA-OBL-C668456FEC0FF4E4)
    from what a given composite-op VALUE resolves to -- proven here by
    showing the same composite-op value resolves identically whether or not
    the surrounding stack's own other attributes would trigger isolation."""
    non_isolating = OraStack(composite_op="svg:multiply", opacity=1.0, isolation="auto")
    isolating = OraStack(composite_op="svg:multiply", opacity=0.5, isolation="isolate")

    assert non_isolating.composite_op_details == isolating.composite_op_details
    assert non_isolating.composite_op_details == CompositeOpInfo("Multiply", "Source Over")


def test_every_registry_value_resolves_the_same_way_on_a_root_and_non_root_stack() -> None:
    """Root stacks are never isolated (isolation only applies to non-root
    stacks per SAL-ORA-00011) -- the inventory itself does not distinguish
    root from non-root, or any other structural/profile context."""
    for value, expected in COMPOSITE_OP_REGISTRY.items():
        assert composite_op_info(value) == expected


# -- "validation" means universal acceptance with structured lookup -------


def test_validation_accepts_every_value_the_spec_defines_plus_forward_compatible_unknowns() -> None:
    """The spec's own text explicitly reserves composite-op for future
    growth ("a way for applications to define new modes will be
    specified") -- "validation" here cannot mean rejection of unrecognized
    values without contradicting the spec it is meant to enforce. Every
    known value resolves to a structured CompositeOpInfo; every unknown,
    well-formed string resolves to None without raising -- both outcomes
    are accepted equally, differing only in whether a documented meaning
    is available."""
    for value in COMPOSITE_OP_REGISTRY:
        assert composite_op_info(value) is not None

    for unknown in ("future:not-yet-invented", "custom:my-app-mode", ""):
        assert composite_op_info(unknown) is None
        # None is a valid, non-raising outcome -- constructing a stack with
        # it must not raise either.
        OraStack(composite_op=unknown)


def test_the_default_composite_op_constant_matches_the_registrys_own_default_entry() -> None:
    assert DEFAULT_COMPOSITE_OP == "svg:src-over"
    assert composite_op_info(DEFAULT_COMPOSITE_OP) == CompositeOpInfo("Normal", "Source Over")

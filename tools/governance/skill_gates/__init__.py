"""Skill gates — executable pre-execution checks invoked by governed skills.

These modules are the SINGLE implementation of three defect-class checks that
both (a) the skills invoke at creation time, and (b) the governance validators
V249/V250/V251 are expected to import at sprint time.

    import_hygiene      -> sys.path mutation detection (AST + alias resolution)
    namespace_collision -> stdlib / popular-package package-name collision
    converter_compat    -> converter information-model compatibility

DESIGN RULE (EP-3, anti-drift): the rules live here once. A validator that
re-implements them will drift from the skill gate and the two will disagree.
V249/V250/V251 should call the `check_*` functions in these modules rather than
copying the logic. See `docs/governance/skill-gate-validator-seam.md`.

Enforcement honesty: importing/running these modules produces a deterministic
verdict, but nothing in this package forces a skill to call it. Blocking power
comes from the caller (a validator with blocks_sprint=True, or a git hook).
"""
from __future__ import annotations

__all__ = ["import_hygiene", "namespace_collision", "converter_compat"]

"""
governance_block_registry.py — Machine-readable registry of structural GOV_BLOCK validators.

TC-CQGA2-R1 (mutable-exploring-hellman / CQGA-002)

Replaces the 2-item hardcoded set in check_continuation.py with a single authoritative
registry. CLAUDE.md and check_continuation.py previously diverged (CLAUDE.md listed 4
validators; code checked 2). This module is the canonical truth.

Rules:
- Validators in STRUCTURAL_GOV_BLOCKS produce a hard-stop when they appear in rework_items.
- The Supreme Directive "log exit 3 and continue" does NOT apply to these validators.
- To add a new structural blocker: add it here + update CLAUDE.md §GOV_BLOCK Exception.
- To change an enforcement level from FAIL to WARN: create a gap entry (REQ-CQGA2-004).

See: docs/code-quality/enforcement-level-change-policy.md
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Structural GOV_BLOCK validators
# ---------------------------------------------------------------------------
# These are HARD_STOP conditions. Product deepening is blocked until the root
# cause is resolved via an analytics-separation or architecture-repair sprint.

STRUCTURAL_GOV_BLOCKS: frozenset[str] = frozenset(
    [
        # Original 2 (wired in code since TC-GOVBLK-001)
        "GOV_BLOCK:monolith_detection_validator",
        "GOV_BLOCK:validate_source_architecture",
        # Added by TC-CQGA2-R1: align with CLAUDE.md §GOV_BLOCK Exception
        "GOV_BLOCK:validate_multi_responsibility_file",
        "GOV_BLOCK:validate_analytics_naming_enforced",
        # Stub enforcement — new source files must not be stubs (V149)
        "GOV_BLOCK:validate_source_stubs",
        # Promotion integrity — PROMOTED_STABLE files changed without reopening (V119)
        # REQ-STRUCT-003 (memoized-frolicking-donut / GOV-HEAL-001)
        "GOV_BLOCK:validate_promoted_code_changed_without_reopening",
    ]
)

# ---------------------------------------------------------------------------
# Structural GOV_BLOCK stop-reason (shared constant)
# ---------------------------------------------------------------------------
# check_continuation.py emits this exact reason string when filter_structural_blocks()
# finds a non-empty structural block; sprint_executor.py checks incoming reason strings
# against it before deciding whether a STOP is overridable. Both import this constant
# (rather than each hand-typing the literal) so a rename in one file becomes an
# ImportError/NameError at load time instead of a silent runtime mismatch that would
# reopen the override loophole TC-EXT-010 closed.
STRUCTURAL_GOVBLOCK_STOP_REASON: str = "structural_govblock_must_be_resolved_first"

# ---------------------------------------------------------------------------
# Enforcement-level change policy (REQ-CQGA2-004)
# ---------------------------------------------------------------------------
# Any demotion from blocks_sprint=True → blocks_sprint=False requires:
#   1. A gap ledger entry with disposition=ACKNOWLEDGED_BY_DESIGN
#   2. A reference in the commit message: "closes CQG-NNN"
# CI-pressure demotions are prohibited.
#
# Policy document: docs/code-quality/enforcement-level-change-policy.md
ENFORCEMENT_LEVEL_CHANGE_POLICY_PATH = (
    "docs/code-quality/enforcement-level-change-policy.md"
)

# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def is_structural_block(rework_item: str) -> bool:
    """Return True if *rework_item* is a structural GOV_BLOCK that hard-stops sprints."""
    return any(
        rework_item.startswith(vname) or rework_item == vname
        for vname in STRUCTURAL_GOV_BLOCKS
    )


def filter_structural_blocks(rework_items: list[str]) -> list[str]:
    """Return only the structural GOV_BLOCK items from *rework_items*."""
    return [item for item in rework_items if is_structural_block(item)]

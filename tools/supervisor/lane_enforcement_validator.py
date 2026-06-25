"""lane_enforcement_validator.py — Lane enforcement validator (FAIL, not WARN).

TC-GAP-A04: Checks evidence declarations for cross-lane file ownership violations.
Returns FAIL on violations, PASS otherwise.

Lane ownership rules:
- Each lane owns specific file path prefixes
- Files edited by a declaration must belong to the lane specified in the declaration
- Cross-lane edits produce FAIL verdicts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Paths that are exempt from lane enforcement.
# These files are modified as standard bookkeeping in EVERY product sprint
# regardless of which product lane is being targeted. They must not contribute
# to multi-lane spread counts or trigger cross-lane violations.
GLOBAL_EXEMPT_PATHS: list[str] = [
    "reports/capability-layer/gap-ledger.json",
    "registry/source-structure-baseline.json",
    "reports/r90/product-code-change-ledger.json",
    "reports/supervisor/",
    ".local/",
    ".supervisor/",
]


# Default lane ownership rules (path prefix → lane)
DEFAULT_LANE_OWNERSHIP: dict[str, str] = {
    "tools/specification-authority-layer/": "SAL",
    "tools/requirements_authority/": "REQUIREMENTS",
    "tools/supervisor/": "SUPERVISOR",
    "src/python/": "PYTHON_PRODUCT",
    "src/net/": "DOTNET_PRODUCT",
    "tests/python/": "PYTHON_PRODUCT",
    "tests/net/": "DOTNET_PRODUCT",
    "tests/supervisor/": "SUPERVISOR",
    "reports/": "REPORTING",
    ".supervisor/": "GOVERNANCE",
    "registry/": "GOVERNANCE",
    "examples/": "DOGFOOD",
}


@dataclass
class LaneEnforcementResult:
    """Result of lane enforcement validation."""
    passed: bool
    violations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"LaneEnforcementValidator: {status}"]
        for e in self.evidence:
            lines.append(f"  [OK] {e}")
        for v in self.violations:
            lines.append(f"  [FAIL] {v}")
        return "\n".join(lines)


class LaneEnforcementValidator:
    """Validates evidence declarations for cross-lane file ownership violations."""

    def __init__(self, lane_ownership: dict[str, str] | None = None):
        self.lane_ownership = lane_ownership or DEFAULT_LANE_OWNERSHIP

    def _resolve_lane(self, file_path: str) -> str | None:
        """Determine which lane owns a file path.

        Returns None for globally exempt paths — these are excluded from
        both multi-lane spread counts and cross-lane violation checks.
        """
        normalized = file_path.replace("\\", "/")
        for exempt in GLOBAL_EXEMPT_PATHS:
            if normalized.startswith(exempt) or normalized == exempt.rstrip("/"):
                return None
        for prefix, lane in sorted(
            self.lane_ownership.items(), key=lambda x: -len(x[0])
        ):
            if normalized.startswith(prefix):
                return lane
        return None

    def validate(
        self,
        declaration: dict[str, Any],
        declared_lane: str | None = None,
    ) -> LaneEnforcementResult:
        """Validate that all changed files belong to the declared lane.

        Args:
            declaration: Evidence declaration dict with changed_files or
                         planned_work_items containing changed_files.
            declared_lane: The lane this sprint claims to operate in.
                           If None, cross-lane checking is skipped but
                           multi-lane spread is still detected.
        """
        result = LaneEnforcementResult(passed=True)

        # Collect all changed files from declaration
        changed_files: list[str] = []
        for f in declaration.get("changed_files", []):
            changed_files.append(f)
        for item in declaration.get("planned_work_items", []):
            for f in item.get("changed_files", []):
                if f not in changed_files:
                    changed_files.append(f)

        if not changed_files:
            result.evidence.append("No changed files in declaration")
            return result

        # Map files to lanes
        file_lanes: dict[str, str | None] = {}
        for f in changed_files:
            file_lanes[f] = self._resolve_lane(f)

        # Check against declared lane
        if declared_lane and declared_lane.upper() != "MULTI_LANE":
            for f, lane in file_lanes.items():
                if lane and lane != declared_lane:
                    result.passed = False
                    result.violations.append(
                        f"File '{f}' belongs to lane '{lane}' but declaration "
                        f"claims lane '{declared_lane}'"
                    )
                elif lane == declared_lane:
                    result.evidence.append(f"File '{f}' → lane '{lane}' (matches)")
                else:
                    result.evidence.append(f"File '{f}' → no lane ownership defined")
        else:
            # No declared lane (or MULTI_LANE declared) — check for multi-lane spread
            lanes_touched = {l for l in file_lanes.values() if l}
            if declared_lane and declared_lane.upper() == "MULTI_LANE":
                # Multi-lane sprint: allow any number of lanes, just report
                result.evidence.append(
                    f"Multi-lane sprint declared. Lanes touched: {sorted(lanes_touched)}"
                )
            elif len(lanes_touched) > 2:
                result.passed = False
                result.violations.append(
                    f"Declaration touches {len(lanes_touched)} lanes without "
                    f"declaring a lane: {sorted(lanes_touched)}"
                )
            else:
                result.evidence.append(
                    f"Declaration touches {len(lanes_touched)} lane(s): "
                    f"{sorted(lanes_touched)}"
                )

        return result

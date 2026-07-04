"""Gap Ledger Hygiene Tool (TC-C3, playful-swimming-stearns).

Detects orphaned gap ledger entries — entries that are open but reference
capabilities that no longer exist in the active system, or entries that
were created for suspended capabilities.

Usage:
    python gap_ledger_hygiene.py --ledger <path> [--apply] [--output <path>]

    --apply   Apply closures (mark orphaned entries as DEFERRED_BY_DESIGN).
              Without this flag, runs in dry-run mode.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Orphan detection patterns
# ---------------------------------------------------------------------------

# Suspended capability patterns — any open gap matching these is an orphan.
# Source: MEMORY.md "Product Deepening Rotation — SUSPENDED (2026-06-18)"
SUSPENDED_CAPABILITY_PATTERNS: list[str] = [
    "_mod_prime_times_multiplier",
    "_mod_",
    "arithmetic_analytics_rotation",
]

# Known-suspended format+capability combinations
# Format: (format_prefix, capability_keyword)
SUSPENDED_FORMAT_CAPABILITIES: list[tuple[str, str]] = [
    ("ZST", "_mod_"),
    ("XCF", "_mod_"),
    ("FODG", "_mod_"),
]


@dataclass
class OrphanedEntry:
    gap_id: str
    format: str
    capability_name: str
    status: str
    reason: str
    orphan_type: str  # "suspended_capability" | "stale_reference" | "deferred_format"

    def to_dict(self) -> dict:
        return {
            "gap_id": self.gap_id,
            "format": self.format,
            "capability_name": self.capability_name,
            "status": self.status,
            "reason": self.reason,
            "orphan_type": self.orphan_type,
        }


@dataclass
class CleanupResult:
    applied: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "applied": self.applied,
            "skipped": self.skipped,
            "errors": self.errors,
        }


class GapLedgerHygiene:
    """Detect and optionally close orphaned gap ledger entries."""

    def load_ledger(self, ledger_path: Path) -> tuple[dict, list[dict]]:
        """Load ledger JSON. Returns (full_data, gaps_list)."""
        raw = ledger_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
        if isinstance(data, list):
            return {}, data
        gaps = data.get("gaps", [])
        return data, gaps

    def find_orphaned_entries(self, ledger_path: Path, repo_root: Path) -> list[OrphanedEntry]:
        """Find orphaned entries in the gap ledger.

        An entry is orphaned when:
        1. Status is "open" AND the capability matches a suspended rotation pattern
        2. Status is "open" AND the entry's format/capability combination is in the
           known-suspended list (ZST/XCF/FODG arithmetic rotation)

        NOTE: The gap ledger's related_capability_id refers to product source capabilities
        (format-specific), NOT the agent/skill capability registry. Do not cross-reference
        against .governance/capabilities/registry.yaml for orphan detection.
        """
        _, gaps = self.load_ledger(ledger_path)
        open_gaps = [g for g in gaps if g.get("status", "").lower() == "open"]

        orphans: list[OrphanedEntry] = []
        for gap in open_gaps:
            gap_id = gap.get("gap_id", "")
            fmt = gap.get("format", "")
            cap_name = gap.get("capability_name", "")

            # Check 1: suspended analytics rotation patterns in gap_id or capability_name
            combined = f"{gap_id} {cap_name}".lower()
            matched_pattern = False
            for pattern in SUSPENDED_CAPABILITY_PATTERNS:
                if pattern.lower() in combined:
                    orphans.append(OrphanedEntry(
                        gap_id=gap_id,
                        format=fmt,
                        capability_name=cap_name,
                        status="open",
                        reason=f"Matches suspended rotation pattern '{pattern}'",
                        orphan_type="suspended_capability",
                    ))
                    matched_pattern = True
                    break

            if not matched_pattern:
                # Check 2: known-suspended format+capability combination
                for susp_fmt, susp_kw in SUSPENDED_FORMAT_CAPABILITIES:
                    if fmt.upper() == susp_fmt and susp_kw.lower() in cap_name.lower():
                        orphans.append(OrphanedEntry(
                            gap_id=gap_id,
                            format=fmt,
                            capability_name=cap_name,
                            status="open",
                            reason=f"Format {susp_fmt} capability '{susp_kw}' is suspended",
                            orphan_type="deferred_format",
                        ))
                        break

        return orphans

    def report(self, orphans: list[OrphanedEntry], output_path: Path) -> None:
        """Write orphan report. Never auto-closes without --apply."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        by_type: dict[str, int] = {}
        for o in orphans:
            by_type[o.orphan_type] = by_type.get(o.orphan_type, 0) + 1

        report_data = {
            "total_orphans": len(orphans),
            "by_type": by_type,
            "orphans": [o.to_dict() for o in orphans],
            "note": "Dry-run only. Use --apply to close these entries.",
        }
        output_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        print(f"  Orphan report: {output_path} ({len(orphans)} orphans)")

    def apply_closures(
        self, orphans: list[OrphanedEntry], ledger_path: Path
    ) -> CleanupResult:
        """Mark orphaned entries as DEFERRED_BY_DESIGN. Requires explicit --apply flag."""
        result = CleanupResult()
        try:
            data, gaps = self.load_ledger(ledger_path)

            orphan_ids = {o.gap_id for o in orphans}
            for gap in gaps:
                if gap.get("gap_id") in orphan_ids:
                    gap["status"] = "DEFERRED_BY_DESIGN"
                    gap["deferred_reason"] = next(
                        (o.reason for o in orphans if o.gap_id == gap["gap_id"]), "orphaned"
                    )
                    result.applied += 1

            # Write back
            if isinstance(data, dict):
                data["gaps"] = gaps
                output = data
            else:
                output = gaps

            ledger_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
            print(f"  Applied {result.applied} closures to {ledger_path}")
        except Exception as e:
            result.errors.append(str(e))
            print(f"  ERROR applying closures: {e}")

        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Gap Ledger Hygiene Tool")
    parser.add_argument("--ledger", default="reports/capability-layer/gap-ledger.json",
                        help="Path to gap ledger JSON")
    parser.add_argument("--output", default="reports/assurance/gap-ledger-orphan-report.json",
                        help="Path for orphan report output")
    parser.add_argument("--apply", action="store_true",
                        help="Apply closures (mark orphans as DEFERRED_BY_DESIGN)")
    parser.add_argument("--repo-root", default=".",
                        help="Repository root for capability registry lookup")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ledger_path = repo_root / args.ledger if not Path(args.ledger).is_absolute() else Path(args.ledger)
    output_path = repo_root / args.output if not Path(args.output).is_absolute() else Path(args.output)

    hygiene = GapLedgerHygiene()
    print(f"Scanning: {ledger_path}")
    orphans = hygiene.find_orphaned_entries(ledger_path, repo_root)
    print(f"Found {len(orphans)} orphaned entries")

    hygiene.report(orphans, output_path)

    if args.apply and orphans:
        print(f"Applying {len(orphans)} closures...")
        result = hygiene.apply_closures(orphans, ledger_path)
        print(f"Done: applied={result.applied}, errors={len(result.errors)}")
    elif not args.apply:
        print("Dry-run mode. Use --apply to apply closures.")


if __name__ == "__main__":
    main()

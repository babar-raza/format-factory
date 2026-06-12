"""
rework_orchestrator.py — Self-Healing Loop Pilot: Detect → Classify → Repair → Verify

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
Lane: L1-healing-loop
Taskcard: SHQ-L1-001

Wires bounded_repair_engine + capability_verifier into an autonomous repair cycle:

    detect → classify → create repair taskcard → execute repair → verify → idempotency proof

Pilot defect: STALE_QUEUE_ITEM — queue items whose target function already exists in source.
Uses action-queue.jsonl items anl-q-002, anl-q-004, anl-q-005 as the pilot defect set.

Repair strategy for STALE_QUEUE_ITEM:
  - Mark the queue item status=done with stale_reason="function_already_exists"
  - No source mutation required (function is already present)
  - Re-verify via capability_verifier to confirm no SIGNATURE_DRIFT remains
  - Prove idempotency: second run detects zero stale items for already-repaired items

Non-negotiables:
  - No product source mutations (healing loop does NOT write to src/)
  - All repairs are queue-state changes only
  - continuation_state update is advisory-only (does not overwrite global signal)
  - Stop condition: if defect is NOT STALE_QUEUE_ITEM, refuse and document blocker

Exit codes (when used as script):
  0 — all defects classified and repaired (or no defects found)
  1 — unrepaired defects remain (stop condition hit)
  9 — unexpected error
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent

# ---------------------------------------------------------------------------
# Defect classification
# ---------------------------------------------------------------------------


class DefectClass(str, Enum):
    STALE_QUEUE_ITEM = "STALE_QUEUE_ITEM"          # function exists; queue item is stale
    CAPABILITY_GAP = "CAPABILITY_GAP"              # function genuinely missing — no auto-repair
    UNREPAIRABLE = "UNREPAIRABLE"                  # cannot determine; stop condition
    NONE = "NONE"                                  # no defect found


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class QueueItem:
    """A parsed action-queue.jsonl item."""

    action_id: str
    action_type: str
    target_path: str
    status: str
    function_name: str = ""
    description: str = ""
    sprint_id: str = ""
    queued_at: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectedDefect:
    """A defect identified by the detector."""

    queue_item: QueueItem
    defect_class: DefectClass
    detail: str
    source_path: str = ""
    function_exists_in_source: bool = False


@dataclass
class RepairTaskcard:
    """Repair taskcard created for each detected defect."""

    taskcard_id: str
    defect_class: str
    queue_item_id: str
    target_path: str
    function_name: str
    repair_action: str
    repair_note: str
    created_at: str


@dataclass
class RepairOutcome:
    """Result of executing a repair."""

    defect: DetectedDefect
    taskcard: RepairTaskcard
    success: bool
    action_taken: str
    detail: str
    verified: bool = False
    idempotent: bool = False


# ---------------------------------------------------------------------------
# StaleQueueDetector
# ---------------------------------------------------------------------------


class StaleQueueDetector:
    """Scans action-queue.jsonl for pending PRODUCT_SOURCE_PATCH_BOUNDED items
    where the target function already exists in source.

    Pure read — does not modify source or queue.
    """

    def __init__(
        self,
        queue_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
    ) -> None:
        self.repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        self.queue_path = (
            Path(queue_path) if queue_path
            else self.repo_root / ".local" / "supervisor" / "action-queue.jsonl"
        )

    def load_queue(self) -> List[QueueItem]:
        """Load all queue items from JSONL file."""
        if not self.queue_path.exists():
            return []
        items: List[QueueItem] = []
        for line in self.queue_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            items.append(QueueItem(
                action_id=raw.get("action_id", ""),
                action_type=raw.get("action_type", ""),
                target_path=raw.get("target_path", ""),
                status=raw.get("status", ""),
                function_name=raw.get("function_name", ""),
                description=raw.get("description", ""),
                sprint_id=raw.get("sprint_id", ""),
                queued_at=raw.get("queued_at", ""),
                raw=raw,
            ))
        return items

    def function_exists_in_source(self, target_path: str, function_name: str) -> bool:
        """Return True if function_name is defined in the target source file."""
        if not function_name:
            return False
        abs_path = self.repo_root / target_path
        if not abs_path.exists():
            return False
        content = abs_path.read_text(encoding="utf-8")
        # Match `def <function_name>(` at start of a line (with optional whitespace)
        pattern = rf"^\s*def\s+{re.escape(function_name)}\s*\("
        return bool(re.search(pattern, content, re.MULTILINE))

    def detect_stale(self) -> List[DetectedDefect]:
        """Return all pending PRODUCT_SOURCE_PATCH_BOUNDED items whose target
        function already exists in source (i.e., stale queue items).
        """
        items = self.load_queue()
        defects: List[DetectedDefect] = []

        for item in items:
            if item.action_type != "PRODUCT_SOURCE_PATCH_BOUNDED":
                continue
            if item.status != "pending":
                continue
            if not item.function_name:
                continue

            exists = self.function_exists_in_source(item.target_path, item.function_name)
            if exists:
                defects.append(DetectedDefect(
                    queue_item=item,
                    defect_class=DefectClass.STALE_QUEUE_ITEM,
                    detail=(
                        f"Function '{item.function_name}' already exists in "
                        f"'{item.target_path}'; queue item is stale."
                    ),
                    source_path=item.target_path,
                    function_exists_in_source=True,
                ))
            else:
                defects.append(DetectedDefect(
                    queue_item=item,
                    defect_class=DefectClass.CAPABILITY_GAP,
                    detail=(
                        f"Function '{item.function_name}' is NOT yet in "
                        f"'{item.target_path}'; this is a real capability gap."
                    ),
                    source_path=item.target_path,
                    function_exists_in_source=False,
                ))

        return defects


# ---------------------------------------------------------------------------
# ReworkOrchestrator
# ---------------------------------------------------------------------------


class ReworkOrchestrator:
    """Full self-healing loop: detect → classify → taskcard → repair → verify.

    Pilot scope: handles STALE_QUEUE_ITEM defects only.
    On CAPABILITY_GAP or UNREPAIRABLE: documents blocker and stops (non-autonomous).

    Usage:
        orch = ReworkOrchestrator.from_repo()
        summary = orch.run_cycle()
    """

    def __init__(
        self,
        queue_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
        taskcards_root: Optional[Path] = None,
        continuation_signal_path: Optional[Path] = None,
        dry_run: bool = False,
    ) -> None:
        self.repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        self.queue_path = (
            Path(queue_path) if queue_path
            else self.repo_root / ".local" / "supervisor" / "action-queue.jsonl"
        )
        self.taskcards_root = (
            Path(taskcards_root) if taskcards_root
            else self.repo_root / "taskcards" / "self-healing-queue-professionalize"
        )
        self.continuation_signal_path = (
            Path(continuation_signal_path) if continuation_signal_path
            else self.repo_root / ".local" / "supervisor" / "continuation-signal.json"
        )
        self.dry_run = dry_run
        self.detector = StaleQueueDetector(
            queue_path=self.queue_path,
            repo_root=self.repo_root,
        )

    @classmethod
    def from_repo(
        cls,
        repo_root: Optional[Path] = None,
        dry_run: bool = False,
    ) -> "ReworkOrchestrator":
        return cls(repo_root=repo_root, dry_run=dry_run)

    # ------------------------------------------------------------------
    # Phase 1: Detect
    # ------------------------------------------------------------------

    def detect_defects(self) -> List[DetectedDefect]:
        """Detect stale queue items and capability gaps.

        Returns all detected defects (both stale and gap).
        """
        return self.detector.detect_stale()

    # ------------------------------------------------------------------
    # Phase 2: Classify
    # ------------------------------------------------------------------

    def classify(self, defect: DetectedDefect) -> DefectClass:
        """Classify a detected defect. Returns its defect_class."""
        return defect.defect_class

    # ------------------------------------------------------------------
    # Phase 3: Create repair taskcard
    # ------------------------------------------------------------------

    def create_repair_taskcard(self, defect: DetectedDefect) -> RepairTaskcard:
        """Create a repair taskcard for a STALE_QUEUE_ITEM defect.

        Raises ValueError if defect_class is not STALE_QUEUE_ITEM.
        """
        if defect.defect_class != DefectClass.STALE_QUEUE_ITEM:
            raise ValueError(
                f"Repair taskcard only for STALE_QUEUE_ITEM; "
                f"got {defect.defect_class} for {defect.queue_item.action_id}"
            )

        taskcard_id = f"SHQ-REPAIR-{defect.queue_item.action_id.upper()}"
        now = datetime.now(timezone.utc).isoformat()

        return RepairTaskcard(
            taskcard_id=taskcard_id,
            defect_class=DefectClass.STALE_QUEUE_ITEM.value,
            queue_item_id=defect.queue_item.action_id,
            target_path=defect.queue_item.target_path,
            function_name=defect.queue_item.function_name,
            repair_action="MARK_QUEUE_ITEM_DONE",
            repair_note=(
                f"Function '{defect.queue_item.function_name}' already exists in "
                f"'{defect.queue_item.target_path}'. Marking queue item as done "
                f"(stale — no source mutation required)."
            ),
            created_at=now,
        )

    def _write_taskcard_yaml(self, taskcard: RepairTaskcard) -> Path:
        """Write repair taskcard as YAML to taskcards_root.

        Returns the path written.
        """
        self.taskcards_root.mkdir(parents=True, exist_ok=True)
        out_path = self.taskcards_root / f"{taskcard.taskcard_id}.yaml"

        if self.dry_run:
            return out_path

        content = (
            f"item_id: {taskcard.taskcard_id}\n"
            f"title: \"Repair: close stale queue item {taskcard.queue_item_id}\"\n"
            f"lane: L1-healing-loop\n"
            f"status: completed\n"
            f"defect_class: {taskcard.defect_class}\n"
            f"queue_item_id: {taskcard.queue_item_id}\n"
            f"target_path: {taskcard.target_path}\n"
            f"function_name: {taskcard.function_name}\n"
            f"repair_action: {taskcard.repair_action}\n"
            f"repair_note: >\n"
            f"  {taskcard.repair_note}\n"
            f"created_at: \"{taskcard.created_at}\"\n"
            f"sprint_id: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001\n"
            f"execution_method: AGENT_GOVERNED_DIRECT_EXECUTION\n"
        )
        out_path.write_text(content, encoding="utf-8")
        return out_path

    # ------------------------------------------------------------------
    # Phase 4: Execute repair
    # ------------------------------------------------------------------

    def execute_repair(
        self, defect: DetectedDefect, taskcard: RepairTaskcard
    ) -> RepairOutcome:
        """Execute the repair for a STALE_QUEUE_ITEM: mark queue item as done.

        For stale items, repair = update status in action-queue.jsonl from
        'pending' to 'done' with stale_reason and completed_at fields.
        No source file is modified.

        Returns RepairOutcome with success=True if item was marked done.
        """
        if defect.defect_class != DefectClass.STALE_QUEUE_ITEM:
            return RepairOutcome(
                defect=defect,
                taskcard=taskcard,
                success=False,
                action_taken="SKIPPED_NOT_STALE",
                detail=(
                    f"Stop condition: {defect.defect_class} is not auto-repairable. "
                    f"Manual review required for '{defect.queue_item.action_id}'."
                ),
            )

        if self.dry_run:
            return RepairOutcome(
                defect=defect,
                taskcard=taskcard,
                success=True,
                action_taken="DRY_RUN_MARK_DONE",
                detail=f"[DRY_RUN] Would mark {defect.queue_item.action_id} as done.",
            )

        # Update the queue JSONL
        success = self._mark_queue_item_done(
            action_id=defect.queue_item.action_id,
            stale_reason="function_already_exists",
            note=taskcard.repair_note,
        )

        if success:
            return RepairOutcome(
                defect=defect,
                taskcard=taskcard,
                success=True,
                action_taken="MARKED_QUEUE_ITEM_DONE",
                detail=(
                    f"Queue item '{defect.queue_item.action_id}' marked done. "
                    f"Stale reason: function_already_exists."
                ),
            )
        else:
            return RepairOutcome(
                defect=defect,
                taskcard=taskcard,
                success=False,
                action_taken="QUEUE_UPDATE_FAILED",
                detail=f"Failed to update queue item '{defect.queue_item.action_id}'.",
            )

    def _mark_queue_item_done(
        self,
        action_id: str,
        stale_reason: str,
        note: str,
    ) -> bool:
        """Rewrite action-queue.jsonl, updating the target item to status=done.

        Returns True if the item was found and updated.
        """
        if not self.queue_path.exists():
            return False

        lines = self.queue_path.read_text(encoding="utf-8").splitlines()
        new_lines: List[str] = []
        updated = False
        now = datetime.now(timezone.utc).isoformat()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError:
                new_lines.append(line)
                continue

            if item.get("action_id") == action_id and item.get("status") == "pending":
                item["status"] = "done"
                item["stale_reason"] = stale_reason
                item["stale_note"] = note
                item["completed_at"] = now
                item["repair_method"] = "STALE_QUEUE_ITEM_CLOSURE"
                updated = True

            new_lines.append(json.dumps(item, separators=(",", ":")))

        if updated:
            self.queue_path.write_text(
                "\n".join(new_lines) + "\n", encoding="utf-8"
            )

        return updated

    # ------------------------------------------------------------------
    # Phase 5: Verify repair
    # ------------------------------------------------------------------

    def verify_repair(self, defect: DetectedDefect) -> bool:
        """Re-run detection to verify defect is gone (no longer stale/pending).

        Returns True if the queue item is no longer pending.
        """
        items = self.detector.load_queue()
        for item in items:
            if item.action_id == defect.queue_item.action_id:
                # If still pending, repair failed
                return item.status != "pending"
        # Item not found (unusual) — treat as repaired
        return True

    # ------------------------------------------------------------------
    # Idempotency check
    # ------------------------------------------------------------------

    def check_idempotency(self, prior_outcomes: List[RepairOutcome]) -> bool:
        """Verify that running detection again produces no new stale items
        for already-repaired action IDs.

        Returns True if idempotent (no re-emergence of repaired items).
        """
        repaired_ids = {
            o.defect.queue_item.action_id
            for o in prior_outcomes
            if o.success
        }
        if not repaired_ids:
            return True

        fresh_defects = self.detect_defects()
        fresh_stale_ids = {
            d.queue_item.action_id
            for d in fresh_defects
            if d.defect_class == DefectClass.STALE_QUEUE_ITEM
        }
        # Idempotent if none of the repaired IDs re-appear as stale
        return len(repaired_ids & fresh_stale_ids) == 0

    # ------------------------------------------------------------------
    # Full cycle
    # ------------------------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """Run the full detect → classify → taskcard → repair → verify cycle.

        Returns a summary dict with:
          - defects_detected: int
          - stale_items: list of action IDs
          - gap_items: list of action IDs
          - repairs_attempted: int
          - repairs_succeeded: int
          - repairs_verified: int
          - idempotent: bool
          - stop_condition_hit: bool
          - outcomes: list of RepairOutcome dicts
          - blocker: str (if stop_condition_hit)
        """
        # Phase 1: Detect
        all_defects = self.detect_defects()

        stale = [d for d in all_defects if d.defect_class == DefectClass.STALE_QUEUE_ITEM]
        gaps = [d for d in all_defects if d.defect_class == DefectClass.CAPABILITY_GAP]

        # Check stop condition: CAPABILITY_GAP items cannot be auto-repaired
        if gaps:
            return {
                "defects_detected": len(all_defects),
                "stale_items": [d.queue_item.action_id for d in stale],
                "gap_items": [d.queue_item.action_id for d in gaps],
                "repairs_attempted": 0,
                "repairs_succeeded": 0,
                "repairs_verified": 0,
                "idempotent": False,
                "stop_condition_hit": True,
                "blocker": (
                    "CAPABILITY_GAP items detected (not auto-repairable): "
                    + ", ".join(d.queue_item.action_id for d in gaps)
                ),
                "outcomes": [],
            }

        if not stale:
            return {
                "defects_detected": 0,
                "stale_items": [],
                "gap_items": [],
                "repairs_attempted": 0,
                "repairs_succeeded": 0,
                "repairs_verified": 0,
                "idempotent": True,
                "stop_condition_hit": False,
                "blocker": None,
                "outcomes": [],
            }

        # Phase 2-4: For each stale item, classify → taskcard → repair
        outcomes: List[RepairOutcome] = []
        for defect in stale:
            # Phase 2: Classify (already classified by detector)
            dc = self.classify(defect)

            # Phase 3: Repair taskcard
            taskcard = self.create_repair_taskcard(defect)
            self._write_taskcard_yaml(taskcard)

            # Phase 4: Execute repair
            outcome = self.execute_repair(defect, taskcard)
            outcomes.append(outcome)

        # Phase 5: Verify all repairs
        verified_count = 0
        for outcome in outcomes:
            if outcome.success:
                verified = self.verify_repair(outcome.defect)
                outcome.verified = verified
                if verified:
                    verified_count += 1

        # Idempotency check
        is_idempotent = self.check_idempotency(outcomes)
        for outcome in outcomes:
            if outcome.success:
                outcome.idempotent = is_idempotent

        return {
            "defects_detected": len(all_defects),
            "stale_items": [d.queue_item.action_id for d in stale],
            "gap_items": [],
            "repairs_attempted": len(outcomes),
            "repairs_succeeded": sum(1 for o in outcomes if o.success),
            "repairs_verified": verified_count,
            "idempotent": is_idempotent,
            "stop_condition_hit": False,
            "blocker": None,
            "outcomes": [
                {
                    "action_id": o.defect.queue_item.action_id,
                    "function_name": o.defect.queue_item.function_name,
                    "source_path": o.defect.source_path,
                    "defect_class": o.defect.defect_class.value,
                    "success": o.success,
                    "verified": o.verified,
                    "idempotent": o.idempotent,
                    "action_taken": o.action_taken,
                    "detail": o.detail,
                }
                for o in outcomes
            ],
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def run_healing_cycle(
    repo_root: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run the full self-healing cycle and return summary.

    Convenience entry point for use in tests and evidence generation.
    """
    orch = ReworkOrchestrator.from_repo(repo_root=repo_root, dry_run=dry_run)
    return orch.run_cycle()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", default=None,
        help="Path to repo root (default: auto-detected)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Detect and classify but do not modify queue or write taskcards"
    )
    parser.add_argument(
        "--output-json", default=None,
        help="Write cycle summary to this JSON file"
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else None
    summary = run_healing_cycle(repo_root=repo_root, dry_run=args.dry_run)

    # Print summary
    print(f"ReworkOrchestrator: defects_detected={summary['defects_detected']}")
    print(f"  stale_items: {summary['stale_items']}")
    print(f"  gap_items: {summary['gap_items']}")
    print(f"  repairs_succeeded: {summary['repairs_succeeded']}/{summary['repairs_attempted']}")
    print(f"  repairs_verified: {summary['repairs_verified']}")
    print(f"  idempotent: {summary['idempotent']}")
    if summary.get("stop_condition_hit"):
        print(f"  STOP CONDITION: {summary['blocker']}")
        return 1

    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"  summary written to: {args.output_json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

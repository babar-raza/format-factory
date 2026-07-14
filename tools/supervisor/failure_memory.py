"""failure_memory.py — Machine-readable persistent failure memory store.

HEAL-RECT-001: Provides read/write/query functions for a durable failure
registry at .local/supervisor/failure-memory.json.

Each failure entry records:
  - category (from failure taxonomy)
  - root_cause classification
  - correction applied
  - files modified
  - verification command
  - sprint where discovered
  - occurrence count (auto-incremented on duplicate)
  - escalation flag (set when count >= escalation_threshold)

Usage:
  from failure_memory import FailureMemory
  fm = FailureMemory(repo_root)
  fm.record_failure(category="EVIDENCE_DECLARATION_FAILURE",
                    root_cause="missing_type_field",
                    correction="added type to evidence_artifacts",
                    sprint_id="MY-SPRINT-001")
  fm.save()
  dups = fm.find_duplicates(threshold=3)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STORE_PATH = ".local/supervisor/failure-memory.json"
ESCALATION_THRESHOLD = 3

VALID_CATEGORIES = frozenset({
    "EVIDENCE_DECLARATION_FAILURE",
    "OVERCLAIM_FAILURE",
    "SUPERVISOR_CONTROL_FAILURE",
    "AUTONOMOUS_CONTINUATION_FAILURE",
    "AUTONOMOUS_HEALING_FAILURE",
    "AUTONOMOUS_LEARNING_FAILURE",
    "REPEATED_FAILURE_PATTERN",
    "PROMPT_ONLY_HEALING_FAILURE",
    "TASK_SELECTION_FAILURE",
    "GRADING_FALSE_POSITIVE",
    "SPEC_AUTHORITY_FAILURE",
    "CAPABILITY_EXTRACTION_FAILURE",
    "PRODUCT_ARCHITECTURE_FAILURE",
    "IMPLEMENTATION_DEPTH_FAILURE",
    "TEST_VALIDATION_FAILURE",
    "CI_PACKAGE_FAILURE",
    "AGENT_LANE_DRIFT",
    "STALE_STATE_FAILURE",
    "QNAME_MAPPING_FAILURE",
    "SCHEMA_VALIDATION_FAILURE",
    "IMPORT_COLLISION",
    "API_SIGNATURE_MISMATCH",
    "GOVERNANCE_FALSE_TRIGGER",
    "OTHER",
})


class FailureMemory:
    """Persistent failure memory store backed by a JSON file."""

    def __init__(self, repo_root: Path | str, store_path: str | None = None):
        self.repo_root = Path(repo_root)
        self.store_file = self.repo_root / (store_path or DEFAULT_STORE_PATH)
        self.entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.store_file.exists():
            try:
                data = json.loads(self.store_file.read_text(encoding="utf-8"))
                self.entries = data.get("failures", [])
            except (json.JSONDecodeError, KeyError):
                self.entries = []
        else:
            self.entries = []

    def save(self) -> Path:
        self.store_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "failure_count": len(self.entries),
            "escalated_count": sum(1 for e in self.entries if e.get("escalated")),
            "failures": self.entries,
        }
        self.store_file.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                   encoding="utf-8")
        return self.store_file

    def record_failure(
        self,
        category: str,
        root_cause: str,
        correction: str = "",
        sprint_id: str = "",
        files_modified: list[str] | None = None,
        verification_command: str = "",
        severity: str = "HIGH",
        gap_id: str = "",
    ) -> dict[str, Any]:
        """Record a failure. If a duplicate (same category + root_cause) exists,
        increment its count instead of creating a new entry."""
        if category not in VALID_CATEGORIES:
            category = "OTHER"

        existing = self._find_existing(category, root_cause)
        if existing is not None:
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            existing["last_seen_sprint"] = sprint_id
            existing["last_seen_at"] = datetime.now(timezone.utc).isoformat()
            if existing["occurrence_count"] >= ESCALATION_THRESHOLD:
                existing["escalated"] = True
            if correction:
                existing["correction"] = correction
            if files_modified:
                merged = list(set(existing.get("files_modified", []) + files_modified))
                existing["files_modified"] = sorted(merged)
            return existing

        entry: dict[str, Any] = {
            "id": f"FM-{len(self.entries) + 1:04d}",
            "category": category,
            "root_cause": root_cause,
            "correction": correction,
            "severity": severity,
            "sprint_discovered": sprint_id,
            "last_seen_sprint": sprint_id,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
            "files_modified": files_modified or [],
            "verification_command": verification_command,
            "occurrence_count": 1,
            "escalated": False,
            "resolved": False,
            "gap_id": gap_id,
        }
        self.entries.append(entry)
        return entry

    def _find_existing(self, category: str, root_cause: str) -> dict[str, Any] | None:
        for entry in self.entries:
            if entry.get("category") == category and entry.get("root_cause") == root_cause:
                return entry
        return None

    def find_duplicates(self, threshold: int = ESCALATION_THRESHOLD) -> list[dict]:
        """Return entries with occurrence_count >= threshold."""
        return [e for e in self.entries if e.get("occurrence_count", 1) >= threshold]

    def find_by_category(self, category: str) -> list[dict]:
        return [e for e in self.entries if e.get("category") == category]

    def find_unresolved(self) -> list[dict]:
        return [e for e in self.entries if not e.get("resolved")]

    def find_escalated(self) -> list[dict]:
        return [e for e in self.entries if e.get("escalated")]

    def mark_resolved(self, failure_id: str, resolution: str = "") -> bool:
        for entry in self.entries:
            if entry.get("id") == failure_id:
                entry["resolved"] = True
                entry["resolution"] = resolution
                entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self.entries),
            "unresolved": len(self.find_unresolved()),
            "escalated": len(self.find_escalated()),
            "by_category": self._count_by_category(),
        }

    def _count_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.entries:
            cat = e.get("category", "OTHER")
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _read_exclusion_window(self) -> int:
        """Read failure_exclusion_window_sprints from .supervisor/policies.yaml.

        Falls back to 3 if the file is missing or the key is absent.
        """
        policies_path = self.repo_root / ".supervisor" / "policies.yaml"
        if not policies_path.exists():
            return 3
        try:
            import yaml  # type: ignore[import]
            policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
            return int(
                policies.get("autonomous_continuation", {})
                .get("failure_exclusion_window_sprints", 3)
            )
        except Exception:
            return 3

    def load_excluded_gap_ids(self, exclusion_window_sprints: int | None = None) -> set[str]:
        """Return gap_ids to exclude from task selection due to repeated failures.

        Excludes gaps where:
        - entry has a gap_id
        - resolved is False (or absent)
        - occurrence_count >= ESCALATION_THRESHOLD

        exclusion_window_sprints controls how long a gap stays suppressed.
        If None (default), reads the value from .supervisor/policies.yaml
        (key: autonomous_continuation.failure_exclusion_window_sprints).
        Falls back to 3 if the policy file is absent or the key is missing.
        Passing an explicit int overrides the policy value (used in tests).
        """
        if exclusion_window_sprints is None:
            exclusion_window_sprints = self._read_exclusion_window()

        excluded: set[str] = set()
        for entry in self.entries:
            gap_id = entry.get("gap_id", "")
            if not gap_id:
                continue
            if entry.get("resolved"):
                continue
            if entry.get("occurrence_count", 1) >= ESCALATION_THRESHOLD:
                excluded.add(gap_id)
        return excluded

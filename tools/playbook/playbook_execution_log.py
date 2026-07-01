"""
playbook_execution_log.py — Playbook Execution Result Logger

FF-PLAYBOOK-SYSTEM-001 (bright-marinating-map), TC-PB-008

Records playbook execution results for learning and healing.
Writes to .local/playbook-executions/<execution_id>.yaml

After each execution: compare expected vs actual phases, capture failure modes,
and record recommendations for playbook improvement.

Only promotes REUSABLE lessons — one-off workarounds are NOT encoded.

Usage:
  from tools.playbook.playbook_execution_log import PlaybookExecutionLog

  log = PlaybookExecutionLog(playbook_id="format-feature-expansion", version="1.1")
  log.phase_complete("read_codec")
  log.phase_failed("draft_function", error="stdlib function not available")
  log.gap_created("GAP-PB-001", reason="missing skill: add-python-api")
  log.save()
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


_REPO_ROOT = Path(__file__).parent.parent.parent
_LOG_DIR = _REPO_ROOT / ".local" / "playbook-executions"


class PlaybookExecutionLog:
    """
    Records the result of a Sprint Task Template execution.
    Captures: successful/failed/skipped phases, new failure modes,
    missing skills (creates gap entries), healing actions, and
    recommended playbook changes (reusable lessons only).
    """

    def __init__(
        self,
        playbook_id: str,
        version: str,
        plan_id: str = "",
        work_item_type: str = "",
    ) -> None:
        self.execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        self.playbook_id = playbook_id
        self.version = version
        self.plan_id = plan_id
        self.work_item_type = work_item_type
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: str | None = None
        self.taskcards: list[str] = []
        self.successful_phases: list[str] = []
        self.failed_phases: list[dict[str, str]] = []
        self.skipped_phases: list[dict[str, str]] = []
        self.new_failure_modes: list[dict[str, str]] = []
        self.unnecessary_phases: list[str] = []
        self.missing_phases: list[str] = []
        self.missing_skills: list[dict[str, str]] = []
        self.gaps_created: list[dict[str, str]] = []
        self.evidence_quality: str = "NOT_RECORDED"
        self.rollback_used: bool = False
        self.healing_actions: list[dict[str, str]] = []
        self.recommended_playbook_changes: list[dict[str, str]] = []
        self.verdict: str = "IN_PROGRESS"

    def phase_complete(self, phase: str) -> None:
        self.successful_phases.append(phase)

    def phase_failed(self, phase: str, error: str = "") -> None:
        self.failed_phases.append({"phase": phase, "error": error})

    def phase_skipped(self, phase: str, reason: str = "") -> None:
        self.skipped_phases.append({"phase": phase, "reason": reason})

    def record_failure_mode(
        self, failure_mode: str, description: str, is_reusable: bool = True
    ) -> None:
        """Record a new failure mode. Only promote REUSABLE lessons."""
        if is_reusable:
            self.new_failure_modes.append({
                "failure_mode": failure_mode,
                "description": description,
                "promote_to_playbook": "YES",
            })

    def missing_skill(self, skill_id: str, phase: str = "") -> None:
        """Record a missing skill. Creates a gap entry record."""
        entry = {"skill_id": skill_id, "phase": phase, "action": "CREATE_SKILL_GAP"}
        self.missing_skills.append(entry)

    def gap_created(self, gap_id: str, reason: str = "") -> None:
        self.gaps_created.append({"gap_id": gap_id, "reason": reason})

    def healing_action(self, action: str, outcome: str = "") -> None:
        self.healing_actions.append({"action": action, "outcome": outcome})

    def recommend_playbook_change(
        self, section: str, change: str, is_reusable: bool = True
    ) -> None:
        """Recommend a playbook change. Only for reusable lessons — not one-off workarounds."""
        if is_reusable:
            self.recommended_playbook_changes.append({
                "section": section,
                "change": change,
                "reusable_lesson": "YES",
            })

    def set_evidence_quality(self, quality: str) -> None:
        """Values: COMPLETE, PARTIAL, MISSING, NOT_RECORDED"""
        self.evidence_quality = quality

    def set_rollback_used(self, used: bool = True) -> None:
        self.rollback_used = used

    def complete(self, verdict: str = "SUCCESS") -> None:
        """
        Mark execution as complete.
        Verdict: SUCCESS, PARTIAL_SUCCESS, FAILED, ROLLED_BACK, BLOCKED
        """
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.verdict = verdict

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "playbook-execution-log/1.0",
            "execution_id": self.execution_id,
            "playbook_id": self.playbook_id,
            "version": self.version,
            "plan_id": self.plan_id,
            "work_item_type": self.work_item_type,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "taskcards": self.taskcards,
            "successful_phases": self.successful_phases,
            "failed_phases": self.failed_phases,
            "skipped_phases": self.skipped_phases,
            "new_failure_modes": self.new_failure_modes,
            "unnecessary_phases": self.unnecessary_phases,
            "missing_phases": self.missing_phases,
            "missing_skills": self.missing_skills,
            "gaps_created": self.gaps_created,
            "evidence_quality": self.evidence_quality,
            "rollback_used": self.rollback_used,
            "healing_actions": self.healing_actions,
            "recommended_playbook_changes": self.recommended_playbook_changes,
            "verdict": self.verdict,
            "authority_note": (
                "This execution log is informational only. "
                "Does NOT approve gates, does NOT mark work complete, "
                "does NOT replace evidence contracts."
            ),
        }

    def save(self, output_dir: Path | None = None) -> Path:
        """Save execution log to .local/playbook-executions/<execution_id>.yaml"""
        if self.completed_at is None:
            self.complete(verdict="SUCCESS" if not self.failed_phases else "PARTIAL_SUCCESS")

        log_dir = output_dir or _LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / f"{self.execution_id}.yaml"
        path.write_text(
            yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return path


def load_execution_log(execution_id: str, log_dir: Path | None = None) -> dict[str, Any]:
    """Load an existing execution log by execution_id."""
    log_dir = log_dir or _LOG_DIR
    path = log_dir / f"{execution_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Execution log not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def list_execution_logs(log_dir: Path | None = None) -> list[dict[str, Any]]:
    """List all execution logs, sorted by started_at descending."""
    log_dir = log_dir or _LOG_DIR
    if not log_dir.exists():
        return []
    logs = []
    for path in sorted(log_dir.glob("EXEC-*.yaml"), reverse=True):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            logs.append({
                "execution_id": data.get("execution_id"),
                "playbook_id": data.get("playbook_id"),
                "verdict": data.get("verdict"),
                "started_at": data.get("started_at"),
                "path": str(path),
            })
        except Exception:
            continue
    return logs

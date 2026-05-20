"""Canonical commit metadata model — distinguish implementation, metadata, and bundle commits.

R33 introduces this to prevent confusion between commit SHAs in final verdicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SprintCommitMetadata:
    """Track the distinct commit types within a sprint."""
    sprint_id: str
    implementation_commit: str = ""
    metadata_commit: str = ""
    bundle_head_commit: str = ""
    notes: list[str] = field(default_factory=list)
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def all_populated(self) -> bool:
        return bool(self.implementation_commit and self.metadata_commit)

    @property
    def commits_match(self) -> bool:
        if not self.implementation_commit or not self.metadata_commit:
            return False
        return self.implementation_commit == self.metadata_commit

    def to_dict(self) -> dict[str, Any]:
        return {
            "sprint_id": self.sprint_id,
            "implementation_commit": self.implementation_commit or "PENDING",
            "metadata_commit": self.metadata_commit or "PENDING",
            "bundle_head_commit": self.bundle_head_commit or "PENDING",
            "all_populated": self.all_populated,
            "commits_match": self.commits_match,
            "notes": self.notes,
            "recorded_at": self.recorded_at,
        }

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []
        if not self.sprint_id:
            errors.append("sprint_id is required")
        if self.implementation_commit == "PENDING":
            errors.append("implementation_commit is PENDING")
        if self.metadata_commit == "PENDING":
            errors.append("metadata_commit is PENDING")
        return errors

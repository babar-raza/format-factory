"""learning_consumer.py — Consumes sprint-learnings.jsonl and proposes durable rules.

HEAL-RECT-002: Reads all sprint-learnings.jsonl files across evidence directories,
aggregates by (category, description_hash), and auto-promotes entries with 3+ occurrences
to durable rule proposals in .local/supervisor/rule-proposals.json.

Rule proposals are non_authoritative (ai_draft) until reviewed.

Usage:
  from learning_consumer import LearningConsumer
  lc = LearningConsumer(repo_root)
  lc.scan_all_learnings()
  proposals = lc.generate_proposals(threshold=3)
  lc.save_proposals()
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PROPOSALS_PATH = ".local/supervisor/rule-proposals.json"
PROMOTION_THRESHOLD = 3


class LearningConsumer:
    """Scans sprint-learnings.jsonl files and generates rule proposals."""

    def __init__(self, repo_root: Path | str):
        self.repo_root = Path(repo_root)
        self.entries: list[dict[str, Any]] = []
        self.aggregated: dict[str, dict[str, Any]] = {}
        self.proposals: list[dict[str, Any]] = []

    def scan_all_learnings(self) -> int:
        """Scan all sprint-learnings.jsonl files under .local/evidences/."""
        evidences_dir = self.repo_root / ".local" / "evidences"
        if not evidences_dir.exists():
            return 0

        count = 0
        for jsonl_file in evidences_dir.rglob("sprint-learnings.jsonl"):
            try:
                for line in jsonl_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    self.entries.append(entry)
                    count += 1
            except (json.JSONDecodeError, OSError):
                continue
        return count

    def aggregate(self) -> dict[str, dict[str, Any]]:
        """Group entries by (category, description_hash) and count occurrences."""
        self.aggregated = {}
        for entry in self.entries:
            category = entry.get("category", "unknown")
            description = entry.get("description", "")
            key = self._make_key(category, description)

            if key not in self.aggregated:
                self.aggregated[key] = {
                    "category": category,
                    "description": description,
                    "recommended_action": entry.get("recommended_action", ""),
                    "impacted_stream": entry.get("impacted_stream", ""),
                    "occurrence_count": 0,
                    "sprint_ids": [],
                }
            agg = self.aggregated[key]
            agg["occurrence_count"] += 1
            sprint_id = entry.get("sprint_id", "")
            if sprint_id and sprint_id not in agg["sprint_ids"]:
                agg["sprint_ids"].append(sprint_id)

        return self.aggregated

    def generate_proposals(self, threshold: int = PROMOTION_THRESHOLD) -> list[dict[str, Any]]:
        """Generate rule proposals for entries exceeding the threshold."""
        if not self.aggregated:
            self.aggregate()

        self.proposals = []
        for key, agg in self.aggregated.items():
            if agg["occurrence_count"] >= threshold:
                self.proposals.append({
                    "proposal_id": f"RP-{key[:12]}",
                    "category": agg["category"],
                    "description": agg["description"],
                    "recommended_action": agg["recommended_action"],
                    "impacted_stream": agg["impacted_stream"],
                    "occurrence_count": agg["occurrence_count"],
                    "sprint_ids": agg["sprint_ids"],
                    "proposed_at": datetime.now(timezone.utc).isoformat(),
                    "authority_state": "ai_draft",
                    "status": "proposed",
                })
        return self.proposals

    def save_proposals(self, path: str | None = None) -> Path:
        """Save proposals to JSON file."""
        out_path = self.repo_root / (path or DEFAULT_PROPOSALS_PATH)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_learnings_scanned": len(self.entries),
            "total_aggregated_patterns": len(self.aggregated),
            "proposals_count": len(self.proposals),
            "promotion_threshold": PROMOTION_THRESHOLD,
            "authority_state": "ai_draft",
            "proposals": self.proposals,
        }
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        return out_path

    def summary(self) -> dict[str, Any]:
        return {
            "total_entries": len(self.entries),
            "unique_patterns": len(self.aggregated),
            "proposals": len(self.proposals),
            "top_recurring": sorted(
                self.aggregated.values(),
                key=lambda x: x["occurrence_count"],
                reverse=True,
            )[:5],
        }

    @staticmethod
    def _make_key(category: str, description: str) -> str:
        normalized = f"{category}:{description.strip().lower()[:100]}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

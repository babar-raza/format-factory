"""Round-trip test for learning consumer: write → scan → propose → read → format.

TC-GAP-A03: Proves rule-proposals.json is both written AND read.
"""

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.learning_consumer import LearningConsumer


class TestLearningConsumerRoundtrip:
    def test_roundtrip_write_read_format(self):
        """Write 3 identical entries → propose → save → read back → format advisory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            evidences = repo / ".local" / "evidences" / "test-sprint"
            evidences.mkdir(parents=True)

            # Write 3 identical learning entries
            entries = []
            for i in range(3):
                entries.append(json.dumps({
                    "category": "EVIDENCE_QUALITY",
                    "description": "Focused-proof files must come first in evidence_paths",
                    "recommended_action": "Reorder evidence_paths with <80-line files first",
                    "impacted_stream": "mainstream",
                    "sprint_id": f"TEST-SPRINT-{i}",
                }))
            (evidences / "sprint-learnings.jsonl").write_text(
                "\n".join(entries), encoding="utf-8"
            )

            # Run full pipeline
            lc = LearningConsumer(repo)
            count = lc.scan_all_learnings()
            assert count == 3

            proposals = lc.generate_proposals(threshold=3)
            assert len(proposals) >= 1

            saved_path = lc.save_proposals()
            assert saved_path.exists()

            # Read back
            promoted = lc.read_promoted_proposals()
            assert len(promoted) >= 1
            assert promoted[0]["category"] == "EVIDENCE_QUALITY"
            assert promoted[0]["occurrence_count"] >= 3

            # Format advisory
            advisory = lc.format_governance_advisories(promoted)
            assert "Learning-Based Governance Advisories" in advisory
            assert "EVIDENCE_QUALITY" in advisory
            assert "Focused-proof" in advisory

    def test_empty_proposals_returns_empty_string(self):
        """No proposals → empty advisory string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lc = LearningConsumer(Path(tmpdir))
            advisory = lc.format_governance_advisories([])
            assert advisory == ""

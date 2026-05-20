"""R34 evidence guards: run-ID scope collision detection.

Ensures sprint report directories contain only artifacts from their own sprint,
and that sprint metadata is internally consistent.
"""

import pathlib
import unittest

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestR33SprintStateConsistency(unittest.TestCase):
    """sprint-state.yaml must match the drift recovery sprint, not AI runner."""

    def setUp(self):
        self.state_path = REPO_ROOT / "reports" / "r33" / "sprint-state.yaml"
        self.assertTrue(self.state_path.exists(), "reports/r33/sprint-state.yaml missing")
        with open(self.state_path) as f:
            self.state = yaml.safe_load(f)

    def test_sprint_id_is_drift_recovery(self):
        self.assertIn("DRIFT-RECOVERY", self.state["sprint_id"])

    def test_sprint_id_not_ai_runner(self):
        self.assertNotIn("AI-RUNNER", self.state["sprint_id"])

    def test_no_ai_lane_names(self):
        for key, lane in self.state.get("lanes", {}).items():
            name = lane.get("name", "")
            self.assertNotIn("synthesis", name.lower(),
                             f"Lane {key} has AI synthesis reference: {name}")
            self.assertNotIn("live_pipeline", name.lower(),
                             f"Lane {key} has AI pipeline reference: {name}")

    def test_verdict_not_pending(self):
        self.assertNotEqual(self.state.get("verdict"), "PENDING")

    def test_scope_contamination_note_exists(self):
        self.assertIn("scope_contamination_note", self.state)


class TestR33FinalVerdictConsistency(unittest.TestCase):
    """final-verdict.md must reference drift recovery, not AI runner."""

    def setUp(self):
        self.verdict_path = REPO_ROOT / "reports" / "r33" / "final-verdict.md"
        self.assertTrue(self.verdict_path.exists())
        self.content = self.verdict_path.read_text(encoding="utf-8")

    def test_sprint_id_is_drift_recovery(self):
        self.assertIn("DRIFT-RECOVERY", self.content)

    def test_verdict_is_drift_recovery_complete(self):
        self.assertIn("R33_DRIFT_RECOVERY_COMPLETE", self.content)

    def test_scope_contamination_note_present(self):
        self.assertIn("Scope Contamination Note", self.content)

    def test_no_push_no_publish(self):
        self.assertIn("NO-PUSH", self.content)


class TestR33EvidenceContractConsistency(unittest.TestCase):
    """Evidence contract must match drift recovery and require clean git."""

    def setUp(self):
        self.contract_path = (
            REPO_ROOT / "tools" / "evidence" / "contracts"
            / "r33-drift-recovery-overclaim-deepening.yaml"
        )
        self.assertTrue(self.contract_path.exists())
        with open(self.contract_path) as f:
            self.contract = yaml.safe_load(f)

    def test_contract_id_is_drift_recovery(self):
        self.assertIn("DRIFT-RECOVERY", self.contract["contract_id"])

    def test_require_clean_git_true(self):
        self.assertTrue(self.contract.get("require_clean_git", False))

    def test_no_ai_artifacts_in_required(self):
        for art in self.contract.get("required_artifacts", []):
            self.assertNotIn("live-telemetry", art,
                             f"AI telemetry in required artifacts: {art}")
            self.assertNotIn("pipeline-fixture-run", art,
                             f"AI pipeline in required artifacts: {art}")
            self.assertNotIn("tools/ai", art,
                             f"AI tool in required artifacts: {art}")


class TestR33ReportDirectoryClean(unittest.TestCase):
    """reports/r33/ must not contain AI runner artifacts after separation."""

    def test_no_live_telemetry_dir(self):
        p = REPO_ROOT / "reports" / "r33" / "live-telemetry"
        self.assertFalse(p.exists(),
                         "reports/r33/live-telemetry/ still exists after separation")

    def test_no_pipeline_fixture_dir(self):
        p = REPO_ROOT / "reports" / "r33" / "pipeline-fixture-run"
        self.assertFalse(p.exists(),
                         "reports/r33/pipeline-fixture-run/ still exists after separation")

    def test_no_ai_runner_verdict(self):
        p = REPO_ROOT / "reports" / "r33" / "final-verdict-ai-runner-pipeline.md"
        self.assertFalse(p.exists(),
                         "AI runner verdict still in reports/r33/")


class TestAIArtifactsSeparated(unittest.TestCase):
    """AI artifacts must exist in their new location."""

    AI_DIR = REPO_ROOT / "reports" / "ai" / "r33-runner-pipeline-truth-20260519"

    def test_ai_dir_exists(self):
        self.assertTrue(self.AI_DIR.exists())

    def test_preflight_moved(self):
        self.assertTrue((self.AI_DIR / "preflight-current-state.md").exists())

    def test_truth_reconciliation_moved(self):
        self.assertTrue((self.AI_DIR / "r32-truth-reconciliation.md").exists())

    def test_lane_ownership_moved(self):
        self.assertTrue((self.AI_DIR / "lane-ownership-and-overlap-matrix.md").exists())

    def test_live_telemetry_moved(self):
        self.assertTrue(
            (self.AI_DIR / "live-telemetry" / "live-pipeline-output.json").exists()
        )

    def test_pipeline_fixture_moved(self):
        self.assertTrue(
            (self.AI_DIR / "pipeline-fixture-run" / "ai-pipeline-runner-output.json").exists()
        )


if __name__ == "__main__":
    unittest.main()

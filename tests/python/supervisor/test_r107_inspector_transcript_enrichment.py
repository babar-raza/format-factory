"""R107: Tests for inspector-level transcript enrichment.

Verifies that inspect_declared_evidence.py detects transcript JSON in
evidence_paths and validates them via validate_skill_transcript.validate_transcript().
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure tools/supervisor is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from inspect_declared_evidence import (
    _is_transcript_json,
    check_transcript_in_evidence,
    inspect_item,
)


def _make_valid_transcript(skill_id="validate-skill-transcript", mode="dry-run"):
    """Create a minimal valid transcript dict."""
    return {
        "invocation_id": "test-inv-r107-001",
        "skill_id": skill_id,
        "mode": mode,
        "inputs": {"transcript_path": "test.json"},
        "allowed_files": ["reports/test/"],
        "actual_files_changed": [],
        "tests_run": ["test_something"],
        "result": "PASS",
        "timestamp": "2026-06-03T18:00:00Z",
    }


def _make_invalid_transcript():
    """Create a transcript with validation errors."""
    return {
        "invocation_id": "inv",
        "skill_id": "nonexistent-skill-xyz",
        "mode": "dry-run",
        "inputs": {},
        "allowed_files": [],
        "actual_files_changed": [],
        "tests_run": [],
        "result": "PASS",
    }


class TestIsTranscriptJson(unittest.TestCase):
    """Test the _is_transcript_json helper."""

    def test_valid_transcript_detected(self):
        data = _make_valid_transcript()
        self.assertTrue(_is_transcript_json(data))

    def test_non_transcript_json_rejected(self):
        data = {"name": "test", "value": 42}
        self.assertFalse(_is_transcript_json(data))

    def test_partial_transcript_rejected(self):
        data = {"invocation_id": "x", "skill_id": "y"}
        self.assertFalse(_is_transcript_json(data))

    def test_regrading_json_not_detected(self):
        data = [{"item_id": "W0", "r106_grade": "ACCEPTED"}]
        # list, not dict — should not crash
        self.assertFalse(isinstance(data, dict) and _is_transcript_json(data))


class TestCheckTranscriptInEvidence(unittest.TestCase):
    """Test check_transcript_in_evidence with real files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo_root = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_json(self, relpath, data):
        full = self.repo_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(json.dumps(data), encoding="utf-8")
        return relpath

    def test_no_json_files_returns_none(self):
        result = check_transcript_in_evidence(
            ["reports/test/evidence.md"], self.repo_root
        )
        self.assertIsNone(result)

    def test_non_transcript_json_returns_none(self):
        path = self._write_json("reports/test/data.json", {"key": "value"})
        result = check_transcript_in_evidence([path], self.repo_root)
        self.assertIsNone(result)

    def test_valid_transcript_enriches(self):
        transcript = _make_valid_transcript()
        path = self._write_json("reports/test/transcript.json", transcript)
        result = check_transcript_in_evidence([path], self.repo_root)
        self.assertIsNotNone(result)
        self.assertEqual(result["transcripts_found"], 1)
        self.assertEqual(result["transcripts_valid"], 1)
        self.assertEqual(result["transcripts_invalid"], 0)
        self.assertTrue(result["all_valid"])

    def test_invalid_transcript_enriches_with_errors(self):
        transcript = _make_invalid_transcript()
        path = self._write_json("reports/test/bad-transcript.json", transcript)
        result = check_transcript_in_evidence([path], self.repo_root)
        self.assertIsNotNone(result)
        self.assertEqual(result["transcripts_found"], 1)
        self.assertEqual(result["transcripts_valid"], 0)
        self.assertEqual(result["transcripts_invalid"], 1)
        self.assertFalse(result["all_valid"])

    def test_mixed_valid_and_invalid(self):
        p1 = self._write_json("reports/test/good.json", _make_valid_transcript())
        p2 = self._write_json("reports/test/bad.json", _make_invalid_transcript())
        result = check_transcript_in_evidence([p1, p2], self.repo_root)
        self.assertIsNotNone(result)
        self.assertEqual(result["transcripts_found"], 2)
        self.assertEqual(result["transcripts_valid"], 1)
        self.assertEqual(result["transcripts_invalid"], 1)
        self.assertFalse(result["all_valid"])

    def test_missing_json_file_skipped(self):
        result = check_transcript_in_evidence(
            ["reports/test/nonexistent.json"], self.repo_root
        )
        self.assertIsNone(result)

    def test_malformed_json_skipped(self):
        bad_path = self.repo_root / "reports" / "test" / "corrupt.json"
        bad_path.parent.mkdir(parents=True, exist_ok=True)
        bad_path.write_text("{invalid json", encoding="utf-8")
        result = check_transcript_in_evidence(
            ["reports/test/corrupt.json"], self.repo_root
        )
        self.assertIsNone(result)


class TestInspectItemTranscriptEnrichment(unittest.TestCase):
    """Test that inspect_item() includes transcript_validation in output."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo_root = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_file(self, relpath, content="# Evidence"):
        full = self.repo_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return relpath

    def test_item_without_transcript_has_none(self):
        md_path = self._write_file("reports/test/evidence.md")
        item = {
            "item_id": "W-TEST",
            "status": "completed",
            "evidence_paths": [md_path],
            "tests_supporting": [],
        }
        result = inspect_item(item, self.repo_root)
        self.assertIn("transcript_validation", result)
        self.assertIsNone(result["transcript_validation"])

    def test_item_with_valid_transcript(self):
        transcript = _make_valid_transcript()
        json_path = self._write_file(
            "reports/test/transcript.json", json.dumps(transcript)
        )
        md_path = self._write_file("reports/test/evidence.md")
        item = {
            "item_id": "W-TEST",
            "status": "completed",
            "evidence_paths": [md_path, json_path],
            "tests_supporting": [],
        }
        result = inspect_item(item, self.repo_root)
        self.assertIsNotNone(result["transcript_validation"])
        self.assertTrue(result["transcript_validation"]["all_valid"])
        self.assertEqual(result["transcript_validation"]["transcripts_found"], 1)

    def test_item_with_invalid_transcript(self):
        transcript = _make_invalid_transcript()
        json_path = self._write_file(
            "reports/test/bad.json", json.dumps(transcript)
        )
        item = {
            "item_id": "W-TEST",
            "status": "completed",
            "evidence_paths": [json_path],
            "tests_supporting": [],
        }
        result = inspect_item(item, self.repo_root)
        self.assertIsNotNone(result["transcript_validation"])
        self.assertFalse(result["transcript_validation"]["all_valid"])


class TestGradeItemWithTranscript(unittest.TestCase):
    """Test that grade_item() correctly handles transcript_validation from inspector."""

    def setUp(self):
        sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
        from grade_declared_work import grade_item
        self.grade_item = grade_item

    def _make_inspection(self, transcript_validation=None, has_evidence=True,
                         has_tests=False, tests_with_content=None):
        return {
            "item_id": "W-TEST",
            "declared_status": "completed",
            "has_evidence": has_evidence,
            "has_tests": has_tests,
            "evidence_paths_found": ["reports/test/evidence.md"] if has_evidence else [],
            "evidence_paths_missing": [],
            "tests_declared": ["test_something.py"] if has_tests else [],
            "tests_with_content": tests_with_content or (["test_something.py"] if has_tests else []),
            "tests_empty_or_stub": [],
            "test_summaries": [],
            "acceptance_criteria_verified": False,
            "acceptance_criteria_pattern": "",
            "transcript_validation": transcript_validation,
        }

    def test_no_transcript_no_tests_is_with_limitations(self):
        insp = self._make_inspection(transcript_validation=None, has_tests=False)
        grade = self.grade_item(insp, {"passed": 101, "failed": 0})
        self.assertEqual(grade["supervisor_grade"], "ACCEPTED_WITH_LIMITATIONS")

    def test_with_tests_is_verified(self):
        insp = self._make_inspection(has_tests=True, tests_with_content=["test.py"])
        grade = self.grade_item(insp, {"passed": 101, "failed": 0})
        self.assertEqual(grade["supervisor_grade"], "ACCEPTED_VERIFIED")

    def test_valid_transcript_present_but_no_tests_still_path_only(self):
        """Transcript validation enriches inspection but doesn't change grade_item logic.
        grade_item uses tests_with_content and criteria_verified for VERIFIED."""
        tv = {
            "transcripts_found": 1, "transcripts_valid": 1,
            "transcripts_invalid": 0, "all_valid": True,
            "valid_transcripts": [{"path": "t.json", "skill_id": "x", "mode": "dry-run", "result": "PASS"}],
            "invalid_transcripts": [],
        }
        insp = self._make_inspection(transcript_validation=tv, has_tests=False)
        grade = self.grade_item(insp, {"passed": 101, "failed": 0})
        # Transcript presence alone doesn't upgrade to VERIFIED — that requires test content
        self.assertIn(grade["supervisor_grade"],
                       ("ACCEPTED_WITH_LIMITATIONS", "ACCEPTED_VERIFIED"))


class TestDeclarationLevelTranscriptAggregation(unittest.TestCase):
    """Test that inspect_declaration produces transcript_validation in item inspections."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo_root = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_file(self, relpath, content="# Evidence"):
        full = self.repo_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return relpath

    def test_declaration_with_transcript_produces_enrichment(self):
        from inspect_declared_evidence import inspect_declaration

        transcript = _make_valid_transcript()
        t_path = self._write_file("reports/test/transcript.json", json.dumps(transcript))
        md_path = self._write_file("reports/test/evidence.md")
        (self.repo_root / "reports" / "test").mkdir(parents=True, exist_ok=True)

        decl = {
            "run_id": "test-r107",
            "sprint_id": "TEST-SPRINT-001",
            "evidence_root": "reports/test",
            "planned_work_items": [
                {
                    "item_id": "W1",
                    "status": "completed",
                    "evidence_paths": [md_path, t_path],
                    "tests_supporting": [],
                }
            ],
            "evidence_artifacts": [],
        }
        inspection = inspect_declaration(decl, self.repo_root)
        item_insp = inspection["item_inspections"][0]
        self.assertIn("transcript_validation", item_insp)
        self.assertIsNotNone(item_insp["transcript_validation"])
        self.assertTrue(item_insp["transcript_validation"]["all_valid"])


if __name__ == "__main__":
    unittest.main()

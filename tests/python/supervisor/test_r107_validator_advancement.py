"""R107: Validator advancement tests.

Tests the integration between transcript validation and the inspector/grader
pipeline, plus edge cases for the new enrichment functions.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_skill_transcript import validate_transcript, validate_directory, REQUIRED_FIELDS, VALID_MODES, VALID_RESULTS
from inspect_declared_evidence import (
    _is_transcript_json,
    check_transcript_in_evidence,
    inspect_item,
    inspect_declaration,
)
from grade_declared_work import grade_item, grade_all


def _make_transcript(**overrides):
    base = {
        "invocation_id": "test-r107-val-001",
        "skill_id": "validate-skill-transcript",
        "mode": "dry-run",
        "inputs": {"transcript_path": "test.json"},
        "allowed_files": ["reports/"],
        "actual_files_changed": [],
        "tests_run": ["test_validate"],
        "result": "PASS",
        "timestamp": "2026-06-03T19:00:00Z",
    }
    base.update(overrides)
    return base


class TestTranscriptValidatorConstants(unittest.TestCase):
    """Verify transcript validator constants are stable."""

    def test_required_fields_count(self):
        self.assertEqual(len(REQUIRED_FIELDS), 8)

    def test_valid_modes(self):
        self.assertEqual(VALID_MODES, {"dry-run", "live", "anti-bypass-demo"})

    def test_valid_results(self):
        self.assertEqual(VALID_RESULTS, {"PASS", "FAIL"})


class TestTranscriptValidatorEdgeCases(unittest.TestCase):
    """Edge cases for validate_transcript."""

    def test_empty_invocation_id_warns(self):
        t = _make_transcript(invocation_id="abc")
        result = validate_transcript(t)
        self.assertTrue(result["valid"])
        # Short ID should produce warning
        self.assertTrue(any("short" in w for w in result["warnings"]))

    def test_anti_bypass_demo_mode_accepted(self):
        t = _make_transcript(mode="anti-bypass-demo")
        result = validate_transcript(t)
        self.assertTrue(result["valid"])

    def test_files_outside_allowed_produces_error(self):
        t = _make_transcript(
            allowed_files=["reports/"],
            actual_files_changed=["src/python/test.py"],
        )
        result = validate_transcript(t)
        self.assertFalse(result["valid"])
        self.assertTrue(any("outside allowed" in e for e in result["errors"]))

    def test_fail_result_accepted(self):
        t = _make_transcript(result="FAIL")
        result = validate_transcript(t)
        self.assertTrue(result["valid"])


class TestValidateDirectoryEdgeCases(unittest.TestCase):
    """Edge cases for validate_directory."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_directory(self):
        result = validate_directory(Path(self.tmpdir))
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["pass"], 0)

    def test_directory_with_valid_transcript(self):
        t = _make_transcript()
        p = Path(self.tmpdir) / "t1.json"
        p.write_text(json.dumps(t), encoding="utf-8")
        result = validate_directory(Path(self.tmpdir))
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pass"], 1)

    def test_directory_with_non_json_files(self):
        (Path(self.tmpdir) / "readme.md").write_text("# Readme")
        result = validate_directory(Path(self.tmpdir))
        self.assertEqual(result["total"], 0)


class TestEnrichmentPipelineEndToEnd(unittest.TestCase):
    """Test the full pipeline: transcript in evidence → inspector → grader."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.repo_root = Path(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, relpath, content):
        full = self.repo_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return relpath

    def test_full_pipeline_with_valid_transcript(self):
        """Transcript found in evidence → inspector enriches → grader grades."""
        md = self._write("reports/test/evidence.md", "# Evidence\nPASS\n19 tests pass")
        t = _make_transcript()
        tj = self._write("reports/test/transcript.json", json.dumps(t))
        (self.repo_root / "reports" / "test").mkdir(parents=True, exist_ok=True)

        decl = {
            "run_id": "pipeline-test",
            "sprint_id": "TEST-PIPELINE-001",
            "evidence_root": "reports/test",
            "test_results": {"passed": 19, "failed": 0},
            "tests_run": 19,
            "planned_work_items": [
                {
                    "item_id": "W1-HANDOFF",
                    "status": "completed",
                    "evidence_paths": [md, tj],
                    "tests_supporting": [],
                    "acceptance_criteria": "1 transcript validates. PASS.",
                }
            ],
            "evidence_artifacts": [{"path": tj, "type": "transcript-json"}],
        }

        inspection = inspect_declaration(decl, self.repo_root)
        review = grade_all(inspection, decl)

        # Inspector should have enriched with transcript
        item_insp = inspection["item_inspections"][0]
        self.assertIsNotNone(item_insp["transcript_validation"])
        self.assertTrue(item_insp["transcript_validation"]["all_valid"])

        # Grader should accept
        self.assertIn(review["item_grades"][0]["supervisor_grade"],
                       ("ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS"))

    def test_full_pipeline_without_transcript(self):
        """No transcript in evidence → inspector has None → grader still works."""
        md = self._write("reports/test/evidence.md", "# Evidence\nDone")
        (self.repo_root / "reports" / "test").mkdir(parents=True, exist_ok=True)

        decl = {
            "run_id": "no-transcript-test",
            "sprint_id": "TEST-NO-TRANSCRIPT-001",
            "evidence_root": "reports/test",
            "test_results": {"passed": 5, "failed": 0},
            "tests_run": 5,
            "planned_work_items": [
                {
                    "item_id": "W1",
                    "status": "completed",
                    "evidence_paths": [md],
                    "tests_supporting": [],
                }
            ],
            "evidence_artifacts": [],
        }

        inspection = inspect_declaration(decl, self.repo_root)
        review = grade_all(inspection, decl)

        item_insp = inspection["item_inspections"][0]
        self.assertIsNone(item_insp["transcript_validation"])
        self.assertEqual(review["item_grades"][0]["supervisor_grade"], "ACCEPTED_WITH_LIMITATIONS")


if __name__ == "__main__":
    unittest.main()

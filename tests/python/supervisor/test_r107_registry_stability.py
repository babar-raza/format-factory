"""R107: Registry stability tests.

Verifies the skill registry is stable at expected counts and that
every active skill has a valid command file, every deferred skill
has a deferred_reason, and no orphan/draft skills exist.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

import yaml


def _load_registry():
    registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    return data.get("skills", [])


def _load_registry_meta():
    registry_path = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
    return yaml.safe_load(registry_path.read_text(encoding="utf-8"))


class TestRegistryStability(unittest.TestCase):
    """Verify registry counts are stable."""

    @classmethod
    def setUpClass(cls):
        cls.skills = _load_registry()
        cls.by_status = {}
        for s in cls.skills:
            status = s.get("status", "unknown")
            cls.by_status.setdefault(status, []).append(s)

    def test_active_count_at_least_23(self):
        active = self.by_status.get("active", [])
        self.assertGreaterEqual(len(active), 23, f"Expected >=23 active, got {len(active)}")

    def test_deferred_count(self):
        deferred = self.by_status.get("deferred", [])
        # R112: record-lane-execution promoted to active (was 2, now 1)
        self.assertIn(len(deferred), (1, 2), f"Expected 1-2 deferred, got {len(deferred)}")

    def test_no_draft_skills(self):
        draft = self.by_status.get("draft", [])
        self.assertEqual(len(draft), 0, f"Expected 0 draft, got {len(draft)}: {[s['skill_id'] for s in draft]}")

    def test_no_orphan_skills(self):
        orphan = self.by_status.get("orphan", [])
        self.assertEqual(len(orphan), 0, f"Expected 0 orphan, got {len(orphan)}")

    def test_total_skill_count(self):
        self.assertEqual(len(self.skills), 32, f"Expected 32 total, got {len(self.skills)}")

    def test_registry_status_is_active_fail_closed(self):
        meta = _load_registry_meta()
        self.assertEqual(meta.get("registry_status"), "active_fail_closed")


class TestActiveSkillsHaveCommandFiles(unittest.TestCase):
    """Verify every active skill has a command file that exists on disk."""

    @classmethod
    def setUpClass(cls):
        cls.skills = _load_registry()

    def test_all_active_skills_have_command_files(self):
        missing = []
        for s in self.skills:
            if s.get("status") != "active":
                continue
            cmd_file = s.get("command_file", "")
            if not cmd_file:
                missing.append(f"{s['skill_id']}: no command_file field")
                continue
            full = REPO_ROOT / cmd_file
            if not full.exists():
                missing.append(f"{s['skill_id']}: {cmd_file} not found")
        self.assertEqual(missing, [], f"Active skills with missing command files: {missing}")

    def test_all_active_skills_have_required_handoff_fields(self):
        missing = []
        for s in self.skills:
            if s.get("status") != "active":
                continue
            fields = s.get("required_handoff_fields", [])
            if not fields:
                missing.append(s["skill_id"])
        self.assertEqual(missing, [], f"Active skills without required_handoff_fields: {missing}")

    def test_all_active_skills_have_mandatory_validations(self):
        missing = []
        for s in self.skills:
            if s.get("status") != "active":
                continue
            vals = s.get("mandatory_validations", [])
            if not vals:
                missing.append(s["skill_id"])
        self.assertEqual(missing, [], f"Active skills without mandatory_validations: {missing}")


class TestDeferredSkillsHaveReason(unittest.TestCase):
    """Verify every deferred skill has a deferred_reason field."""

    @classmethod
    def setUpClass(cls):
        cls.skills = _load_registry()

    def test_deferred_skills_have_reason(self):
        missing = []
        for s in self.skills:
            if s.get("status") != "deferred":
                continue
            reason = s.get("deferred_reason", "")
            if not reason:
                missing.append(s["skill_id"])
        self.assertEqual(missing, [], f"Deferred skills without reason: {missing}")

    def test_deferred_skill_ids(self):
        deferred = [s["skill_id"] for s in self.skills if s.get("status") == "deferred"]
        # R112: record-lane-execution promoted to active; check-mcp-status remains deferred
        self.assertIn("check-mcp-status", deferred)
        self.assertNotIn("record-lane-execution", deferred)


class TestCommandFileValidation(unittest.TestCase):
    """Verify that every active skill's command file passes basic validation."""

    @classmethod
    def setUpClass(cls):
        cls.skills = _load_registry()

    def test_command_files_have_minimum_content(self):
        too_short = []
        for s in self.skills:
            if s.get("status") != "active":
                continue
            cmd_file = s.get("command_file", "")
            if not cmd_file:
                continue
            full = REPO_ROOT / cmd_file
            if not full.exists():
                continue
            text = full.read_text(encoding="utf-8", errors="replace")
            lines = text.strip().split("\n")
            if len(lines) < 10:
                too_short.append(f"{s['skill_id']}: {len(lines)} lines")
        self.assertEqual(too_short, [], f"Command files too short (<10 lines): {too_short}")

    def test_command_files_have_heading_or_frontmatter(self):
        missing = []
        for s in self.skills:
            if s.get("status") != "active":
                continue
            cmd_file = s.get("command_file", "")
            if not cmd_file:
                continue
            full = REPO_ROOT / cmd_file
            if not full.exists():
                continue
            text = full.read_text(encoding="utf-8", errors="replace")
            has_heading = text.startswith("#") or text.startswith("---")
            if not has_heading:
                missing.append(s["skill_id"])
        self.assertEqual(missing, [], f"Command files missing heading or frontmatter: {missing}")


if __name__ == "__main__":
    unittest.main()

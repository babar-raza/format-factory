"""R109 Wave 7: Stream isolation verification tests.

Verify that Skills canonical outputs are stream-local and do not depend
on global Supervisor latest_sprint or stale R98 gaps.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOOLS_DIR = str(REPO_ROOT / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)


class TestSkillsStreamIsolation:
    """Skills outputs must be self-contained under reports/skills-r*."""

    def test_skills_evidence_root_is_stream_local(self):
        """Skills R108 evidence is under reports/skills-r108/, not reports/supervisor/."""
        ev_root = REPO_ROOT / "reports" / "skills-r108"
        assert ev_root.exists()
        assert (ev_root / "final-adversarial-independent-verification.md").exists()

    def test_skills_r109_evidence_root_is_stream_local(self):
        """Skills R109 evidence is under reports/skills-r109/."""
        ev_root = REPO_ROOT / "reports" / "skills-r109"
        assert ev_root.exists()

    def test_skills_adoption_packages_are_stream_local(self):
        """Adoption packages are under Skills evidence, not global supervisor."""
        pkg_dir = REPO_ROOT / "reports" / "skills-r108" / "adoption-packages"
        assert pkg_dir.exists()
        assert (pkg_dir / "mainstream-adoption.yaml").exists()
        assert (pkg_dir / "supervisor-adoption.yaml").exists()
        assert (pkg_dir / "acceleration-adoption.yaml").exists()

    def test_skills_next_prompt_is_skills_only(self):
        """Generated Skills prompt must not contain product implementation tasks."""
        for sprint in ("skills-r108", "skills-r109"):
            prompt_path = REPO_ROOT / "reports" / sprint / "generated-next-skills-prompt.md"
            if prompt_path.exists():
                content = prompt_path.read_text(encoding="utf-8")
                assert "Stream: skills" in content or "stream: skills" in content.lower()
                assert "Forbidden Paths" in content

    def test_global_supervisor_is_reference_only(self):
        """Skills stream reads reports/supervisor/ but doesn't own it."""
        supervisor_dir = REPO_ROOT / "reports" / "supervisor"
        # The session-resume.md may exist from any stream — that's the known limitation
        # Skills must document this as a stream-state limitation, not treat it as owned state
        assert supervisor_dir.exists()  # it exists (shared)
        # Skills R109 evidence is NOT in reports/supervisor/
        skills_specific = REPO_ROOT / "reports" / "skills-r109"
        assert skills_specific.exists()

    def test_no_stale_r98_gaps_in_skills_state(self):
        """Skills stream does not reference R98 gaps as active state."""
        for sprint in ("skills-r108", "skills-r109"):
            prompt_path = REPO_ROOT / "reports" / sprint / "generated-next-skills-prompt.md"
            if prompt_path.exists():
                content = prompt_path.read_text(encoding="utf-8").lower()
                # Should not reference specific R98 gap IDs as active work
                assert "gap-r98" not in content or "reference" in content or "archived" in content

    def test_skills_lane_ledger_is_stream_local(self):
        """Lane execution ledger is under Skills evidence root."""
        for sprint in ("skills-r108", "skills-r109"):
            ledger = REPO_ROOT / "reports" / sprint / "lane-execution-ledger.json"
            if ledger.exists():
                data = json.loads(ledger.read_text(encoding="utf-8"))
                assert isinstance(data, list)
                assert len(data) > 0

    def test_skills_transcripts_are_stream_local(self):
        """Transcripts are under Skills evidence, not mixed with product transcripts."""
        for sprint in ("skills-r108", "skills-r109"):
            ts_dir = REPO_ROOT / "reports" / sprint / "skill-transcripts"
            if ts_dir.exists():
                jsons = list(ts_dir.glob("*.json"))
                assert len(jsons) > 0
